class Event:
    def __init__(self):
        self.handlers = set()

    def subscribe(self, handler):
        self.handlers.add(handler)

    def invoke(self, data):
        for handler in self.handlers:
            handler(data)

    def unsubscribe(self, handler):
        if handler in self.handlers:
            self.handlers.remove(handler)
