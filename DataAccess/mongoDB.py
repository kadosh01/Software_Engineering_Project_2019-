import pymongo

from Domain.User import User


class DB:
    def __init__(self):
        self.myclient = pymongo.MongoClient("mongodb+srv://grsharon:1234@cluster0-bkvsz.mongodb.net/test?retryWrites=true&w=majority")
        self.mydb = self.myclient["Store"]

    # adder functions

    def add_user(self, user):
        collection = self.mydb["Users"]
        user_to_add = {"name": user.username, "password": user.password, "age": user.age, "country": user.country}
        collection.insert_one(user_to_add)

    def add_store(self, store, username):
        collection = self.mydb["Stores"]
        store_to_add = {"name": store.name, "rank": store.rank}
        collection.insert_one(store_to_add)
        self.add_store_owner(store.name, username, 0)

    def add_store_owner(self, store_name, user_name, appointer):
        collection = self.mydb["StoreOwners"]
        store_owner_to_add = {"store_name": store_name, "owner": user_name, "appointer": appointer}
        collection.insert_one(store_owner_to_add)

    def add_store_manager(self, store_name, user_name, appointer, is_add_per, is_edit_per, is_remove_per, is_disc_per):
        collection = self.mydb["StoreManagers"]
        store_manager_to_add = {"store_name": store_name, "manager": user_name, "appointer": appointer,
                                "permission": {"add": is_add_per, "edit": is_edit_per,
                                               "remove": is_remove_per, "Discounts": is_disc_per}}
        collection.insert_one(store_manager_to_add)

    # policy = {type, combo, args, override}
    def add_item(self, item_name, store_name, price, category, quantity, policy):
        collection = self.mydb["Items"]
        item_to_add = {"name": item_name, "store": store_name, "price": price, "category": category,
                       "quantity": quantity, "policy": {"type": policy['type'], "combo": policy['combo'],
                                                        "args": policy['args'], "override": policy['override']}}
        collection.insert_one(item_to_add)

    def add_notification(self, sender_username, receiver_username, key, message):
        collection = self.mydb["UserNotification"]
        not_to_add = {"sender_username": sender_username, "receiver_username": receiver_username,
                      "key": key, "message": message}
        collection.insert_one(not_to_add)

    def add_cart(self, user_name, store_name, item_name, quantity):
        collection = self.mydb["Cart"]
        cart_to_add = {"user_name": user_name, "store_name": store_name, "item_name": item_name, "quantity": quantity}
        collection.insert_one(cart_to_add)

    def add_policy_to_item(self, store_name, item_name, new_policy): pass
    # TODO: set new policy to an item

    def add_policy_to_store(self, store_name, new_policy): pass
    # TODO: set new policy to a store

    # getters

    def get_user(self, user_name):
        if self.does_user_exist(user_name):
            curs = self.mydb.Users.find_one({"name": user_name})
            the_user = User(user_name, curs['password'], curs['age'], curs['country'])
            return the_user
        return None

    def does_user_exist(self, user_name):
        return True if self.mydb.Users.count_documents({"name": user_name}) > 1 else False

    def get_store(self, store_name):
        return self.mydb.Stores.find({"name": store_name})

    def get_item_from_store(self, param, store_name):
        return self.mydb.Items.find({"store": store_name}, {"quantity": {"$gt": 0}},
                                    {"$or": [{"name": param}, {"price": param}, {"category": param}]})

    def get_inventory_from_db(self):
        return self.mydb.Items.find({})

    def get_all_stores_from_db(self):
        return self.mydb.Stores.find({})

    # editors

    def edit_item_price_in_db(self, store_name, item_name, new_price):
        collection = self.mydb["Items"]
        item_to_change = {"name": item_name, "store": store_name}
        collection.update_one(item_to_change, {"$set": {"price": new_price}})

    def edit_item_quantity_in_db(self, store_name, item_name, quantity):
            collection = self.mydb["Items"]
            item_to_change = {"name": item_name, "store": store_name}
            collection.update_one(item_to_change, {"$inc": {"quantity": quantity}})

    # removers

    def remove_user(self, user_name):
        collection = self.mydb["Users"]
        user_to_remove = {"name": user_name}
        collection.delete_one(user_to_remove)
        collection2 = self.mydb["StoreOwners"]
        owners_to_remove = {"appointer": user_name}
        collection2.delete_many(owners_to_remove)
        collection2.delete_many({"owner": user_name})
        collection3 = self.mydb["StoreManagers"]
        managers_to_remove = {"appointer": user_name}
        collection3.delete_many(managers_to_remove)
        collection3.delete_many({"manager": user_name})

    def remove_store(self, store_name):
        collection = self.mydb["Stores"]
        store_to_remove = {"name": store_name}
        collection.delete_one(store_to_remove)
        collection1 = self.mydb["StoreManagers"]
        collection1.delete_many({"store_name": store_name})
        collection2 = self.mydb["StoreOwners"]
        collection2.delete_one({"store_name": store_name})
        collection3 = self.mydb["Items"]
        collection3.delete_many({"store": store_name})
        collection4 = self.mydb["Cart"]
        collection4.delete_many({"store_name": store_name})

    def remove_store_manager(self, manager_name, store_name):
        collection = self.mydb["StoreManagers"]
        manager_to_remove = {"store_name": store_name, "manager": manager_name}
        collection.delete_one(manager_to_remove)

    def remove_store_owner(self, store_name, owner_name):
        collection = self.mydb["StoreOwners"]
        owner_to_remove = {"store_name": store_name, "owner": owner_name}
        collection.delete_one(owner_to_remove)

    def remove_cart(self, user_name, store_name):
        collection = self.mydb["Cart"]
        cart_to_remove = {"user_name": user_name, "store_name": store_name}
        collection.delete_one(cart_to_remove)

    def remove_item_from_cart(self, user_name, store_name, item_name, quantity_to_remove):
        collection = self.mydb["Cart"]
        item_to_remove_from_cart = {"user_name": user_name, "store_name": store_name, "item_name": item_name}
        collection.update_one(item_to_remove_from_cart, {"$inc": {"quantity": quantity_to_remove}})
