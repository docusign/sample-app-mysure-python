import base64
from os import path
import re

from docusign_esign import (
    Recipients,
    ConnectEventData,
    EnvelopeDefinition,
    EventNotification,
    Tabs,
    Email,
    SignHere,
    Signer,
    Checkbox,
    FormulaTab,
    Number,
    PaymentDetails,
    PaymentLineItem,
    Document,
    SignerAttachment,
    Text,
)
from jinja2 import Environment, BaseLoader

from app.ds_config import TPL_PATH, IMG_PATH
from app.extensions import Extensions


class DsDocument: # pylint: disable=too-many-locals
    CURRENCY_MULTIPLIER = 100
    DISCOUNT_PERCENT = 5
    INSURANCE_RATE_PERCENT = 10

    @classmethod
    def _render_claim_template(cls, tpl, claim, remove_white_styles=False):
        """Reads and renders the HTML claim template with claim data"""
        with open(path.join(TPL_PATH, tpl), 'r') as file:
            content_bytes = file.read()

        # Get base64 logo representation to paste it into the HTML file
        with open(path.join(IMG_PATH, 'logo.png'), 'rb') as file:
            img_base64_src = base64.b64encode(file.read()).decode('utf-8')

        if remove_white_styles:
            # Fields that should be replaced
            fields_to_replace = ['zip_code', 'street', 'city', 'state', 'country']
            for field in fields_to_replace:
                pattern = rf'<span[^>]*style="color:\s*white"[^>]*>\s*/{field}/\s*</span>'
                replacement = f'<span class="user-info">{{{{ {field} }}}}</span>'
                content_bytes = re.sub(pattern, replacement, content_bytes, flags=re.IGNORECASE)

        # Render template with claim data
        return Environment(loader=BaseLoader).from_string(content_bytes).render(
            first_name=claim['first_name'],
            last_name=claim['last_name'],
            email=claim['email'],
            street=claim['street'],
            city=claim['city'],
            state=claim['state'],
            country=claim['country'],
            zip_code=claim['zip_code'],
            type=claim['type'],
            timestamp=claim['timestamp'],
            description=claim['description'],
            img_base64_src=img_base64_src
        )


    @classmethod
    def _create_base_envelope_objects(cls, claim, envelope_args, rendered_html):
        """Creates base DocuSign objects (document, signer, and base tabs)"""
        base64_file_content = base64.b64encode(rendered_html.encode('utf-8')).decode('ascii')

        # Create the document model
        document = Document(  # Create the Docusign document object
            document_base64=base64_file_content,
            name='Submit a Claim',
            file_extension='html',
            document_id=1
        )

        # Create the signer recipient model
        signer = Signer(  # The signer
            email=claim['email'],
            name=f"{claim['first_name']} {claim['last_name']}",
            recipient_id='1',
            routing_order='1',
            # Setting the client_user_id marks the signer as embedded
            client_user_id=envelope_args['signer_client_id']
        )

        # Create a sign_here tab (field on the document)
        sign_here = SignHere(
            anchor_string='/signature_1/',
            anchor_units='pixels',
            anchor_y_offset='10',
            anchor_x_offset='20'
        )

        # Create a signer_attachment tab
        signer_attachment_tabs = SignerAttachment(
            anchor_string='/attachment/',
            anchor_y_offset='-20',
            anchor_units='pixels',
            anchor_x_offset='20',
            optional='true'
        )

        return document, signer, sign_here, signer_attachment_tabs


    @classmethod
    def create_claim(cls, tpl, claim, envelope_args, extensions, auth_type):
        """Creates claim document
        Parameters:
            tpl (str): Template path for the document
            claim (dict): Claim information
            envelope_args (dict): Parameters of the document
            extensions (list): List of extension objects
        Returns:
            EnvelopeDefinition object that will be submitted to Docusign
        """
        # Render and prepare HTML
        content_bytes = cls._render_claim_template(tpl, claim)

        # Base DocuSign setup
        document, signer, sign_here, signer_attachment_tabs = cls._create_base_envelope_objects(
            claim, envelope_args, content_bytes
        )

        # Extensions handling
        extension_for_email = next(
            (ext for ext in extensions if ext["appId"].strip() in Extensions.getEmailExtensionIds()),
            None
        )
        extension_for_address = Extensions.get_object_by_app_id(extensions, Extensions.getAddressExtensionId())

        # Create an email field
        for tab in (t for t in extension_for_email["tabs"] if "VerifyEmailInput" in t["tabLabel"]):
            verification_data = Extensions.extract_verification_data(extension_for_email["appId"], tab)
            extension_data = Extensions.get_extension_data(verification_data)
            email = Email(
                name=verification_data["application_name"],
                tab_label=verification_data["tab_label"],
                tooltip=verification_data["action_input_key"],
                document_id='1',
                page_number='1',
                anchor_string='/email/',
                anchor_units='pixels',
                required=True,
                value=claim['email'],
                locked=False,
                anchor_y_offset='-5',
                extension_data=extension_data
            )

        # Address fields mapping
        address_fields = {
            "street": "VerifyPostalAddressInput[0].street1",
            "city": "VerifyPostalAddressInput[0].locality",
            "state": "VerifyPostalAddressInput[0].subdivision",
            "country": "VerifyPostalAddressInput[0].countryOrRegion",
            "zip_code": "VerifyPostalAddressInput[0].postalCode",
        }

        text_tabs = []
        for field, label_pattern in address_fields.items():
            for tab in (t for t in extension_for_address["tabs"] if label_pattern in t["tabLabel"]):
                verification_data = Extensions.extract_verification_data(extension_for_address["appId"], tab)
                extension_data = Extensions.get_extension_data(verification_data)
                text_tabs.append(
                    Text(
                        name=verification_data["application_name"],
                        tab_label=verification_data["tab_label"],
                        tooltip=verification_data["action_input_key"],
                        document_id="1",
                        page_number="1",
                        anchor_string=f"/{field}/",
                        anchor_units="pixels",
                        required=True,
                        value=claim[field],
                        locked=False,
                        anchor_y_offset="-5",
                        anchor_x_offset="-5",
                        width="50",
                        extension_data=extension_data,
                    )
                )

        # Assign all tabs
        signer.tabs = Tabs(
            sign_here_tabs=[sign_here],
            email_tabs=[email],
            text_tabs=text_tabs,
            signer_attachment_tabs=[signer_attachment_tabs],
        )

        # Create the top-level envelope definition and populate it
        envelope_definition = EnvelopeDefinition(
            email_subject='Submit a Claim',
            documents=[document],
            recipients=Recipients(signers=[signer]),
            status='sent',
            event_notification=cls._create_event_notification(envelope_args, auth_type)
        )

        return envelope_definition


    @classmethod
    def create_claim_without_extension(cls, tpl, claim, envelope_args, auth_type):
        """Creates claim document
        Parameters:
            tpl (str): Template path for the document
            claim (dict): Claim information
            envelope_args (dict): Parameters of the document
        Returns:
            EnvelopeDefinition object that will be submitted to Docusign
        """
        # Render and prepare HTML (with style cleanup)
        content_bytes = cls._render_claim_template(tpl, claim, remove_white_styles=True)

        # Base DocuSign setup
        document, signer, sign_here, signer_attachment_tabs = cls._create_base_envelope_objects(
            claim, envelope_args, content_bytes
        )

        # Create an email field
        email = Email(
            document_id='1',
            page_number='1',
            anchor_string='/email/',
            anchor_units='pixels',
            required=True,
            value=claim['email'],
            locked=False,
            anchor_y_offset='-5'
        )

        signer.tabs = Tabs(
            sign_here_tabs=[sign_here],
            email_tabs=[email],
            signer_attachment_tabs=[signer_attachment_tabs],
        )

        # Create the top-level envelope definition and populate it
        envelope_definition = EnvelopeDefinition(
            email_subject='Submit a Claim',
            documents=[document],
            recipients=Recipients(signers=[signer]),
            status='sent',
            event_notification=cls._create_event_notification(envelope_args, auth_type)
        )

        return envelope_definition

    @staticmethod
    def _read_and_render_template(tpl, render_context, fields_to_replace=None):
        """Reads and renders the HTML template"""
        with open(path.join(TPL_PATH, tpl), 'r') as file:
            content_bytes = file.read()

        # Get base64 logo representation to paste it into the HTML file
        with open(path.join(IMG_PATH, 'logo.png'), 'rb') as file:
            img_base64_src = base64.b64encode(file.read()).decode('utf-8')

        # Optional cleanup of unwanted inline styles
        if fields_to_replace:
            for field in fields_to_replace:
                pattern = rf'<span[^>]*style="color:\s*white"[^>]*>\s*/{field}/\s*</span>'
                replacement = f'<span class="user-info">{{{{ {field} }}}}</span>'
                content_bytes = re.sub(pattern, replacement, content_bytes, flags=re.IGNORECASE)

        render_context["img_base64_src"] = img_base64_src

        return Environment(loader=BaseLoader).from_string(content_bytes).render(**render_context)

    @staticmethod
    def _create_payment_tabs(currency_multiplier, discount_percent, insurance_rate_percent, envelope_args):
        """Creates all payment-related tabs (number, formula, checkbox)"""
        # Create number tabs for the coverage amount and deductible
        coverage = Number(
            font='helvetica',
            font_size='size11',
            anchor_string='/l1e/',
            anchor_y_offset='-7',
            anchor_units='pixels',
            tab_label='l1e',
            required='true',
        )

        deductible = Number(
            font='helvetica',
            font_size='size11',
            anchor_string='/l2e/',
            anchor_y_offset='-7',
            anchor_units='pixels',
            tab_label='l2e',
            required='true',
        )

        # Create checkbox and trigger tabs to apply the discount
        checkbox = Checkbox(
            font='helvetica',
            font_size='size11',
            anchor_string='/cb/',
            anchor_y_offset='-4',
            anchor_units='pixels',
            anchor_x_offset='-8',
            tab_label='checkbox',
            height='50',
            bold='true',
        )

        trigger = FormulaTab(
            anchor_string='/trigger/',
            font_color='white',
            anchor_y_offset='10',
            tab_label='trigger',
            conditional_parent_label='checkbox',
            conditional_parent_value='on',
            formula='1',
            required='true',
            locked='true',
        )

        discount = FormulaTab(
            font='helvetica',
            font_size='size11',
            bold='true',
            anchor_string='/dt/',
            anchor_y_offset='-4',
            anchor_units='pixels',
            anchor_x_offset='0',
            tab_label='discount',
            formula=f"if([trigger] > 0, {discount_percent}, 0)",
            round_decimal_places='0',
            locked='true',
        )

        # Formula tab for total price
        total = f'([l1e]-[l2e]) * {insurance_rate_percent}/100'

        formula_total = FormulaTab(
            font='helvetica',
            bold='true',
            font_size='size12',
            anchor_string='/l4t/',
            anchor_y_offset='-6',
            anchor_units='pixels',
            anchor_x_offset='84',
            tab_label='l4t',
            formula=f'({total}) - (({total}) * [discount]/100)',
            round_decimal_places='2',
            required='true',
            locked='true',
        )

        # Payment line item and hidden formula
        payment_line_item = PaymentLineItem(name='Insurance payment', description='$[l4t]', amount_reference='l4t')
        payment_details = PaymentDetails(
            gateway_account_id=envelope_args['gateway_account_id'],
            currency_code='USD',
            gateway_name=envelope_args['gateway_name'],
            line_items=[payment_line_item]
        )
        formula_payment = FormulaTab(
            tab_label='payment', formula=f'([l4t]) * {currency_multiplier}',
            round_decimal_places='2', payment_details=payment_details,
            hidden='true', required='true', locked='true',
            document_id='1', page_number='1', x_position='0', y_position='0'
        )


        return coverage, deductible, checkbox, trigger, discount, formula_total, formula_payment

    @staticmethod
    def _create_common_envelope_parts(user, envelope_args, base64_file_content):
        """Creates document, signer, and base envelope with shared logic"""
        # Create the envelope definition
        envelope_definition = EnvelopeDefinition(email_subject='Buy New Insurance')

        # Create the document
        doc = Document(
            document_base64=base64_file_content,
            name='Insurance order form',
            file_extension='html',
            document_id='1'
        )
        envelope_definition.documents = [doc]

        # Create the signer recipient
        signer = Signer(
            email=user['email'],
            name=f"{user['first_name']} {user['last_name']}",
            recipient_id='1',
            routing_order='1',
            client_user_id=envelope_args['signer_client_id']
        )

        sign_here = SignHere(
            anchor_string='/sn1/',
            anchor_y_offset='10',
            anchor_units='pixels',
            anchor_x_offset='20',
        )

        return envelope_definition, signer, sign_here

    @classmethod
    def create_with_payment(cls, tpl, user, insurance_info, envelope_args, extensions):
        """Create envelope with payment feature included"""
        render_context = dict(
            user_name=f"{user['first_name']} {user['last_name']}",
            user_email=user['email'],
            street=user['street'],
            city=user['city'],
            state=user['state'],
            country=user['country'],
            zip_code=user['zip_code'],
            detail_1=insurance_info['detail1']['name'],
            detail_2=insurance_info['detail2']['name'],
            value_detail_1=insurance_info['detail1']['value'],
            value_detail_2=insurance_info['detail2']['value']
        )

        content_bytes = cls._read_and_render_template(tpl, render_context)
        base64_file_content = base64.b64encode(content_bytes.encode('utf-8')).decode('ascii')

        envelope_definition, signer, sign_here = cls._create_common_envelope_parts(user, envelope_args, base64_file_content)
        coverage, deductible, checkbox, trigger, discount, formula_total, formula_payment = cls._create_payment_tabs(cls.CURRENCY_MULTIPLIER, cls.DISCOUNT_PERCENT, cls.INSURANCE_RATE_PERCENT, envelope_args)

        # Extensions logic
        extension_for_email = next(
            (ext for ext in extensions if ext["appId"].strip() in Extensions.getEmailExtensionIds()), None
        )
        extension_for_address = Extensions.get_object_by_app_id(extensions, Extensions.getAddressExtensionId())

        # Email tab
        for tab in (t for t in extension_for_email["tabs"] if "VerifyEmailInput" in t["tabLabel"]):
            verification_data = Extensions.extract_verification_data(extension_for_email["appId"], tab)
            extension_data = Extensions.get_extension_data(verification_data)
            email = Email(
                name=verification_data["application_name"],
                tab_label=verification_data["tab_label"],
                tooltip=verification_data["action_input_key"],
                document_id='1',
                page_number='1',
                anchor_string='/user_email/',
                anchor_units='pixels',
                required=True,
                value=user['email'],
                locked=False,
                anchor_y_offset='-5',
                extension_data=extension_data
            )

        # Address text tabs
        address_fields = {
            "street": "VerifyPostalAddressInput[0].street1",
            "city": "VerifyPostalAddressInput[0].locality",
            "state": "VerifyPostalAddressInput[0].subdivision",
            "country": "VerifyPostalAddressInput[0].countryOrRegion",
            "zip_code": "VerifyPostalAddressInput[0].postalCode",
        }
        text_tabs = []
        for field, label_pattern in address_fields.items():
            for tab in (t for t in extension_for_address["tabs"] if label_pattern in t["tabLabel"]):
                verification_data = Extensions.extract_verification_data(extension_for_address["appId"], tab)
                extension_data = Extensions.get_extension_data(verification_data)
                text_tabs.append(
                    Text(
                        name=verification_data["application_name"],
                        tab_label=verification_data["tab_label"],
                        tooltip=verification_data["action_input_key"],
                        document_id="1",
                        page_number="1",
                        anchor_string=f"/{field}/",
                        anchor_units="pixels",
                        required=True,
                        value=user[field],
                        locked=False,
                        anchor_y_offset="-5",
                        anchor_x_offset="-5",
                        width="50",
                        extension_data=extension_data,
                    )
                )

        signer.tabs = Tabs(
            sign_here_tabs=[sign_here],
            number_tabs=[coverage, deductible],
            formula_tabs=[formula_payment, formula_total, discount, trigger],
            email_tabs=[email],
            text_tabs=text_tabs,
            checkbox_tabs=[checkbox]
        )

        envelope_definition.recipients = Recipients(signers=[signer])
        envelope_definition.status = 'sent'
        return envelope_definition

    @classmethod
    def create_with_payment_without_extension(cls, tpl, user, insurance_info, envelope_args):
        """Create envelope with payment feature included (no extensions)"""
        render_context = dict(
            user_name=f"{user['first_name']} {user['last_name']}",
            user_email=user['email'],
            street=user['street'],
            city=user['city'],
            state=user['state'],
            country=user['country'],
            zip_code=user['zip_code'],
            detail_1=insurance_info['detail1']['name'],
            detail_2=insurance_info['detail2']['name'],
            value_detail_1=insurance_info['detail1']['value'],
            value_detail_2=insurance_info['detail2']['value']
        )

        fields_to_replace = ['street', 'city', 'country', 'state', 'zip_code', 'user_email']
        content_bytes = cls._read_and_render_template(tpl, render_context, fields_to_replace)
        base64_file_content = base64.b64encode(content_bytes.encode('utf-8')).decode('ascii')

        envelope_definition, signer, sign_here = cls._create_common_envelope_parts(user, envelope_args, base64_file_content)
        coverage, deductible, checkbox, trigger, discount, formula_total, formula_payment = cls._create_payment_tabs(cls.CURRENCY_MULTIPLIER, cls.DISCOUNT_PERCENT, cls.INSURANCE_RATE_PERCENT, envelope_args)

        signer.tabs = Tabs(
            sign_here_tabs=[sign_here],
            number_tabs=[coverage, deductible],
            formula_tabs=[formula_payment, formula_total, discount, trigger],
            checkbox_tabs=[checkbox]
        )

        envelope_definition.recipients = Recipients(signers=[signer])
        envelope_definition.status = 'sent'
        return envelope_definition

    @classmethod
    def _create_event_notification(cls, envelope_args, auth_type):
        """Creates event notification object for the envelope"""
        monitor_url = f"{envelope_args['monitor_callback_url']}/api/monitor/envelopes/status"

        event_data = ConnectEventData(
            version='restv2.1',
            include_data=["recipients"]
        )
        event_notification = EventNotification(
            url=monitor_url,
            delivery_mode='SIM',
            logging_enabled='true',
            require_acknowledgment='true',
            events=[
                'envelope-sent',
                'envelope-delivered',
                'envelope-completed',
                'envelope-declined',
                'envelope-voided',
            ],
            event_data=event_data
        )

        if auth_type == 'jwt':
            event_notification.events.append('extension-executed')  # Add envelope-sent event for JWT auth

        return event_notification
