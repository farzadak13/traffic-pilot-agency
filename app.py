import os
import re
import logging
import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from datetime import date

from prompts import (
    INSTAGRAM_SYSTEM_INSTRUCTION,
    SEO_SYSTEM_INSTRUCTION,
    build_instagram_prompt,
    build_seo_prompt,
    build_fix_prompt,
)

# ── تنظیمات لاگ ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("ENVIRONMENT") == "local":
    os.environ["HTTP_PROXY"] = os.getenv("HTTP_PROXY", "")
    os.environ["HTTPS_PROXY"] = os.getenv("HTTPS_PROXY", "")

# ── پیکربندی صفحه ──
st.set_page_config(
    page_title="Traffic Pilot Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="auto",
)

# =============================================
# CSS
# =============================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

.stApp{
    background:#0f0f1a!important;
    color:#e2e8f0!important;
    font-family:'Inter','Tahoma',sans-serif!important;
    direction:rtl!important;
}
.stApp::before{
    content:'';position:fixed;top:0;left:0;width:100%;height:100%;
    background:
        radial-gradient(ellipse at 20% 50%,rgba(99,102,241,.08) 0%,transparent 50%),
        radial-gradient(ellipse at 80% 20%,rgba(168,85,247,.06) 0%,transparent 50%),
        radial-gradient(ellipse at 50% 80%,rgba(59,130,246,.05) 0%,transparent 50%);
    pointer-events:none;z-index:0;
}
.main .block-container{padding:2rem 3rem!important;max-width:1400px!important}

