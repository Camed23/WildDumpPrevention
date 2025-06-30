from backend.config import supabase
from backend.services.user_service import get_or_create_user
from backend.services.feature_extractor import calculate_image_properties

def insert_image_metadata(filename, filepath):
    size, width, height, avg_red, avg_green, avg_blue, contrast, edges_detected = calculate_image_properties(filepath)
    user_id = get_or_create_user()

    return supabase.rpc("creation_image", {
        "p_user_id": user_id,
        "p_file_path": f"/uploads/{filename}",
        "p_name_image": filename,
        "p_size": size,
        "p_width": width,
        "p_height": height,
        "p_avg_red": avg_red,
        "p_avg_green": avg_green,
        "p_avg_blue": avg_blue,
        "p_contrast": contrast,
        "p_edges_detected": int(edges_detected)
    }).execute()

def insert_annotation(image_id, label, source='manuel'):
    return supabase.rpc("creation_annotation", {
        "p_image_id": image_id,
        "p_label": label,
        "p_source": source
    }).execute()

def get_image_id_by_filename(filename):
    result = supabase.table("image").select("image_id").eq("name_image", filename).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]['image_id']
    return None
