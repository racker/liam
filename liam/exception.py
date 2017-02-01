class LiamException(Exception):
    """Generic liam exception"""


class InvalidArn(LiamException):
    """Supplied arn was not formatted properly"""