h1{
    font-size:2.2rem!important;font-weight:800!important;
    background:linear-gradient(135deg,#6366f1,#a855f7,#3b82f6)!important;
    -webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;
    background-clip:text!important;border-bottom:none!important;
    padding-bottom:0!important;letter-spacing:-.5px!important;
}
h2,h3{color:#c4b5fd!important;font-weight:600!important}
p,label,.stMarkdown{color:#94a3b8!important;line-height:1.7!important}

div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlock"]{
    background:rgba(255,255,255,.03)!important;
    border:1px solid rgba(255,255,255,.06)!important;
    border-radius:16px!important;backdrop-filter:blur(10px)!important;
}

section[data-testid="stSidebar"]{
    background:rgba(15,15,30,.95)!important;
    border-right:1px solid rgba(99,102,241,.2)!important;
    backdrop-filter:blur(20px)!important;
}
section[data-testid="stSidebar"] .block-container{padding:2rem 1.2rem!important}

div[data-baseweb="input"]>div,
div[data-baseweb="select"]>div,
div[data-baseweb="textarea"]>div{
    background:#1a1b26!important;
    border:1px solid rgba(255,255,255,.15)!important;
    border-radius:10px!important;transition:all .2s ease!important;
}
div[data-baseweb="input"]>div:focus-within,
div[data-baseweb="textarea"]>div:focus-within{
    border-color:rgba(99,102,241,.8)!important;
    box-shadow:0 0 0 2px rgba(99,102,241,.2)!important;
    background:#1e1e2f!important;
}
input,textarea,select{color:#fff!important;caret-color:#6366f1!important;background-color:transparent!important}
input::placeholder,textarea::placeholder{color:#64748b!important}

div[data-testid="InputInstructions"],
div[data-testid="stTextInputInstructions"]{
    display:none!important;visibility:hidden!important;opacity:0!important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label{
    color:#94a3b8!important;font-size:.85rem!important;font-weight:500!important;
    text-transform:uppercase!important;letter-spacing:.5px!important;margin-bottom:4px!important;
}

.stButton>button[kind="primary"],.stButton>button{
    background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;
    color:#fff!important;font-weight:600!important;font-size:.95rem!important;
    border:none!important;border-radius:12px!important;padding:.75rem 2rem!important;
    letter-spacing:.3px!important;transition:all .3s cubic-bezier(.4,0,.2,1)!important;
    box-shadow:0 4px 15px rgba(99,102,241,.3)!important;
    position:relative!important;overflow:hidden!important;
}
.stButton>button:hover{
    transform:translateY(-2px)!important;
    box-shadow:0 8px 25px rgba(99,102,241,.45)!important;
    background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;
}
.stButton>button:active{transform:translateY(0)!important}

.stDownloadButton>button{
    background:rgba(255,255,255,.05)!important;color:#94a3b8!important;
    border:1px solid rgba(255,255,255,.1)!important;border-radius:10px!important;
    font-weight:500!important;transition:all .2s ease!important;
}
.stDownloadButton>button:hover{
    background:rgba(99,102,241,.15)!important;
    border-color:rgba(99,102,241,.4)!important;
    color:#c4b5fd!important;transform:translateY(-1px)!important;
}

div[data-testid="stRadio"]>div{
    background:rgba(255,255,255,.03)!important;
    border:1px solid rgba(255,255,255,.06)!important;
    border-radius:12px!important;padding:.5rem!important;
    gap:.5rem!important;flex-direction:row!important;
}
div[data-testid="stRadio"] label{
    background:transparent!important;border-radius:8px!important;
    padding:.5rem 1rem!important;cursor:pointer!important;
    transition:all .2s!important;color:#64748b!important;font-weight:500!important;
}
div[data-testid="stRadio"] label:has(input:checked){
    background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;
    color:#fff!important;box-shadow:0 2px 8px rgba(99,102,241,.3)!important;
}

div[data-testid="stProgress"]>div>div{
    background:linear-gradient(90deg,#6366f1,#a855f7)!important;border-radius:99px!important;
}
div[data-testid="stProgress"]>div{
    background:rgba(255,255,255,.05)!important;border-radius:99px!important;height:6px!important;
}

hr{border-color:rgba(255,255,255,.06)!important;margin:1.5rem 0!important}

div[data-testid="stTabs"] button{
    color:#64748b!important;font-weight:500!important;
    border-radius:8px 8px 0 0!important;padding:.6rem 1.5rem!important;
    transition:all .2s!important;
}
div[data-testid="stTabs"] button[aria-selected="true"]{
    color:#6366f1!important;border-bottom:2px solid #6366f1!important;
    background:rgba(99,102,241,.05)!important;
}
div[data-testid="stTabs"] button:hover{
    color:#a5b4fc!important;background:rgba(99,102,241,.05)!important;
}

div[data-testid="stAlert"]{border-radius:12px!important;border:none!important;backdrop-filter:blur(10px)!important}
div[data-testid="stAlert"][data-baseweb="notification"]{
    background:rgba(99,102,241,.1)!important;border-left:3px solid #6366f1!important;
}
div[data-testid="stSpinner"]{color:#6366f1!important}

.stMarkdown h3{color:#a5b4fc!important;margin-top:1.5rem!important;font-weight:600!important}

table{border-collapse:collapse!important;width:100%!important;font-size:.875rem!important;border-radius:12px!important;overflow:hidden!important}
thead tr{background:linear-gradient(135deg,rgba(99,102,241,.3),rgba(168,85,247,.3))!important}
thead th{padding:12px 16px!important;text-align:right!important;color:#e2e8f0!important;font-weight:600!important;font-size:.8rem!important;text-transform:uppercase!important;letter-spacing:.5px!important;border:none!important}
tbody tr{background:rgba(255,255,255,.02)!important;border-bottom:1px solid rgba(255,255,255,.04)!important;transition:background .15s ease!important}
tbody tr:hover{background:rgba(99,102,241,.06)!important}
tbody td{padding:12px 16px!important;color:#cbd5e1!important;border:none!important;vertical-align:top!important;line-height:1.6!important}

ul[data-testid="stSelectboxVirtualDropdown"]{background:#1e1e35!important;border:1px solid rgba(99,102,241,.3)!important;border-radius:10px!important}
ul[data-testid="stSelectboxVirtualDropdown"] li{background-color:#1e1e35!important}
ul[data-testid="stSelectboxVirtualDropdown"] li *{color:#e2e8f0!important;background-color:transparent!important}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"]{background-color:rgba(99,102,241,.25)!important}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover *,
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] *{color:#fff!important}

#MainMenu,footer,header{visibility:hidden!important}

::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:rgba(255,255,255,.02)}
::-webkit-scrollbar-thumb{background:rgba(99,102,241,.4);border-radius:99px}
::-webkit-scrollbar-thumb:hover{background:rgba(99,102,241,.7)}

div[data-testid="metric-container"]{
    background:rgba(255,255,255,.03)!important;
    border:1px solid rgba(255,255,255,.07)!important;
    border-radius:12px!important;padding:1rem!important;
}
div[data-testid="metric-container"] label{color:#64748b!important;font-size:.8rem!important}
div[data-testid="metric-container"] div[data-testid="stMetricValue"]{color:#e2e8f0!important;font-weight:700!important}

@media(max-width:768px){
    .main .block-container{padding:1rem 1rem!important}
    h1{font-size:1.5rem!important}
    h2,h3{font-size:1.1rem!important}
    div[data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:.5rem!important}
    div[data-testid="stHorizontalBlock"]>div[data-testid="column"]{width:100%!important;flex:1 1 100%!important;min-width:100%!important}
    div[data-testid="stRadio"]>div{flex-direction:column!important}
    .stButton>button,.stDownloadButton>button{font-size:.85rem!important;padding:.65rem 1rem!important}
    table{display:block!important;overflow-x:auto!important;white-space:nowrap!important;font-size:.72rem!important;-webkit-overflow-scrolling:touch!important}
    thead th,tbody td{padding:8px 10px!important}
}
@media(max-width:480px){
    .main .block-container{padding:.75rem .6rem!important}
    h1{font-size:1.25rem!important}
    .stButton>button,.stDownloadButton>button{font-size:.8rem!important;padding:.6rem .8rem!important}
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================
# اتصال به سرویس‌ها
# =============================================
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    SERVICE_ROLE_KEY = st.secrets.get("SERVICE_ROLE_KEY")
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception as e:
    st.error("خطا در بارگذاری تنظیمات.")
    logger.error(f"Config error: {e}")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = (
    create_client(SUPABASE_URL, SERVICE_ROLE_KEY) if SERVICE_ROLE_KEY else supabase
)
genai.configure(api_key=GEMINI_API_KEY)

current_date = date.today().strftime("%Y-%m-%d")

if "user" not in st.session_state:
    st.session_state.user = None


# =============================================
# توابع کمکی
# =============================================
def get_user_profile(user_id: str) -> dict:
    try:
        res = (
            supabase_admin.table("user_profiles")
            .select("credits")
            .eq("id", user_id)
            .execute()
        )
        return res.data[0] if res.data else {"credits": 0}
    except Exception as e:
        logger.error(f"DB error: {e}")
        return {"credits": 0}


def deduct_credit(user_id: str, current_credits: int) -> bool:
    try:
        supabase_admin.table("user_profiles").update(
            {"credits": current_credits - 1}
        ).eq("id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Credit deduction error: {e}")
        return False


def refund_credit(user_id: str, credits_before: int):
    try:
        supabase_admin.table("user_profiles").update(
            {"credits": credits_before}
        ).eq("id", user_id).execute()
    except Exception as e:
        logger.error(f"Credit refund error: {e}")


# ── اعتبارسنجی خروجی اینستاگرام ──
def validate_instagram_output(
    content: str, total_budget: int, followers: int
) -> dict:
    errors = []
    warnings = []

    boost_budget = int(total_budget * 0.70)
    influencer_budget = int(total_budget * 0.30)

    # ۱. بررسی وجود جداول
    has_table1 = bool(re.search(r"جدول\s*[۱1]|تقویم.*روز", content))
    has_table2 = bool(re.search(r"جدول\s*[۲2]|استوری", content))
    has_table3 = bool(re.search(r"جدول\s*[۳3]|اینفلوئنسر", content))
    has_table4 = bool(re.search(r"جدول\s*[۴4]|بحران", content))

    if not has_table1:
        errors.append("جدول ۱ (تقویم ۷ روزه) پیدا نشد")
    if not has_table2:
        warnings.append("جدول ۲ (استوری) پیدا نشد")
    if not has_table3:
        errors.append("جدول ۳ (اینفلوئنسر) پیدا نشد")
    if not has_table4:
        warnings.append("جدول ۴ (بحران) پیدا نشد")

    # ۲. بررسی اعداد بودجه بوست
    budget_numbers = re.findall(
        r"([\d,٬۰-۹]+)\s*(?:تومان|تومن)", content
    )
    cleaned = []
    for b in budget_numbers:
        n = b.replace(",", "").replace("٬", "")
        n = (
            n.replace("۰", "0").replace("۱", "1").replace("۲", "2")
            .replace("۳", "3").replace("۴", "4").replace("۵", "5")
            .replace("۶", "6").replace("۷", "7").replace("۸", "8")
            .replace("۹", "9")
        )
        if n.isdigit():
            cleaned.append(int(n))

    if cleaned:
        found_boost = any(abs(v - boost_budget) < 50_000 for v in cleaned)
        found_inf = any(abs(v - influencer_budget) < 50_000 for v in cleaned)
        if not found_boost:
            errors.append(
                f"جمع بودجه بوست ({boost_budget:,}) در خروجی تطابق ندارد"
            )
        if not found_inf:
            errors.append(
                f"بودجه اینفلوئنسر ({influencer_budget:,}) در خروجی تطابق ندارد"
            )
    else:
        errors.append("هیچ عدد بودجه‌ای در خروجی یافت نشد")

    # ۳. بررسی CTA تعاملی
    cta_kw = ["کامنت", "سیو کن", "ذخیره", "تگ کن", "دایرکت", "بفرست"]
    if not any(kw in content for kw in cta_kw):
        warnings.append("هیچ CTA تعاملی (کامنت/سیو/تگ) پیدا نشد")

    # ۴. بررسی ردیف جمع کل
    if "جمع کل" not in content and "جمع" not in content:
        warnings.append("ردیف «جمع کل» در جدول ۱ وجود ندارد")

    # ۵. بررسی Hook کلیشه‌ای
    banned = ["بی‌نظیر", "فوق‌العاده", "درخشش", "تجربه‌ای لوکس"]
    for word in banned:
        if word in content:
            warnings.append(f"کلمه کلیشه‌ای «{word}» در خروجی وجود دارد")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": max(0, 100 - len(errors) * 25 - len(warnings) * 5),
    }


# =============================================
# صفحه لاگین
# =============================================
if not st.session_state.user:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown(
            """
            <div style='text-align:center;padding:3rem 0 2rem;'>
                <div style='font-size:3rem;margin-bottom:1rem;'>🚀</div>
                <h1 style='font-size:2rem!important;margin-bottom:.5rem;'>Traffic Pilot</h1>
                <p style='color:#475569;font-size:.95rem;'>
                    پلتفرم تدوین استراتژی محتوای داده‌محور
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["ورود به حساب", "ایجاد حساب"])

        with tab1:
            with st.form("login_form"):
                st.text_input(
                    "آدرس ایمیل", placeholder="name@company.com", key="li_email"
                )
                st.text_input(
                    "رمز عبور", type="password", placeholder="••••••••", key="li_pass"
                )
                st.write("")
                if st.form_submit_button("ورود به سیستم", use_container_width=True):
                    try:
                        res = supabase.auth.sign_in_with_password(
                            {
                                "email": st.session_state.li_email,
                                "password": st.session_state.li_pass,
                            }
                        )
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        logger.warning(f"Login failed: {e}")
                        st.error("ایمیل یا رمز عبور اشتباه است.")

        with tab2:
            with st.form("signup_form"):
                st.text_input(
                    "آدرس ایمیل", placeholder="name@company.com", key="su_email"
                )
                st.text_input(
                    "رمز عبور",
                    type="password",
                    placeholder="حداقل ۶ کاراکتر",
                    key="su_pass",
                )
                st.write("")
                if st.form_submit_button(
                    "ایجاد حساب رایگان", use_container_width=True
                ):
                    try:
                        supabase.auth.sign_up(
                            {
                                "email": st.session_state.su_email,
                                "password": st.session_state.su_pass,
                            }
                        )
                        st.success("✅ حساب ایجاد شد. لطفاً وارد شوید.")
                    except Exception as e:
                        logger.error(f"Signup error: {e}")
                        st.error("خطا در ثبت‌نام. ایمیل تکراری یا رمز کوتاه است.")

# =============================================
# داشبورد اصلی
# =============================================
else:
    user = st.session_state.user
    profile = get_user_profile(user.id)
    credits = profile.get("credits", 0)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(
            f"""
            <div style='text-align:center;padding:1.5rem 0 1rem;'>
                <div style='
                    width:56px;height:56px;
                    background:linear-gradient(135deg,#6366f1,#a855f7);
                    border-radius:50%;display:flex;align-items:center;
                    justify-content:center;margin:0 auto 12px;
                    font-size:1.5rem;box-shadow:0 4px 15px rgba(99,102,241,.4);
                '>🚀</div>
                <div style='font-weight:700;font-size:1.1rem;color:#e2e8f0;'>Traffic Pilot</div>
                <div style='font-size:.75rem;color:#475569;margin-top:2px;'>Agency Standard</div>
            </div>
            <hr style='border-color:rgba(255,255,255,.06);margin:.5rem 0 1.5rem;'/>
        """,
            unsafe_allow_html=True,
        )

        credit_color = (
            "#22c55e" if credits > 3 else "#f59e0b" if credits > 0 else "#ef4444"
        )
        st.markdown(
            f"""
            <div style='
                background:rgba(255,255,255,.03);
                border:1px solid rgba(255,255,255,.07);
                border-radius:14px;padding:1.2rem;margin-bottom:1rem;
            '>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:12px;'>
                    <div style='
                        width:32px;height:32px;background:rgba(99,102,241,.15);
                        border-radius:8px;display:flex;align-items:center;
                        justify-content:center;font-size:1rem;
                    '>👤</div>
                    <div>
                        <div style='font-size:.85rem;font-weight:600;color:#e2e8f0;'>
                            {user.email.split('@')[0]}
                        </div>
                        <div style='font-size:.72rem;color:#475569;'>{user.email}</div>
                    </div>
                </div>
                <div style='
                    background:rgba(255,255,255,.03);border-radius:10px;padding:12px;
                    display:flex;justify-content:space-between;align-items:center;
                '>
                    <div>
                        <div style='font-size:.72rem;color:#475569;margin-bottom:2px;'>
                            اعتبار باقی‌مانده
                        </div>
                        <div style='font-size:1.8rem;font-weight:800;color:{credit_color};line-height:1;'>
                            {credits}
                        </div>
                    </div>
                    <div style='
                        background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);
                        border-radius:8px;padding:6px 12px;font-size:.72rem;
                        color:#a5b4fc;font-weight:500;
                    '>استراتژیست</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.progress(min(credits / 10, 1.0))
        st.write("")

        if st.button("خروج از سیستم", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # ── Header ──
    st.markdown(
        """
        <div style='margin-bottom:2rem;'>
            <h1>تدوین مدیا پلن آژانسی</h1>
            <p style='color:#475569;margin-top:.5rem;font-size:.95rem;'>
                داده‌های واقعی کسب‌وکار را وارد کنید تا KPIها به صورت ریاضی محاسبه شوند
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Mode Selector ──
    mode = st.radio(
        "نوع خروجی:",
        ["📱 تقویم اینستاگرام", "🔍 کلاستر محتوایی سایت (SEO)"],
        horizontal=True,
    )
    st.write("")

    # ── فرم ورودی ──
    with st.container():
        st.markdown(
            """<div style='font-size:.8rem;font-weight:600;color:#475569;
            text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem;'>
            اطلاعات پایه برند</div>""",
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            brand_name = st.text_input("نام برند", placeholder="مثلاً: پاما")
        with c2:
            niche = st.text_input("حوزه فعالیت", placeholder="مثلاً: کفش چرم طبی")
        with c3:
            target_audience = st.text_input(
                "مخاطب هدف", placeholder="آقایان ۴۰ ساله کارمند"
            )

        st.write("")

        # ── فیلدهای اختصاصی هر مود ──
        if mode == "📱 تقویم اینستاگرام":
            st.markdown(
                """<div style='font-size:.8rem;font-weight:600;color:#475569;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem;'>
                📊 داده‌های استراتژیک اینستاگرام</div>""",
                unsafe_allow_html=True,
            )

            c4, c5, c6 = st.columns(3)
            with c4:
                current_followers = st.number_input(
                    "فالوور فعلی پیج", min_value=0, value=1500, step=100
                )
            with c5:
                total_budget = st.number_input(
                    "بودجه کل کمپین (تومان)",
                    min_value=0,
                    value=10_000_000,
                    step=1_000_000,
                )
            with c6:
                competitors = st.text_input(
                    "رقبای اصلی (پیج اینستاگرام)",
                    placeholder="@novincharm، @charm_mashhad",
                )

            st.write("")
            st.markdown(
                """<div style='font-size:.8rem;font-weight:600;color:#475569;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem;'>
                🎬 سبک تولید محتوا</div>""",
                unsafe_allow_html=True,
            )

            c7, c8, c9 = st.columns(3)
            with c7:
                admin_on_camera = st.selectbox(
                    "حضور جلوی دوربین",
                    [
                        "ادمین/مدیر کاملاً جلوی دوربین",
                        "ترکیبی (صداگذاری + کمی چهره)",
                        "فقط محصول (بدون چهره)",
                    ],
                )
            with c8:
                campaign_goal = st.selectbox(
                    "هدف اصلی کمپین",
                    [
                        "آگاهی و جذب فالوور (TOFU)",
                        "تعامل و داستان‌سرایی (MOFU)",
                        "فروش مستقیم (BOFU)",
                    ],
                )
            with c9:
                campaign_phase = st.selectbox(
                    "فاز کمپین",
                    [
                        "عادی / استمرار (Sustain)",
                        "تیزینگ (Teasing)",
                        "رونمایی / لانچ (Launch)",
                    ],
                )

            # متغیرهای SEO – None
            domain_authority = None
            seo_strategy = None
            monthly_traffic = None
            cms_platform = None

        else:  # SEO mode
            st.markdown(
                """<div style='font-size:.8rem;font-weight:600;color:#475569;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem;'>
                📊 داده‌های استراتژیک سئو</div>""",
                unsafe_allow_html=True,
            )

            c4, c5, c6 = st.columns(3)
            with c4:
                domain_authority = st.number_input(
                    "Domain Authority سایت", min_value=0, max_value=100, value=15
                )
            with c5:
                monthly_traffic = st.number_input(
                    "ترافیک ماهانه فعلی (بازدید)",
                    min_value=0,
                    value=500,
                    step=100,
                )
            with c6:
                competitors = st.text_input(
                    "رقبای اصلی (دامنه سایت)",
                    placeholder="novincharm.com، charm-mashhad.ir",
                )

            st.write("")
            st.markdown(
                """<div style='font-size:.8rem;font-weight:600;color:#475569;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem;'>
                🔍 تنظیمات استراتژی سئو</div>""",
                unsafe_allow_html=True,
            )

            c7, c8, c9 = st.columns(3)
            with c7:
                seo_strategy = st.selectbox(
                    "اولویت اصلی سئو",
                    [
                        "پوشش کلمات اطلاعاتی (Blog/Article)",
                        "پوشش کلمات فروشگاهی (Category/Product)",
                        "لینک‌سازی داخلی و رپورتاژ",
                    ],
                )
            with c8:
                campaign_goal = st.selectbox(
                    "هدف اصلی محتوا",
                    [
                        "افزایش ترافیک ارگانیک (TOFU)",
                        "جذب لید و مشتری (MOFU)",
                        "افزایش فروش مستقیم (BOFU)",
                    ],
                )
            with c9:
                cms_platform = st.selectbox(
                    "CMS سایت",
                    [
                        "وردپرس (WordPress)",
                        "شاپیفای (Shopify)",
                        "اختصاصی / سفارشی",
                    ],
                )

            # متغیرهای اینستاگرام – None
            current_followers = None
            total_budget = None
            admin_on_camera = None
            campaign_phase = None

    st.write("")

    generate_col, _ = st.columns([1, 3])
    with generate_col:
        generate = st.button("⚡ تولید پلن", use_container_width=True)

    # =============================================
    # منطق تولید
    # =============================================
    if generate:
        if credits <= 0:
            st.error("اعتبار شما به پایان رسیده است.")
        elif not brand_name or not niche:
            st.warning("نام برند و حوزه فعالیت الزامی است.")
        else:
            if not deduct_credit(user.id, credits):
                st.error("خطا در کسر اعتبار.")
            else:
                try:
                    # ── ساخت پرامپت ──
                    if mode == "📱 تقویم اینستاگرام":
                        system_instruction = INSTAGRAM_SYSTEM_INSTRUCTION
                        user_prompt = build_instagram_prompt(
                            current_date=current_date,
                            brand_name=brand_name,
                            niche=niche,
                            target_audience=target_audience,
                            competitors=competitors,
                            current_followers=current_followers,
                            total_budget=total_budget,
                            admin_on_camera=admin_on_camera,
                            campaign_goal=campaign_goal,
                            campaign_phase=campaign_phase,
                        )
                    else:
                        system_instruction = SEO_SYSTEM_INSTRUCTION
                        user_prompt = build_seo_prompt(
                            current_date=current_date,
                            brand_name=brand_name,
                            niche=niche,
                            target_audience=target_audience,
                            competitors=competitors,
                            domain_authority=domain_authority,
                            monthly_traffic=monthly_traffic,
                            seo_strategy=seo_strategy,
                            campaign_goal=campaign_goal,
                            cms_platform=cms_platform,
                        )

                    model = genai.GenerativeModel(
                        "gemini-2.5-flash",
                        system_instruction=system_instruction,
                    )

                    st.markdown(
                        """<div style='font-size:.8rem;font-weight:600;color:#6366f1;
                        text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem;'>
                        📊 خروجی آژانسی</div>""",
                        unsafe_allow_html=True,
                    )

                    output_placeholder = st.empty()

                    # ── تلاش اول ──
                    gen_config_main = genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=16384,
                        top_p=0.9,
                        top_k=40,
                    )

                    full_content = ""
                    with st.spinner("در حال تولید پلن …"):
                        stream = model.generate_content(
                            user_prompt,
                            stream=True,
                            generation_config=gen_config_main,
                        )
                        for chunk in stream:
                            if chunk.text:
                                full_content += chunk.text
                                output_placeholder.markdown(full_content)

                    if not full_content.strip():
                        raise ValueError("خروجی خالی از مدل دریافت شد.")

                    # ── اعتبارسنجی (فقط اینستاگرام) ──
                    if mode == "📱 تقویم اینستاگرام":
                        validation = validate_instagram_output(
                            full_content, total_budget, current_followers
                        )

                        # اگر خطای بحرانی: تلاش دوم
                        if not validation["is_valid"]:
                            st.warning(
                                "⚠️ خطا در بودجه/ساختار — در حال تصحیح خودکار …"
                            )

                            fix_prompt = build_fix_prompt(
                                errors=validation["errors"],
                                total_budget=total_budget,
                                followers=current_followers,
                            )

                            gen_config_fix = genai.types.GenerationConfig(
                                temperature=0.3,
                                max_output_tokens=8192,
                                top_p=0.85,
                            )

                            fix_content = ""
                            with st.spinner("تصحیح خودکار …"):
                                fix_stream = model.generate_content(
                                    fix_prompt,
                                    stream=True,
                                    generation_config=gen_config_fix,
                                )
                                for chunk in fix_stream:
                                    if chunk.text:
                                        fix_content += chunk.text

                            if fix_content.strip():
                                full_content += (
                                    "\n\n---\n### ✅ نسخه تصحیح‌شده:\n" + fix_content
                                )
                                output_placeholder.markdown(full_content)

                            # اعتبارسنجی مجدد
                            validation = validate_instagram_output(
                                full_content, total_budget, current_followers
                            )

                        # نمایش نتیجه
                        if validation["is_valid"]:
                            st.success(
                                f"✅ خروجی تأیید شد — امتیاز کیفیت: {validation['score']}/100"
                            )
                        else:
                            st.warning(
                                f"⚠️ خروجی با برخی ایرادات — امتیاز: {validation['score']}/100"
                            )

                        if validation["warnings"]:
                            for w in validation["warnings"]:
                                st.caption(f"💡 {w}")

                    else:
                        st.success("✅ خروجی SEO با موفقیت تولید شد")

                    # ── دکمه‌های دانلود ──
                    st.write("")
                    dl1, dl2, _ = st.columns([1, 1, 2])
                    with dl1:
                        st.download_button(
                            "📥 دانلود Markdown",
                            full_content,
                            f"{brand_name}_plan.md",
                            "text/markdown",
                            use_container_width=True,
                        )
                    with dl2:
                        st.download_button(
                            "📄 دانلود TXT",
                            full_content,
                            f"{brand_name}_plan.txt",
                            "text/plain",
                            use_container_width=True,
                        )

                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    refund_credit(user.id, credits)
                    st.error("خطا در ارتباط با سرور. اعتبار شما بازگردانده شد.")
