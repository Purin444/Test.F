from extensions import mongo

def create_user(username, password_hash):
    """ สร้าง User ใหม่ """
    user_collection = mongo.db.auth_users
    user_collection.insert_one({"username": username, "password": password_hash})

def find_user_by_username(username):
    """ ค้นหา User จาก Username """
    user_collection = mongo.db.auth_users
    return user_collection.find_one({"username": username})
