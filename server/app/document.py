import base64
from os import path

from docusign_esign import (
    Recipients,
    EnvelopeDefinition,
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
    SignerAttachment
)
from jinja2 import Environment, BaseLoader

from app.ds_config import TPL_PATH, IMG_PATH


class DsDocument: # pylint: disable=too-many-locals
    @classmethod
    def create_claim(cls, tpl, claim, envelope_args):
        """Creates claim document
        Parameters:
            tpl (str): Template path for the document
            claim (dict): Claim information
            envelope_args (dict): Parameters of the document
        Returns:
            EnvelopeDefinition object that will be submitted to Docusign
        """
        with open(path.join(TPL_PATH, tpl), 'r') as file:
            content_bytes = file.read()

        # Get base64 logo representation to paste it into the HTML file
        with open(path.join(IMG_PATH, 'logo.png'), 'rb') as file:
            img_base64_src = base64.b64encode(file.read()).decode('utf-8')

        content_bytes = Environment(loader=BaseLoader).from_string(
            content_bytes) \
            .render(
            first_name=claim['first_name'],
            last_name=claim['last_name'],
            email=claim['email'],
            street=claim['street'],
            city=claim['city'],
            state=claim['state'],
            zip_code=claim['zip_code'],
            type=claim['type'],
            timestamp=claim['timestamp'],
            description=claim['description'],
            img_base64_src=img_base64_src
        )

        base64_file_content = base64.b64encode(
            bytes(content_bytes, 'utf-8')
        ).decode('ascii')

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
        signer_attachment_tabs = SignerAttachment(
            anchor_string='/attachment/',
            anchor_y_offset='-20',
            anchor_units='pixels',
            anchor_x_offset='20',
            optional='true'
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
            # The Recipients object takes arrays for each recipient type
            recipients=Recipients(signers=[signer]),
            status='sent'  # Requests that the envelope be created and sent
        )

        return envelope_definition

    @classmethod
    def create_with_payment(cls, tpl, user, insurance_info, envelope_args):
        """Create envelope with payment feature included
        Parameters:
            tpl (str): Template path for the document
            user (dict}: User information
            insurance_info (dict): Insurance information for enrollment
            envelope_args (dict): Parameters for the envelope
        Returns:
            EnvelopeDefinition object that will be submitted to Docusign
        """
        currency_multiplier = 100
        discount_percent = 5
        insurance_rate_percent = 10

        # Read template and fill it up
        with open(path.join(TPL_PATH, tpl), 'r') as file:
            content_bytes = file.read()

        # Get base64 logo representation to paste it into the HTML file
        with open(path.join(IMG_PATH, 'logo.png'), 'rb') as file:
            img_base64_src = base64.b64encode(file.read()).decode('utf-8')
        content_bytes = Environment(loader=BaseLoader).from_string(
            content_bytes).render(
                user_name=f"{user['first_name']} {user['last_name']}",
                user_email=user['email'],
                address=f"{user['street']}, {user['city']}, {user['state']}",
                zip_code=user['zip_code'],
                detail_1=insurance_info['detail1']['name'],
                detail_2=insurance_info['detail2']['name'],
                value_detail_1=insurance_info['detail1']['value'],
                value_detail_2=insurance_info['detail2']['value'],
                img_base64_src=img_base64_src
            )

        base64_file_content = base64.b64encode(
            bytes(content_bytes, 'utf-8')
        ).decode('ascii')

        # Create the envelope definition
        envelope_definition = EnvelopeDefinition(
            email_subject='Buy New Insurance'
        )

        # Create the document
        doc1 = Document(document_base64=base64_file_content,
                        name='Insurance order form',  # Can be different from actual file name
                        file_extension='html',  # Source data format
                        document_id='1'  # A label used to reference the doc
                        )
        envelope_definition.documents = [doc1]

        # Create a signer recipient to sign the document
        signer1 = Signer(
            email=user['email'],
            name=f"{user['first_name']} {user['last_name']}",
            recipient_id='1',
            routing_order='1',
            client_user_id=envelope_args['signer_client_id']
        )
        sign_here1 = SignHere(
            anchor_string='/sn1/',
            anchor_y_offset='10',
            anchor_units='pixels',
            anchor_x_offset='20',
        )

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

        # Create a formula tab for the insurance price
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

        # Create payment line item
        payment_line_iteml1 = PaymentLineItem(
            name='Insurance payment',
            description='$[l4t]',
            amount_reference='l4t'
        )

        payment_details = PaymentDetails(
            gateway_account_id=envelope_args['gateway_account_id'],
            currency_code='USD',
            gateway_name=envelope_args['gateway_name'],
            line_items=[payment_line_iteml1]
        )

        # Create a hidden formula tab for the payment itself
        formula_payment = FormulaTab(
            tab_label='payment',
            formula=f'([l4t]) * {currency_multiplier}',
            round_decimal_places='2',
            payment_details=payment_details,
            hidden='true',
            required='true',
            locked='true',
            document_id='1',
            page_number='1',
            x_position='0',
            y_position='0'
        )

        # Create tabs for the signer
        signer1_tabs = Tabs(
            sign_here_tabs=[sign_here1],
            number_tabs=[coverage, deductible],
            formula_tabs=[
                formula_payment, formula_total, discount, trigger
            ],
            checkbox_tabs=[checkbox]
        )
        signer1.tabs = signer1_tabs

        # Add the recipients to the envelope object
        recipients = Recipients(signers=[signer1])
        envelope_definition.recipients = recipients

        # Request that the envelope be sent by setting status to 'sent'
        envelope_definition.status = 'sent'

        return envelope_definition
