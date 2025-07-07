from backend.config import supabase
response = supabase.table("annotation").select("label, image_id, image(size)").execute()
print(response.data)