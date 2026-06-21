import logging
from database.supabase_client import get_admin_client

logger = logging.getLogger(__name__)


def get_user_profile(user_id: str) -> dict:
    try:
        supabase_admin = get_admin_client()
        res = (
            supabase_admin
            .table("user_profiles")
            .select("credits, plan, email")
            .eq("id", user_id)
            .execute()
        )
        return res.data[0] if res.data else {"credits": 0, "plan": "free"}
    except Exception as e:
        logger.error(f"DB error get_user_profile: {e}")
        return {"credits": 0, "plan": "free"}


def deduct_credit_atomic(user_id: str, amount: int = 1) -> dict:
    """
    کسر اتمیک اعتبار با استفاده از تابع SQL.
    در صورت race condition، اعتبار منفی نمی‌شود.
    """
    try:
        supabase_admin = get_admin_client()
        result = supabase_admin.rpc(
            "deduct_credit_atomic",
            {"user_uuid": user_id, "amount": amount}
        ).execute()

        return result.data if result.data else {
            "success": False,
            "error": "unknown"
        }
    except Exception as e:
        logger.error(f"Credit deduction error: {e}")
        return {"success": False, "error": str(e)}


def refund_credit(user_id: str, credits_before: int):
    try:
        supabase_admin = get_admin_client()
        supabase_admin.table("user_profiles").update(
            {"credits": credits_before, "updated_at": "NOW()"}
        ).eq("id", user_id).execute()
        logger.info(f"Credit refunded for {user_id}: {credits_before}")
    except Exception as e:
        logger.error(f"Credit refund error: {e}")