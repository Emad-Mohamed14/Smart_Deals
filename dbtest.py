import MySQLdb

try:
    db = MySQLdb.connect(
        host="localhost",
        user="root",  # Replace with your user
        passwd="tsee12345",  # Replace with your password
        db="smart_deals"  # Replace with your database name
    )
    print("Connection successful")
except MySQLdb.Error as e:
    print(f"Error connecting to MySQL: {e}")
finally:
    if db:
        db.close()