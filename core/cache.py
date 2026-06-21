import hashlib
import logging
from datetime import datetime
from database.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def get_prompt_hash(prompt: str, mode: str) -> str:
    content = f"{mode}::{prompt}"
    return hashlib.sha256(content.encode()).hexdigest()


def find_cached_result(prompt_hash: str) -> str | None:
    """
    جستجو برای خروجی کش‌شده.
    اگر پیدا شد، متن خروجی را برمی‌گرداند.
    """
    try:
        supabase_admin = get_admin_client()
        res = (
            supabase_admin
            .table("generation_history")
            .select("output")
            .eq("prompt_hash", prompt_hash)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if res.data:
            logger.info(f"Cache hit for hash: {prompt_hash[:16]}...")
            return res.data[0]["output"]
        return None
    except Exception as e:
        logger.error(f"Cache lookup error: {e}")
        return None


def save_to_cache(
    user_id: str,
    prompt_hash: str,
    mode: str,
    brand_name: str,
    niche: str,
    output: str,
    model_used: str,
    credits_used: int
):
    try:
        supabase_admin = get_admin_client()
        supabase_admin.table("generation_history").insert({
            "user_id": user_id,
            "prompt_hash": prompt_hash,
            "mode": mode,
            "brand_name": brand_name,
            "niche": niche,
            "output": output,
            "model_used": model_used,
            "credits_used": credits_used,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Cache save error: {e}")


def get_user_history(user_id: str, limit: int = 10) -> list:
    try:
        supabase_admin = get_admin_client()
        res = (
            supabase_admin
            .table("generation_history")
            .select("id, mode, brand_name, niche, model_used, credits_used, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return []


def get_history_output(record_id: str, user_id: str) -> str | None:
    try:
        supabase_admin = get_admin_client()
        res = (
            supabase_admin
            .table("generation_history")
            .select("output")
            .eq("id", record_id)
            .eq("user_id", user_id)
            .execute()
        )
        return res.data[0]["output"] if res.data else None
    except Exception as e:
        logger.error(f"History output fetch error: {e}")
        return None