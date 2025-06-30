# backend/config.py

from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
IMAGE_TABLE  = os.getenv("IMAGE_TABLE", "image")
CACHE_PATH   = os.getenv("CACHE_PATH",  "cache\images_metadata.json")
