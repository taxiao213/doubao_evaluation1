class InvanaError(Exception):
    """项目基础异常。"""


class ValidationError(InvanaError):
    pass


class RepoError(InvanaError):
    pass


class PricingError(InvanaError):
    pass
