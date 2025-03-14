import mysql.connector

# 🔹 Update these credentials
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "shopping"
DB_USER = "root"
DB_PASSWORD = "1234"

try:
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    print("✅ MySQL Connection Successful!")

    # Check if database is selected
    cursor.execute("SELECT DATABASE();")
    current_db = cursor.fetchone()
    print(f"📌 Connected to database: {current_db[0]}")

    # Execute a test query
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    
    if not tables:
        print("⚠️ No tables found in the database.")
    else:
        print("✅ Tables in the database:")
        for table in tables:
            print(table[0])

    # Close connection
    cursor.close()
    connection.close()
    print("✅ Connection Closed.")

except mysql.connector.Error as err:
    print(f"❌ Error connecting to MySQL: {err}")