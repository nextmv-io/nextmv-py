"""
Provides role enum for Nextmv accounts.

This module defines enumerations for representing member roles within
a Nextmv account.

Classes
-------
AccountMemberRole
    Represents the role of a member in a Nextmv account.
"""

from enum import Enum

class AccountMemberRole(str, Enum):
    """
    The role type of an `AccountMember` represented as a string.

    You can import the `AccountMemberRole` class directly from `nextmv`:

    ```python
    from nextmv import AccountMemberRole
    ```

    This enum specifies the supported roles for users in Nextmv accounts.

    Attributes
    ----------
    ROOT : str
        The role of the owner of the account
    ADMIN : str
        The role of administrators of the account
    DEVELOPER: str
        The role of developers of the account
    OPERATOR: str
        The role of operators of the account
    VIEWER: str
        The role of viewers of the account
    """

    ROOT = "root"
    """The role of the owner of the account"""
    ADMIN = "admin"
    """The role of administrators of the account"""
    DEVELOPER = "developer"
    """The role of developers of the account"""
    OPERATOR = "operator"
    """The role of operators of the account"""
    VIEWER = "viewer"
    """The role of viewers of the account"""
