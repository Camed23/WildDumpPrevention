# backend/config.py

from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
IMAGE_TABLE  = os.getenv("IMAGE_TABLE", "image")
CACHE_PATH   = os.getenv("CACHE_PATH",  "cache\images_metadata.json")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
