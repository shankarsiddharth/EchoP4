class AppExit(Exception):

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        if self.message is None:
            return "Application Exit by User."
        else:
            return self.message
