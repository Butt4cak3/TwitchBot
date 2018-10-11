class Event:
    handlers = []

    def __init__(self):
        pass

    def subscribe(self, handler):
        self.handlers.append(handler)

    def invoke(self, data):
        for handler in self.handlers:
            handler(data)
