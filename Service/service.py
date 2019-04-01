from abc import abstractmethod


# Interface


class ServiceInterface(object):

    @abstractmethod  # 1.1 ?????
    def init(self, sm_username, sm_password): pass

    @abstractmethod  # 2.2
    def sign_up(self, username, password): pass

    @abstractmethod  # 2.3
    def login(self, username, password): pass

    @abstractmethod  # 2.4
    def search(self, param): pass

    @abstractmethod  # 2.8
    def buy_items(self, items): pass

    @abstractmethod  # 3.1
    def logout(self): pass

    @abstractmethod  # 3.2
    def create_store(self, name): pass

    @abstractmethod  # 6.2
    def remove_client(self, client): pass

    @abstractmethod  # 2.7
    def get_cart(self, store): pass

    @abstractmethod  # 2.6
    def add_to_cart(self, store, item): pass

    @abstractmethod  # 2.7
    def remove_from_cart(self, cart, item): pass

    @abstractmethod  # 2.8
    def buy_item(self, item): pass

    @abstractmethod  # 4.1.1
    def add_item_to_inventory(self, item, store, quantity): pass

    @abstractmethod  # 4.1.2
    def remove_item_from_inventory(self, item, store, quantity): pass

    @abstractmethod  # 4.1.3
    def edit_item_price(self, item, new_price): pass

    @abstractmethod  # 4.3
    def add_new_owner(self, new_owner): pass

    @abstractmethod  # 4.4
    def remove_owner(self, owner_to_remove): pass

    @abstractmethod  # 4.5
    def add_new_manager(self, new_manager): pass

    @abstractmethod  # 4.6
    def remove_manager(self, manager_to_remove): pass

    @abstractmethod  # 4.1.3
    def set_price(self, new_price): pass

