from enum import IntEnum


class Permission(IntEnum):
    Everyone = 1
    Subscriber = 2
    Moderator = 3
    Broadcaster = 4
    OP = 5

    @staticmethod
    def from_string(name):
        for member in Permission:
            if member.name.lower() == name.lower():
                return member

    @staticmethod
    def to_string(permission):
        return permission.name.lower()

    @staticmethod
    def from_strings(permissions):
        result = []
        for name in permissions:
            for member in Permission:
                if name.lower() == member.name.lower():
                    result.append(member)

        return result

    @staticmethod
    def to_strings(permissions):
        result = []

        for permission in Permission:
            if permission in permissions:
                result.append(permission.name.lower())

        return result
