from Service.service import ServiceInterface
from Domain.System import System


class ServiceImpl(ServiceInterface):

    def __init__(self):
        self.sys = System()

    # assumes the init function receives the username and password of the system manager
    def init(self, sm_username, sm_password):
        if self.sys.init_system(sm_username, sm_password) is not None:
            print("System initialized successfully")
            return True
        else:
            print("System failed to initialize")
            return False

    def sign_up(self, username, password):
        if self.sys.sign_up(username, password):
            print("Signed up successfully")
            return True
        else:
            print("Sign up failed")
            return False

    def login(self, username, password):
        if self.sys.login(username, password):
            print("Logged in")
            return True
        else:
            print("Login failed. Please check username and password are correct")
            return False

    def search(self, keyword):
        items_list = self.sys.search(keyword)
        if len(items_list) == 0:
            print("No item matching the search")
            return []
        output_list = []
        for item in items_list:
            print(item)
            output_list.append({'name': item.name, 'price': item.price, 'category': item.category})
        return output_list

    def logout(self):
        if self.sys.logout():
            print("Logged out")
            return True
        else:
            print("Logout failed")
            return False

    def create_store(self, name):
        created = self.sys.create_store(name)
        if not created:
            print("Could not create store" + name)
            return False
        else:
            print("New store created")
            print("Name: " + created.name)
            print("Owners: ")
            print(created.storeOwners)
            owners = []
            for o in created.storeOwners:
                owners.append({'username': o.username})
            return {'name': created.name, 'storeOwners': owners}

    def remove_user(self, username):
        if not self.sys.remove_user(username):
            print("Can't remove user")
            return False
        else:
            print("User " + username + "removed")
            return True

    def get_cart(self, store_name):
        curr_user = self.sys.get_cur_user()
        cart = curr_user.get_cart(store_name)
        if not cart:
            print(store_name + " cart doesn't exist")
            return False
        for i in cart.keys():
            print("Item name: " + i + "quantity: " + cart[i])
        return cart.items_and_quantities

    def add_to_cart(self, store_name, item_name, quantity):
        if not self.sys.add_to_cart(store_name, item_name, quantity):
            print("Can't add item " + item_name + " to cart " + store_name)
            return False
        print("Item " + item_name + " added successfully to cart " + store_name)
        curr_user = self.sys.get_cur_user()
        cart = curr_user.get_cart(store_name)
        if not cart:
            return cart
        return cart.items_and_quantities

    def remove_from_cart(self, store_name, item_name):
        curr_user = self.sys.get_cur_user()
        if not curr_user.remove_from_cart(store_name, item_name):
            print("Can't remove item " + item_name + " from cart " + store_name)
            return False
        print("Item " + item_name + " removed from cart " + store_name)
        return curr_user.get_cart().items_and_quantities

    def buy_items(self, items):
        if not self.sys.buy_items(items):
            print("Can't buy requested items. Transaction cancelled")
            return False
        print("Transaction succeeded. Items removed from basket")
        return True

    # item ::= {'name': string, 'prince': int, 'category': string}
    def add_item_to_inventory(self, item, store_name, quantity):
        store = self.sys.get_store(store_name)
        if store is None:
            print("Error: can't add items to store " + store_name)
            return False
        user = self.sys.get_cur_user()
        if user is None:
            print("Error: no current user")
            return False
        if not store.add_item_to_inventory(user, item, quantity):
            print("Error: can't add item " + item + " to store " + store_name)
            return False
        inv = []
        for i in store.inventory:
            inv.append({'name': i['name'], 'quantity': i['quantity']})
        return inv

    def remove_item_from_inventory(self, item_name, store_name):
        store = self.sys.get_store(store_name)
        if store is None:
            print("Error: can't remove items from store " + store_name)
            return False
        user = self.sys.get_cur_user()
        if user is None:
            print("Error: no current user")
            return False
        if not store.remove_item_from_inventory(user, item_name):
            print("Error: can't remove item " + item_name + " to store " + store_name)
            return False
        inv = []
        for i in store.inventory:
            inv.append({'name': i['name'], 'quantity': i['quantity']})
        return inv

    def decrease_item_quantity(self, store_name, item_name, quantity):
        store = self.sys.get_store(store_name)
        if store is None:
            print("Error: can't remove items from store " + store_name)
            return False
        user = self.sys.get_cur_user()
        if user is None:
            print("Error: no current user")
            return False
        if not store.remove_item_by_quantity(user, item_name, quantity):
            print("Can't change quantity of item " + item_name)
            return False
        inv = []
        for i in store.inventory:
            inv.append({'name': i['name'], 'quantity': i['quantity']})
        return inv

    def edit_item_price(self, store_name, item_name, new_price):
        store = self.sys.get_store(store_name)
        if store is None:
            print("Error: can't edit items in store " + store_name)
            return False
        user = self.sys.get_cur_user()
        if user is None:
            print("Error: no current user")
            return False
        if not store.edit_item_price(user, item_name, new_price):
            print("Error: can't edit item " + item_name + " in store " + store_name)
            return False
        ret = store.search_item_by_name(item_name)
        return {'name': ret.name, 'price': ret.price, 'category': ret.category}

    def add_new_owner(self, store_name, new_owner):
        if not self.sys.add_owner_to_store(store_name, new_owner):
            print("Can't add new owner " + new_owner + " to store " + store_name)
            return False
        store = self.sys.get_store(store_name)
        owners = []
        for o in store.storeOwners:
            owners.append({'username': o.username})
        return {'name': store_name, 'storeOwners': owners}

    def add_new_manager(self, store_name, new_manager, permissions):
        if not self.sys.add_manager_to_store(store_name, new_manager, permissions):
            print("Can't add new manager " + new_manager + " to store " + store_name)
            return False
        store = self.sys.get_store(store_name)
        managers = []
        for m in store.storeManagers:
            managers.append({'username': m.username})
        return {'name': store_name, 'storeManagers': managers}

    def remove_owner(self, store_name, owner_to_remove):
        if not self.sys.remove_owner_from_store(store_name, owner_to_remove):
            print("Can't remove owner " + owner_to_remove + " from store " + store_name)
            return False
        store = self.sys.get_store(store_name)
        owners = []
        for o in store.storeOwners:
            owners.append({'username': o.username})
        return {'name': store_name, 'storeOwners': owners}

    def remove_manager(self, store_name, manager_to_remove):
        if not self.sys.remove_manager_from_store(store_name, manager_to_remove):
            print("Can't remove manager " + manager_to_remove + " from store " + store_name)
            return False
        store = self.sys.get_store(store_name)
        managers = []
        for m in store.storeManagers:
            managers.append({'username': m.username})
        return {'name': store_name, 'storeManagers': managers}

