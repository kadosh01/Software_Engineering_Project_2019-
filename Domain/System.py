from Domain.Cart import Cart
from Domain.ExternalSystems import *
from Domain.User import User
from Domain.Guest import Guest
from Domain.Store import Store
from Domain.Response import ResponseObject
from Domain.SystemManager import SystemManager
from passlib.hash import pbkdf2_sha256
from log.Log import Log
from DataAccess import sqlite_database
import functools


class System:

    def __init__(self):
        self.user_types = {"1": "guest", "2": "user", "3": "store_owner", "4": "store_manager", "5": "sys_manager"}
        self.system_manager = None
        self.database = sqlite_database
        # self.cur_user = None
        self.users = {}  # {username, user}
        self.loggedInUsers = {}     # logged in users that are currently in the system
        self.guests = {}    # guests that are currently in the system
        self.stores = []
        self.log = Log("", "")
        self.supplying_system = SupplyingSystem()
        self.collecting_system = CollectingSystem()
        self.traceability_system = TraceabilitySystem()

    def get_user_or_guest(self, username):
        if username in self.loggedInUsers:
            curr_user = self.loggedInUsers[username]
        elif username in self.guests:
            curr_user = self.guests[username]
        else:
            return ResponseObject(False, False, "User " + username + " doesn't exist in the system")
        return ResponseObject(True, curr_user, "")

    def init_system(self, system_manager_user_name, system_manager_password, system_manager_age, system_manager_country):
        if not self.supplying_system.init() or not self.traceability_system.init() or not self.collecting_system.init():
            return ResponseObject(False, False, "Can't init external systems")
        result = self.sign_up(system_manager_user_name, system_manager_password, system_manager_age, system_manager_country)
        if not result.success:
            self.log.set_info("error: System manager could not sign up", "eventLog")
            return ResponseObject(False, None, "System manager could not sign up")
        enc_password = pbkdf2_sha256.hash(system_manager_password)
        manager = SystemManager(system_manager_user_name, enc_password, system_manager_age, system_manager_country)
        # self.users[manager.username] = manager
        self.system_manager = manager
        # init db
        self.database.set_up()
        return ResponseObject(True, True, "")

    def sign_up(self, username, password, age, country):
        if username is None or username == '':
            self.log.set_info("error: signup failed: Username can not be empty", "eventLog")
            return ResponseObject(False, False, "Username can not be empty")
        if password is None or password == '':
            self.log.set_info("error: signup failed: Password can not be empty", "eventLog")
            return ResponseObject(False, False, "Password can not be empty")
        if username in self.users:
            self.log.set_info("error: signup failed: This user name is already taken", "eventLog")
            return ResponseObject(False, False, "This user name is already taken")
        else:
            enc_password = pbkdf2_sha256.hash(password)
            new_user = User(username, enc_password, age, country)
            # self.database.add_to_users(new_user)
            self.users[username] = new_user
            self.log.set_info("signup succeeded", "eventLog")
            return ResponseObject(True, True, "Welcome new user " + username + "! You may now log in")

    def login(self, username, password):
        if username not in self.users:
            self.log.set_info("error: login failed: Username doesn't exist", "eventLog")
            return ResponseObject(False, False, "Username doesn't exist")
        user_to_check = self.users[username]
        if user_to_check.logged_in:
            self.log.set_info("error: login failed: You are already logged in", "eventLog")
            return ResponseObject(False, False, "You are already logged in")
        elif not pbkdf2_sha256.verify(password, user_to_check.password):
            self.log.set_info("error: login failed: Wrong password", "eventLog")
            return ResponseObject(False, False, "Wrong password")
        else:
            user_to_check.logged_in = True
            self.loggedInUsers[username] = user_to_check
            self.log.set_info("login succeeded", "eventLog")
            user_type = self.get_user_type(username)
            return ResponseObject(True, user_type, "Hey " + username + "! You are now logged in")

    def logout(self, username):
        if username not in self.loggedInUsers:
            self.log.set_info("error: logout failed: you are not logged in", "eventLog")
            return ResponseObject(False, False, "You are not logged in")
        else:
            self.loggedInUsers[username].logged_in = False
            self.loggedInUsers.pop(username)
            self.log.set_info("Logged out successfully", "eventLog")
            return ResponseObject(True, True, "Logged out successfully")

    def search(self, param):
        ret_list = []
        for store in self.stores:
            boo = store.search_item_by_name(param)
            if boo:
                ret_list.append(boo)
            ret_list.extend(store.search_item_by_category(param))
            ret_list.extend(store.search_item_by_price(param))
        return ret_list

    @staticmethod
    def filter_by_price_range(item_list, low, high):
        result_list = []
        for item in item_list:
            if low <= item.price <= high:
                result_list.append(item)
        return result_list

    @staticmethod
    def filter_by_item_rank(item_list, low, high):
        result_list = []
        for item in item_list:
            if low <= item.rank <= high:
                result_list.append(item)
        return result_list

    @staticmethod
    def filter_by_item_category(item_list, category):
        result_list = []
        for item in item_list:
            if item.category == category:
                result_list.append(item)
        return result_list

    def add_owner_to_store(self, store_name, new_owner_name, username):
        store_result = self.get_store(store_name)
        if not store_result.success:
            return store_result
        store = store_result.value
        new_owner_obj = self.get_user(new_owner_name)
        if new_owner_obj is None:
            self.log.set_info("error: adding owner failed: user is not a user in the system", "eventLog")
            return ResponseObject(False, False, new_owner_name + " is not a user in the system")
        find_user = self.sys.get_user_or_guest(username)
        if not find_user.success:
            return find_user
        curr_user = find_user.value
        add = store.add_new_owner(curr_user, new_owner_obj)
        if not add.success:
            return add
        self.log.set_info("adding owner succeeded", "eventLog")
        return ResponseObject(True, True, "")

    def remove_owner_from_store(self, store_name, owner_to_remove, username):
        store_result = self.get_store(store_name)
        if not store_result.success:
            return store_result
        store = store_result.value
        new_owner_obj = self.get_user(owner_to_remove)
        if new_owner_obj is None:
            self.log.set_info("error: remove owner failed: user is not in the system", "eventLog")
            return ResponseObject(False, False, owner_to_remove + " is not a user in the system")
        find_user = self.sys.get_user_or_guest(username)
        if not find_user.success:
            return find_user
        curr_user = find_user.value
        remove = store.remove_owner(curr_user, new_owner_obj)
        if not remove.success:
            return remove
        self.log.set_info("remove owner succeeded", "eventLog")
        return ResponseObject(True, True, "")

    def add_manager_to_store(self, store_name, new_manager_name, permissions, username):
        store_result = self.get_store(store_name)
        if not store_result.success:
            return store_result
        store = store_result.value
        new_manager_obj = self.get_user(new_manager_name)
        if new_manager_obj is None:
            self.log.set_info("error: adding manager failed: user is not in the system", "eventLog")
            return ResponseObject(False, False, new_manager_name + " is not a user in the system")
        find_user = self.sys.get_user_or_guest(username)
        if not find_user.success:
            return find_user
        curr_user = find_user.value
        add = store.add_new_manager(curr_user, new_manager_obj, permissions)
        if not add.success:
            return add
        self.log.set_info("adding manager succeeded", "eventLog")
        return ResponseObject(True, True, "")

    def remove_manager_from_store(self, store_name, manager_to_remove, username):
        store_result = self.get_store(store_name)
        if not store_result.success:
            return store_result
        store = store_result.value
        new_manager_obj = self.get_user(manager_to_remove)
        if new_manager_obj is None:
            self.log.set_info("error: removing manager failed: user is not in the system", "eventLog")
            return ResponseObject(False, False, manager_to_remove + " is not a user in the system")
        find_user = self.sys.get_user_or_guest(username)
        if not find_user.success:
            return find_user
        curr_user = find_user.value
        remove = store.remove_manager(curr_user, new_manager_obj)
        if not remove.success:
            return remove
        self.log.set_info("removing manager succeeded", "eventLog")
        return ResponseObject(True, True, "")

    def buy_items(self, items, username):
        # check if items exist in basket??
        for item in items:
            store = self.get_store(item['store_name'])
            if not store.success:
                self.log.set_info("error: buy items failed: store does not exist", "eventLog")
                return ResponseObject(False, False, "buy items failed: Store " + item['store_name'] + " does not exist")
            if not self.supplying_system.get_supply(item['name']):
                self.log.set_info("error: buy items failed: item is out of stock", "eventLog")
                return ResponseObject(False, False, "Item " + item['name'] + " is currently out of stock")
        find_user = self.get_user_or_guest(username)
        if not find_user.success:
            return find_user
        curr_user = find_user.value
        # TODO: apply discount
        amount = functools.reduce(lambda acc, it: (acc + it['price']), items, 0)
        flag = self.collecting_system.collect(amount, curr_user.creditDetails)
        if flag == 0:
            self.log.set_info("error: buy items failed: payment rejected", "eventLog")
            return ResponseObject(False, False, "Payment rejected")
        for item in items:
            removed = curr_user.remove_from_cart(item['store_name'], item['name'])
            if not removed.success:
                self.log.set_info("error: buy items failed", "eventLog")
                return ResponseObject(False, False, "Cannot purchase item " + item.name + "\n" + removed.message)

        # Todo : remove items from store inventory
        self.log.set_info("buy items succeeded", "eventLog")
        return ResponseObject(True, amount, "")

    def create_store(self, store_name, username):
        if username not in self.loggedInUsers:
            self.log.set_info("error: create store failed: user is not a subscriber in the system", "eventLog")
            return ResponseObject(False, None, "User " + username +
                                  " is not a subsciber in the system, or is not logged in")
        b = False
        for stur in self.stores:
            if stur.name == store_name:
                b = True
        if b:
            self.log.set_info("error: create store failed: store already exists", "eventLog")
            return ResponseObject(False, None, "Store already exists")
        else:
            new_store = Store(store_name, self.loggedInUsers[username])
            self.stores.append(new_store)
            self.log.set_info("create store succeeded", "eventLog")
            return ResponseObject(True, new_store, "")

    def remove_user(self, user_to_remove, username):
        if username not in self.loggedInUsers:
            self.log.set_info("error: remove user failed: user is not a subscriber in the system", "eventLog")
            return ResponseObject(False, None, "User " + username +
                                  " is not a subsciber in the system, or is not logged in")
        if username != self.system_manager.username:
            self.log.set_info("error: removing user failed: user is not a system manager", "eventLog")
            return ResponseObject(False, False, "You can't remove a user, you are not the system manager")
        if self.system_manager.username == user_to_remove:
            self.log.set_info("error: removing user failed: user can't remove himself", "eventLog")
            return ResponseObject(False, False, "You can't remove yourself silly")
        remove_user = self.loggedInUsers[user_to_remove]
        stores_to_remove = []
        for store in self.stores:
            if len(store.storeOwners) == 1 and remove_user.username == store.storeOwners[0].username:
                stores_to_remove.append(store)
        for st in stores_to_remove:
            self.stores.remove(st)
        self.loggedInUsers.pop(user_to_remove)
        self.users.pop(user_to_remove)
        self.log.set_info("removing user succeeded", "eventLog")
        return ResponseObject(True, True, "User " + user_to_remove + " removed")

    def get_store(self, store_name):
        for stor in self.stores:
            if store_name == stor.name:
                self.log.set_info("get store succeeded", "eventLog")
                return ResponseObject(True, stor, "")
        self.log.set_info("error: get store failed: store doesn't exist in the system", "eventLog")
        return ResponseObject(False, None, "Store " + store_name + " doesn't exist in the system")

    def get_basket(self, username):
        find_user = self.get_user_or_guest(username)
        if not find_user.success:
            return find_user
        curr_user = find_user.value
        non_empty = 0
        basket_ret = []
        basket = curr_user.get_basket()
        for cart in basket.carts:
            if len(cart.items_and_quantities) > 0:
                non_empty = 1
            cart_ret = []
            store = self.get_store(cart.store_name).value
            for product in cart.items_and_quantities:
                item = store.get_item_if_available(product, cart.items_and_quantities.get(product))
                quantity = cart.items_and_quantities[product]
                cart_ret.append({'name': item.name, 'price': item.price, 'quantity': quantity,
                                'category': item.category, 'rank': item.rank, 'discount': ''})
            basket_ret.append({'cart': cart_ret, 'store': store.name})
        return ResponseObject(False, False, "") if non_empty == 0 else ResponseObject(True, basket_ret, "")

    def get_basket_size(self):
        basket = self.get_basket()
        size =0
        if basket.success:
            for cart in basket.value:
                for item in cart['cart']:
                    size += 1

        return ResponseObject(True, size , "")

    def get_user(self, username):
        if username in self.users:
            print(self.users[username])
            return self.users[username]
        return None

    def add_to_cart(self, store_name, item_name, quantity, username):
        result = self.get_store(store_name)
        if not result.success:
            self.log.set_info("error: adding to cart failed: no such store", "eventLog")
            return ResponseObject(False, False, result.message)
        store = result.value
        available = store.get_item_if_available(item_name, quantity)
        if not available:
            self.log.set_info("error: adding to cart failed: item is not available", "eventLog")
            return ResponseObject(False, False, "Item " + item_name + "is not available")
        find_user = self.sys.get_user_or_guest(username)
        if not find_user.success:
            return find_user
        curr_user = find_user.value
        item = store.search_item_by_name(item_name)
        tmp_cart = Cart(store_name, curr_user)
        old_cart = curr_user.get_cart(store_name)
        tmp_cart.items_and_quantities = old_cart.value.items_and_quantities
        tmp_cart.add_item_to_cart(item_name, quantity)
        if not store.buying_policy.apply_policy(tmp_cart):
            self.log.set_info("error: adding to cart failed: store policy", "eventLog")
            return ResponseObject(False, False, "Store policy")
        if not item.buying_policy.apply_policy(tmp_cart):
            self.log.set_info("error: adding to cart failed: store policy", "eventLog")
            return ResponseObject(False, False, "Store policy")
        curr_user.add_to_cart(store_name, item_name, quantity)
        self.log.set_info("adding to cart succeeded", "eventLog")
        return ResponseObject(True, True, "")

    def get_total_system_inventory(self):
        retList = []
        for store in self.stores:
            for item in store.inventory:
                new_item = {'name': item['name'], 'category': item['val'].category, 'price': item['val'].price,
                            'quantity': item['quantity'], 'store_name': store.name}
                retList.append(new_item)
        return ResponseObject(True, retList, "")

    def get_user_type(self, username):
        if username == self.system_manager.username:
            return "sys_manager"
        for store in self.stores:
            for owner in store.storeOwners:
                if username == owner.username:
                    return "store_owner"
            for manager in store.storeManagers:
                if username == manager.username:
                    return "store_manager"
        if username in self.users:
            return "user"
        return "guest"

    def get_stores(self):
        return self.stores
