import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


@lru_cache(maxsize=1)
def get_db() -> Client:
    """Return a shared Supabase client, built from SUPABASE_URL / SUPABASE_KEY."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set (see .env.example)")
    return create_client(url, key)


def test_connection() -> bool:
    try:
        response = get_db().table("outlets").select("*").limit(1).execute()
        print(f"Connection successful ({len(response.data)} sample row)")
        return True
    except Exception as e:
        print("Error connecting to the database:", e)
        return False
