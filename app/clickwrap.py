from app.ds_config import CLICKWRAP_ID

class Clickwrap: # pylint: disable=too-few-public-methods
    @staticmethod
    def get(args, session):
        """Gets a clickwrap and account data
        Returns:
            JSON structure of the clickwrap.
        """
        account_id = session.get('account_id')

        clickwrap = {
            'accountId': account_id,
            'clickwrapId': CLICKWRAP_ID
        }

        return clickwrap
