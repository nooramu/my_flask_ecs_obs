import os
from pymongo import MongoClient, errors


username = os.getenv('MONGO_USERNAME', 'rwuser')
password = os.getenv('MONGO_PASSWORD', '022000Ql!')
hostname = '120.46.54.234'  # 使用公网 IP
port = 8635
database = 'test'

# 创建MongoDB连接URI
MONGO_URI = f"mongodb://{username}:{password}@{hostname}:{port}/{database}?authSource=admin"

try:
    print("Trying to connect to MongoDB...")
    # 建立连接
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=30000,  # 设置超时时间为 30 秒
    )

    # 选择数据库
    db = client.get_database()
    print("Connected to MongoDB successfully.")
    
    # 查询数据库内容
    print("Querying database...")
    collections = db.list_collection_names()
    print("Collections in database:", collections)
    
    # 查询 user 集合中的所有文档
    if 'user' in collections:
        cursor = db.user.find()
        for document in cursor:
            print(document)
    else:
        print("Collection 'user' not found.")
except errors.PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")
