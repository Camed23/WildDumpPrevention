import os
from backend.config import supabase
from backend.services.user_service import get_or_create_user

def insert_image_metadata(filename, filepath):
    size_kb = os.path.getsize(filepath) / 1024
    user_id = get_or_create_user()
    return supabase.rpc("creation_image", {
        "p_user_id": user_id,
        "p_file_path": f"/uploads/{filename}",
        "p_name_image": filename,
        "p_size": size_kb,
        "p_width": 0,
        "p_height": 0,
        "p_avg_red": 0,
        "p_avg_green": 0,
        "p_avg_blue": 0,
        "p_contrast": 0,
        "p_edges_detected": False
    }).execute()
