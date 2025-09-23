import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# connect to the database
def get_db():
    return supabase

# function to see the connection
def test_connection():
    try:
        response = supabase.table("outlets").select("*").execute()
        print("Connection successful:", response)
    except Exception as e:
        print("Error connecting to the database:", e)





