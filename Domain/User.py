from .Guest import Guest


class User(Guest):
    creditDetails = {}

    def __init__(self, username, password):
        super(User, self).__init__()
        self.username = username
        self.password = password
