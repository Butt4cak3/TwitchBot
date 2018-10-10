from . import Permission


class User:
    _id = ""
    _name = ""
    _displayname = ""
    _color = ""
    _mod = False
    _turbo = False
    _type = ""
    _badges = ""
    _subscriber = False
    _op = False
    _bot = False
    _permissions = [Permission.Everyone]

    def __init__(self, tags, is_op, is_bot):
        self._id = tags["user-id"]
        self._name = tags["nick"]
        self._displayname = tags["display-name"]
        self._color = tags["color"]
        if tags["mod"] == "1":
            self._mod = True
        if tags["turbo"] == "1":
            self._turbo = True
        self._type = tags["user-type"]
        self._badges = tags["badges"]
        if tags["subscriber"] == "1":
            self._subscriber = True
        self._op = is_op
        self._bot = is_bot

        if self.is_subscriber():
            self._permissions.append(Permission.Subscriber)
        if self.is_mod():
            self._permissions.append(Permission.Moderator)
        if self.is_broadcaster():
            self._permissions.append(Permission.Broadcaster)
        if self.is_op():
            self._permissions.append(Permission.OP)

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_displayname(self):
        return self._displayname

    def get_color(self):
        return self._color

    def get_badges(self):
        return self._badges

    def is_mod(self):
        return self._mod

    def is_subscriber(self):
        return self._subscriber

    def is_subscribed(self):
        return self._subscriber

    def is_op(self):
        return self._op

    def is_bot(self):
        return self._bot

    def is_broadcaster(self):
        return "broadcaster" in self.get_badges()

    def has_permission(self, permissions):
        for required in permissions:
            for actual in self._permissions:
                if actual >= required:
                    return True
        else:
            return False
