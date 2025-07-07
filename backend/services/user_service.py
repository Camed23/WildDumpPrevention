from backend.config import supabase

def get_or_create_user(username="ecologiste", email="jsuisecolo@example.com", password="qwerty", role="Admin"):
    result = supabase.table("User").select("*").eq("username", username).execute()
    if result.data:
        return result.data[0]['user_id']
    supabase.rpc("creation_user", {
        "p_username": username,
        "p_email": email,
        "p_password": password,
        "p_role": role
    }).execute()
    result = supabase.table("User").select("*").eq("username", username).execute()
    return result.data[0]['user_id']

def get_user_id_by_email(email):
    result = supabase.table("User").select("user_id").eq("email", email).execute()
    if result.data:
        return result.data[0]['user_id']
    return None
