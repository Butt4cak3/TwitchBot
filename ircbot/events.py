class Event:
    handlers = set()

    def __init__(self):
        pass

    def subscribe(self, handler):
        self.handlers.add(handler)

    def invoke(self, data):
        for handler in self.handlers:
            handler(data)

    def unsubscribe(self, handler):
        if handler in self.handlers:
            self.handlers.remove(handler)
