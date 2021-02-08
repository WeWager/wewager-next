from rest_framework.exceptions import APIException


class BalanceTooLow(APIException):
    status_code = 400
    default_detail = "Your balance is too low for this operation."
    default_code = "balance_too_low"
