from enum import IntEnum


class Permission(IntEnum):
    """
    Represent the multiple levels of permissions for specific actions, like
    running commands.
    """

    Everyone = 1
    """Simply everyone"""
    Subscriber = 2
    """Users who have subscribed to the current channel"""
    Moderator = 3
    """Users who were elected as moderators of the current channel"""
    Broadcaster = 4
    """The owner of the current channel"""
    OP = 5
    """Administrators as defined in the configuration file of this bot"""

    @staticmethod
    def from_string(name):
        """Turn a permission name into a permission."""
        for member in Permission:
            if member.name.lower() == name.lower():
                return member

    @staticmethod
    def to_string(permission):
        """Turn a permission into an all-lowercase string."""
        return permission.name.lower()

    @staticmethod
    def from_strings(permissions):
        """Turn a list of strings into a list of permissions."""
        result = []
        for name in permissions:
            for member in Permission:
                if name.lower() == member.name.lower():
                    result.append(member)

        return result

    @staticmethod
    def to_strings(permissions):
        """Turn a list of permissions into a list of all-lowercase strings."""
        result = []

        for permission in Permission:
            if permission in permissions:
                result.append(permission.name.lower())

        return result
