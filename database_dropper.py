from pymongo import MongoClient
client = MongoClient()
for database in client.list_database_names(): 
    if database == "admin" or database == "config" or database == "local": continue 
    client.drop_database(database)
