import logging
import streamlit as st
from database.supabase_client import get_client

logger = logging.getLogger(__name__)


def login(email: str, password: str) -> bool:
    try:
        supabase = get_client()
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = res.user
        return True
    except Exception as e:
        logger.warning(f"Login failed for {email}: {e}")
        return False


def signup(email: str, password: str) -> bool:
    try:
        supabase = get_client()
        supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return True
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return False


def logout():
    st.session_state.user = None