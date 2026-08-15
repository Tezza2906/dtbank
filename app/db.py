import mysql.connector 
from mysql.connector import connect
from config import DB_CONFIG

# def get_db():
#     return ms.connect(**DB_CONFIG)   # ** used for unpacking


def get_db():
    conn=  mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        auth_plugin="mysql_native_password",
    )
    return conn