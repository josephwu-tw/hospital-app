import mysql.connector
from config import DB_CONFIG

# --- Local ---
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- GCP Cloud Run: uncomment below and comment out the local block above ---
# from mysql.connector.pooling import MySQLConnectionPool
# _pool = MySQLConnectionPool(pool_name="main", pool_size=5, **DB_CONFIG)
# def get_connection():
#     return _pool.get_connection()


def execute_query(sql, params=None, one=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    result = cursor.fetchone() if one else cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def execute_update(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id
