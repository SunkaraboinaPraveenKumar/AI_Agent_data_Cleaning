from data_ingestion import DataIngestion
from data_cleaning import DataCleaning
from ai_agent import AIAgent

# ✅ Database Configuration for MySQL
# Replace with your actual MySQL credentials
DB_USER = "root"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "shopping"

# Construct the MySQL database URL
DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ✅ Initialize DataIngestion, DataCleaning, and AIAgent Components
ingestion = DataIngestion(DB_URL)
cleaner = DataCleaning()
ai_agent = AIAgent()

# ===================================
# === 1️⃣ Load and Clean CSV Data ===
# ===================================
print("🚀 Loading CSV Data...")
df_csv = ingestion.load_csv("sample_data.csv")

if df_csv is not None:
    print("\n🔹 Cleaning CSV Data...")
    # Clean the CSV data
    df_csv = cleaner.clean_data(df_csv)
    
    # Process the data using AI logic
    df_csv = ai_agent.process_data(df_csv)

    print("\n✅ AI-Cleaned CSV Data:\n", df_csv)

# =====================================
# === 2️⃣ Load and Clean Excel Data ===
# =====================================
print("\n🚀 Loading Excel Data...")
df_excel = ingestion.load_excel("sample_data.xlsx")

if df_excel is not None:
    print("\n🔹 Cleaning Excel Data...")
    # Clean the Excel data
    df_excel = cleaner.clean_data(df_excel)
    
    # Process the data using AI logic
    df_excel = ai_agent.process_data(df_excel)

    print("\n✅ AI-Cleaned Excel Data:\n", df_excel)

# ========================================
# === 3️⃣ Load and Clean Database Data ===
# ========================================
print("\n🚀 Loading Data from Database...")

# SQL query to retrieve data from your table
sql_query = "SELECT * FROM products;"  # Replace `my_table` with your actual table name

df_db = ingestion.load_from_database(sql_query)

if df_db is not None:
    print("\n🔹 Cleaning Database Data...")
    
    # Clean the database data
    df_db = cleaner.clean_data(df_db)
    
    # Process the data using AI logic
    df_db = ai_agent.process_data(df_db)

    print("\n✅ AI-Cleaned Database Data:\n", df_db)

# =====================================
# === 4️⃣ Fetch and Clean API Data ====
# =====================================
print("\n🚀 Fetching Data from API...")

# API endpoint
API_URL = "https://jsonplaceholder.typicode.com/posts"

df_api = ingestion.fetch_from_api(API_URL)

if df_api is not None:
    print("\n🔹 Cleaning API Data...")
    
    # ✅ Limit the size of the dataset to avoid token overflow
    df_api = df_api.head(30)  # Adjust as necessary

    # ✅ Truncate text fields to avoid sending too much data to the AI
    if "body" in df_api.columns:
        df_api["body"] = df_api["body"].apply(lambda x: x[:100] + "..." if isinstance(x, str) else x)

    # Clean the API data
    df_api = cleaner.clean_data(df_api)
    
    # Process the data using AI logic
    df_api = ai_agent.process_data(df_api)

    print("\n✅ AI-Cleaned API Data:\n", df_api)

# ================================================
# === Export Cleaned Data Back to CSV (Optional) ==
# ================================================
# Example of exporting cleaned data back to CSV or database
print("\n🚀 Exporting cleaned data to CSV...")

if df_csv is not None:
    cleaned_csv_path = "cleaned_sample_data.csv"
    df_csv.to_csv(cleaned_csv_path, index=False)
    print(f"\n✅ Cleaned CSV data exported successfully: {cleaned_csv_path}")

if df_excel is not None:
    cleaned_excel_path = "cleaned_sample_data.xlsx"
    df_excel.to_excel(cleaned_excel_path, index=False)
    print(f"\n✅ Cleaned Excel data exported successfully: {cleaned_excel_path}")

if df_db is not None:
    cleaned_db_csv_path = "cleaned_database_data.csv"
    df_db.to_csv(cleaned_db_csv_path, index=False)
    print(f"\n✅ Cleaned Database data exported successfully: {cleaned_db_csv_path}")

if df_api is not None:
    cleaned_api_csv_path = "cleaned_api_data.csv"
    df_api.to_csv(cleaned_api_csv_path, index=False)
    print(f"\n✅ Cleaned API data exported successfully: {cleaned_api_csv_path}")
