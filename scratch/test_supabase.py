import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def test_supabase():
    try:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = sb.table("foods").select("*").execute()
        print(f"Success! Found {len(res.data)} foods.")
        if len(res.data) > 0:
            print(f"First food: {res.data[0]['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_supabase()
