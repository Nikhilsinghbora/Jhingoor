# We can also use supabase without orm using this client directly
import os
from supabase import create_client, Client
from dotenv import load_dotenv
# Load variables from .env
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env file")

# Initialize the Supabase client
# This 'supabase' object is what you import in your handlers
supabase: Client = create_client(url, key)