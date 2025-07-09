# backend/config.py

from supabase import create_client, Client


SUPABASE_URL = "https://bqkxmcrmolfjlglmmqlj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJxa3htY3Jtb2xmamxnbG1tcWxqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA3NzI1ODgsImV4cCI6MjA2NjM0ODU4OH0.QrcFfKD2aHZP-PwVoWWq1hnNZ5cOCckL4YvmPHsSmt0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


IMAGE_TABLE= "image"
CACHE_PATH= "cache/images_metadata.json"
