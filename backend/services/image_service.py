from backend.config import supabase

def insert_image_metadata(
    filename, user_id,
    location=None,
    size=None, width=None, height=None,
    avg_red=None, avg_green=None, avg_blue=None, contrast=None,
    edges_detected=None
):
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
        "p_edges_detected": bool(edges_detected),
        "p_localisation": location
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
