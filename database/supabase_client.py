import streamlit as st
from supabase import create_client, Client

_client: Client | None = None
_admin_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    return _client


def get_admin_client() -> Client:
    global _admin_client
    if _admin_client is None:
        service_key = st.secrets.get("SERVICE_ROLE_KEY")
        url = st.secrets["SUPABASE_URL"]
        _admin_client = create_client(
            url,
            service_key if service_key else st.secrets["SUPABASE_KEY"]
        )
    return _admin_client