from flask_pymongo import PyMongo
from flask_cors import CORS

# สร้าง instance ของ PyMongo
mongo = PyMongo()

# สร้าง instance ของ CORS
cors = CORS()
