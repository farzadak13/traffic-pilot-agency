import os
import re
import json
import random
import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

from ai.prompts import (
    INSTAGRAM_SYSTEM_INSTRUCTION,
    SEO_SYSTEM_INSTRUCTION,
    build_instagram_prompt,
    build_instagram_repair_prompt,
    build_seo_prompt_main,
    build_seo_repair_prompt,
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
# CSS — نسخه تقویت‌شده با توکن‌های طراحی
# =============================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root{
    --bg-base:#0a0a13;
    --bg-base-2:#0c0c17;
    --surface:rgba(255,255,255,.03);
    --surface-strong:rgba(255,255,255,.05);
    --border-subtle:rgba(255,255,255,.07);
    --border-strong:rgba(255,255,255,.14);

    --accent-indigo:#6366f1;
    --accent-indigo-deep:#4f46e5;
    --accent-violet:#a855f7;
    --accent-cyan:#22d3ee;

    --text-primary:#e7e9f3;
    --text-muted:#94a3b8;
    --text-faint:#5b6478;

    --success:#22c55e;
    --warning:#f59e0b;
    --danger:#ef4444;

    --radius-lg:16px;
    --radius-md:12px;
    --radius-sm:8px;

    --font-body:'Vazirmatn','Inter','Tahoma',sans-serif;
    --font-data:'IBM Plex Mono','Inter',monospace;
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

.stApp{
    background:var(--bg-base)!important;
    color:var(--text-primary)!important;
    font-family:var(--font-body)!important;
    direction:rtl!important;
}
.stApp::before{
    content:'';position:fixed;top:0;left:0;width:100%;height:100%;
    background:
        radial-gradient(ellipse at 18% 50%,rgba(99,102,241,.10) 0%,transparent 52%),
        radial-gradient(ellipse at 82% 18%,rgba(168,85,247,.08) 0%,transparent 52%),
        radial-gradient(ellipse at 50% 85%,rgba(34,211,238,.05) 0%,transparent 52%);
    pointer-events:none;z-index:0;
}
.main .block-container{padding:2rem 3rem!important;max-width:1440px!important}

h1{
    font-size:2.25rem!important;font-weight:800!important;
    background:linear-gradient(135deg,var(--accent-indigo),var(--accent-violet),var(--accent-cyan))!important;
    -webkit-background-clip:text!important;-webkit-text-fill-color:transparent!important;
    background-clip:text!important;border-bottom:none!important;
    padding-bottom:0!important;letter-spacing:-.5px!important;
}
h2,h3{color:#c4b5fd!important;font-weight:700!important;font-family:var(--font-body)!important}
p,label,.stMarkdown{color:var(--text-muted)!important;line-height:1.75!important}

/* ── کارت‌های شیشه‌ای ── */
div[data-testid="stVerticalBlock"]>div[data-testid="stVerticalBlock"]{
    background:var(--surface)!important;
    border:1px solid var(--border-subtle)!important;
    border-radius:var(--radius-lg)!important;
    backdrop-filter:blur(10px)!important;
}

/* ── eyebrow / برچسب بخش (عنصر امضادار طرح) ── */
.tp-eyebrow{
    display:flex;align-items:center;gap:8px;
    font-size:.76rem;font-weight:700;color:var(--text-faint);
    text-transform:uppercase;letter-spacing:.07em;
    margin-bottom:.9rem;
}
.tp-eyebrow-dot{
    width:7px;height:7px;border-radius:50%;flex-shrink:0;
    background:var(--dot-color,var(--accent-indigo));
    box-shadow:0 0 9px var(--dot-color,var(--accent-indigo));
}

/* ── سایدبار ── */
section[data-testid="stSidebar"]{
    background:rgba(13,13,24,.96)!important;
    border-right:1px solid rgba(99,102,241,.2)!important;
    backdrop-filter:blur(20px)!important;
    transition:width .25s ease-in-out,min-width .25s ease-in-out!important;
}
section[data-testid="stSidebar"] .block-container{padding:2rem 1.2rem!important}
section[data-testid="stSidebar"][aria-expanded="false"]{
    width:0px!important;min-width:0px!important;
    overflow:hidden!important;visibility:hidden!important;
}
section[data-testid="stSidebar"][aria-expanded="false"] *{overflow:hidden!important}

/* ── ورودی‌ها ── */
div[data-baseweb="input"]>div,
div[data-baseweb="select"]>div,
div[data-baseweb="textarea"]>div{
    background:#15151f!important;
    border:1px solid var(--border-strong)!important;
    border-radius:var(--radius-sm)!important;transition:all .2s ease!important;
}
div[data-baseweb="input"]>div:focus-within,
div[data-baseweb="textarea"]>div:focus-within{
    border-color:rgba(99,102,241,.85)!important;
    box-shadow:0 0 0 3px rgba(99,102,241,.18)!important;
    background:#181826!important;
}
input,textarea,select{color:#fff!important;caret-color:var(--accent-indigo)!important;background-color:transparent!important;font-family:var(--font-body)!important}
input::placeholder,textarea::placeholder{color:var(--text-faint)!important}

div[data-testid="InputInstructions"],
div[data-testid="stTextInputInstructions"]{display:none!important;visibility:hidden!important;opacity:0!important}

div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label{
    color:var(--text-muted)!important;font-size:.83rem!important;font-weight:600!important;
    text-transform:uppercase!important;letter-spacing:.04em!important;margin-bottom:4px!important;
}

/* ── دکمه‌ها ── */
.stButton>button[kind="primary"],.stButton>button{
    background:linear-gradient(135deg,var(--accent-indigo),var(--accent-violet))!important;
    color:#fff!important;font-weight:700!important;font-size:.95rem!important;
    border:none!important;border-radius:var(--radius-md)!important;padding:.75rem 2rem!important;
    letter-spacing:.3px!important;transition:transform .2s ease,box-shadow .2s ease,background .2s ease!important;
    box-shadow:0 4px 18px rgba(99,102,241,.32)!important;
}
.stButton>button:hover{
    transform:translateY(-2px)!important;
    box-shadow:0 10px 28px rgba(99,102,241,.45)!important;
    background:linear-gradient(135deg,var(--accent-indigo-deep),#7c3aed)!important;
}
.stButton>button:active{transform:translateY(0)!important}

.stDownloadButton>button{
    background:var(--surface-strong)!important;color:var(--text-muted)!important;
    border:1px solid var(--border-strong)!important;border-radius:var(--radius-sm)!important;
    font-weight:600!important;transition:all .2s ease!important;
}
.stDownloadButton>button:hover{
    background:rgba(99,102,241,.15)!important;border-color:rgba(99,102,241,.4)!important;
    color:#c4b5fd!important;transform:translateY(-1px)!important;
}

/* ── رادیو ── */
div[data-testid="stRadio"]>div{
    background:var(--surface)!important;border:1px solid var(--border-subtle)!important;
    border-radius:var(--radius-md)!important;padding:.5rem!important;gap:.5rem!important;flex-direction:row!important;
}
div[data-testid="stRadio"] label{
    background:transparent!important;border-radius:var(--radius-sm)!important;padding:.5rem 1rem!important;
    cursor:pointer!important;transition:all .2s!important;color:var(--text-faint)!important;font-weight:600!important;
}
div[data-testid="stRadio"] label:has(input:checked){
    background:linear-gradient(135deg,var(--accent-indigo),var(--accent-violet))!important;
    color:#fff!important;box-shadow:0 2px 10px rgba(99,102,241,.32)!important;
}

/* ── پراگرس ── */
div[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,var(--accent-indigo),var(--accent-violet))!important;border-radius:99px!important}
div[data-testid="stProgress"]>div{background:var(--surface-strong)!important;border-radius:99px!important;height:6px!important}

hr{border-color:var(--border-subtle)!important;margin:1.5rem 0!important}

/* ── تب‌ها ── */
div[data-testid="stTabs"] button{color:var(--text-faint)!important;font-weight:600!important;border-radius:8px 8px 0 0!important;padding:.6rem 1.5rem!important;transition:all .2s!important}
div[data-testid="stTabs"] button[aria-selected="true"]{color:var(--accent-indigo)!important;border-bottom:2px solid var(--accent-indigo)!important;background:rgba(99,102,241,.05)!important}
div[data-testid="stTabs"] button:hover{color:#a5b4fc!important;background:rgba(99,102,241,.05)!important}

/* ── اکسپندر ── */
div[data-testid="stExpander"]{
    border:1px solid var(--border-subtle)!important;border-radius:var(--radius-lg)!important;
    background:var(--surface)!important;overflow:hidden!important;
}
div[data-testid="stExpander"] summary{font-weight:700!important;color:var(--text-primary)!important}

/* ── هشدارها ── */
div[data-testid="stAlert"]{border-radius:var(--radius-md)!important;border:none!important;backdrop-filter:blur(10px)!important}
div[data-testid="stAlert"][data-baseweb="notification"]{background:rgba(99,102,241,.1)!important;border-left:3px solid var(--accent-indigo)!important}
div[data-testid="stSpinner"]{color:var(--accent-indigo)!important}

.stMarkdown h3{color:#a5b4fc!important;margin-top:1.5rem!important;font-weight:700!important}

/* ── جدول‌ها ── */
table{border-collapse:collapse!important;width:100%!important;font-size:.875rem!important;border-radius:var(--radius-md)!important;overflow:hidden!important}
thead tr{background:linear-gradient(135deg,rgba(99,102,241,.3),rgba(168,85,247,.3))!important}
thead th{padding:12px 16px!important;text-align:right!important;color:var(--text-primary)!important;font-weight:700!important;font-size:.78rem!important;text-transform:uppercase!important;letter-spacing:.04em!important;border:none!important}
tbody tr{background:rgba(255,255,255,.02)!important;border-bottom:1px solid rgba(255,255,255,.04)!important;transition:background .15s ease!important}
tbody tr:hover{background:rgba(99,102,241,.07)!important}
tbody td{padding:12px 16px!important;color:#cbd5e1!important;border:none!important;vertical-align:top!important;line-height:1.65!important}

/* ── دیتافریم استریم‌لیت ── */
div[data-testid="stDataFrame"]{border-radius:var(--radius-md)!important;overflow:hidden!important;border:1px solid var(--border-subtle)!important}

/* ── دراپ‌داون سلکت‌باکس ── */
ul[data-testid="stSelectboxVirtualDropdown"]{background:#181826!important;border:1px solid rgba(99,102,241,.35)!important;border-radius:var(--radius-sm)!important}
ul[data-testid="stSelectboxVirtualDropdown"] li{background-color:#181826!important}
ul[data-testid="stSelectboxVirtualDropdown"] li *{color:var(--text-primary)!important;background-color:transparent!important}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"]{background-color:rgba(99,102,241,.25)!important}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover *,
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] *{color:#fff!important}

#MainMenu,footer,header{visibility:hidden!important}

::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:rgba(255,255,255,.02)}
::-webkit-scrollbar-thumb{background:rgba(99,102,241,.4);border-radius:99px}
::-webkit-scrollbar-thumb:hover{background:rgba(99,102,241,.7)}

/* ── کارت متریک (بودجه/Reach) با فونت دیتا ── */
div[data-testid="metric-container"]{
    background:var(--surface)!important;border:1px solid var(--border-subtle)!important;
    border-radius:var(--radius-md)!important;padding:1rem!important;
}
div[data-testid="metric-container"] label{color:var(--text-faint)!important;font-size:.78rem!important;font-weight:600!important}
div[data-testid="metric-container"] div[data-testid="stMetricValue"]{
    color:var(--text-primary)!important;font-weight:700!important;font-family:var(--font-data)!important;letter-spacing:-.02em!important;
}

/* ── دسترسی‌پذیری: فوکوس قابل‌مشاهده ── */
button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible,[tabindex]:focus-visible{
    outline:2px solid var(--accent-cyan)!important;outline-offset:2px!important;
}

/* ── احترام به کاهش حرکت ── */
@media (prefers-reduced-motion: reduce){
    *,*::before,*::after{
        animation-duration:.001ms!important;animation-iteration-count:1!important;
        transition-duration:.001ms!important;scroll-behavior:auto!important;
    }
}

/* ── ریسپانسیو موبایل ── */
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

TODAY = date.today()
CURRENT_DATE_STR = TODAY.strftime("%Y-%m-%d")

if "user" not in st.session_state:
    st.session_state.user = None


# =============================================
# ثابت‌های محاسباتی (قطعی، بدون دخالت مدل)
# =============================================
PERSIAN_WEEKDAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
PERSIAN_GREGORIAN_MONTHS = [
    "ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
    "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر",
]

FORMAT_CYCLE = ["ریلز", "کاروسل", "ریلز", "فید پست", "ریلز", "کاروسل", "ریلز"]
FORMAT_REACH_MULTIPLIER = {"ریلز": 3.2, "کاروسل": 1.5, "فید پست": 1.0}
FORMAT_BOOST_WEIGHT = {"ریلز": 1.5, "کاروسل": 1.1, "فید پست": 0.0}
CPM_TOMAN_PER_1000 = 30_000

KPI_POOL = {
    "آگاهی و جذب فالوور (TOFU)": ["Reach", "Impressions", "Follows"],
    "تعامل و داستان‌سرایی (MOFU)": ["Engagement", "Saves", "Shares"],
    "فروش مستقیم (BOFU)": ["Website Clicks", "DM/Lead", "Saves"],
}
DEFAULT_KPI_CYCLE = ["Reach", "Engagement", "Saves"]

BANNED_HOOK_WORDS = ["بی‌نظیر", "فوق‌العاده", "درخشش", "لوکس", "تجربه‌ای خاص"]


# =============================================
# توابع کمکی UI
# =============================================
def eyebrow(text: str, kind: str = "base") -> None:
    color_map = {
        "data": "var(--accent-cyan)",
        "creative": "var(--accent-violet)",
        "base": "var(--accent-indigo)",
    }
    color = color_map.get(kind, "var(--accent-indigo)")
    st.markdown(
        f"<div class='tp-eyebrow' style='--dot-color:{color};'>"
        f"<span class='tp-eyebrow-dot'></span>{text}</div>",
        unsafe_allow_html=True,
    )


# =============================================
# توابع کمکی دیتابیس
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


def refund_credit(user_id: str, credits_before: int) -> None:
    try:
        supabase_admin.table("user_profiles").update(
            {"credits": credits_before}
        ).eq("id", user_id).execute()
    except Exception as e:
        logger.error(f"Credit refund error: {e}")


# =============================================
# محاسبات قطعی تاریخ/بودجه/Reach
# =============================================
def persian_date_label(d: date) -> str:
    weekday = PERSIAN_WEEKDAYS[d.weekday()]
    month = PERSIAN_GREGORIAN_MONTHS[d.month - 1]
    return f"{weekday}، {d.day} {month} {d.year}"


def slugify(text: str) -> str:
    text = text or "campaign"
    ascii_chars = re.sub(r"[^a-zA-Z0-9]+", "", text)
    return ascii_chars.lower() if ascii_chars else "campaign"


def build_instagram_skeleton(
    start_date: date,
    brand_name: str,
    total_budget: int,
    current_followers: int,
    campaign_goal: str,
    products: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    کل بخش عددی (تاریخ، فرمت، KPI، UTM، بودجه بوست، Reach) اینجا و فقط اینجا
    با فرمول قطعی محاسبه می‌شود. مدل هیچ‌وقت این اعداد را حدس نمی‌زند.
    """
    kpi_cycle = KPI_POOL.get(campaign_goal, DEFAULT_KPI_CYCLE)

    boost_pool = int(total_budget * 0.60)
    influencer_budget = int(total_budget * 0.25)
    production_reserve = max(total_budget - boost_pool - influencer_budget, 0)

    weights = [FORMAT_BOOST_WEIGHT[FORMAT_CYCLE[i]] for i in range(7)]
    total_weight = sum(weights) or 1

    slug = slugify(brand_name)
    days = []
    for i in range(7):
        day_index = i + 1
        d = start_date + timedelta(days=i)
        fmt = FORMAT_CYCLE[i]
        kpi = kpi_cycle[i % len(kpi_cycle)]
        weight = weights[i]

        boost_budget = 0
        if weight > 0:
            raw_budget = boost_pool * (weight / total_weight)
            boost_budget = int(round(raw_budget, -4))  # رند به نزدیک‌ترین ۱۰ هزار تومان

        rng = random.Random(f"{slug}-{day_index}")
        jitter = rng.uniform(0.9, 1.18)
        organic_reach = int(current_followers * 0.12 * FORMAT_REACH_MULTIPLIER[fmt] * jitter)
        paid_reach = int(boost_budget / CPM_TOMAN_PER_1000 * 1000) if boost_budget else 0

        product = products[i % len(products)] if products else {"name": "نامشخص", "desc": ""}

        days.append(
            {
                "day_index": day_index,
                "date_label": persian_date_label(d),
                "format": fmt,
                "kpi": kpi,
                "utm": f"utm_source=instagram&utm_medium={'reel' if fmt == 'ریلز' else 'feed'}&utm_campaign={slug}_d{day_index}",
                "boost_budget": boost_budget,
                "reach_organic": organic_reach,
                "reach_paid": paid_reach,
                "featured_product": product.get("name", "نامشخص"),
                "featured_product_desc": product.get("desc", ""),
            }
        )

    story_days = []
    for i in range(3):
        d = start_date + timedelta(days=i)
        story_days.append(
            {
                "day_index": i + 1,
                "date_label": persian_date_label(d),
                "items": [{"time": "09:00"}, {"time": "14:00"}, {"time": "20:00"}],
            }
        )

    return {
        "days": days,
        "story_days": story_days,
        "total_budget": total_budget,
        "boost_pool": boost_pool,
        "influencer_budget": influencer_budget,
        "production_reserve": production_reserve,
    }


# =============================================
# اعتبارسنجی خروجی مدل (ساختاری، روی JSON پارس‌شده)
# =============================================
def validate_instagram_json(data: dict) -> dict:
    errors, warnings = [], []

    feed = data.get("feed_plan", [])
    if len(feed) != 7:
        errors.append(f"تعداد ردیف‌های feed_plan باید ۷ باشد، {len(feed)} دریافت شد")

    story = data.get("story_plan", [])
    if len(story) != 3:
        errors.append(f"تعداد روزهای story_plan باید ۳ باشد، {len(story)} دریافت شد")
    else:
        for sd in story:
            if len(sd.get("stories", [])) != 3:
                warnings.append(f"روز {sd.get('day_index')} استوری باید دقیقاً ۳ آیتم داشته باشد")

    brief = data.get("influencer_brief", {})
    if not brief.get("sample_dialogue"):
        warnings.append("دیالوگ نمونه اینفلوئنسر خالی است")

    crisis = data.get("crisis_matrix", [])
    if len(crisis) < 3:
        warnings.append("ماتریس بحران باید حداقل ۳ سناریو داشته باشد")

    hooks = [item.get("hook", "") for item in feed]
    ctas = [item.get("cta", "") for item in feed if item.get("cta")]
    for h in hooks:
        for w in BANNED_HOOK_WORDS:
            if w in h:
                warnings.append(f"کلمه کلیشه‌ای «{w}» در یک Hook دیده شد")
    if ctas and len(ctas) != len(set(ctas)):
        warnings.append("برخی CTAها در روزهای مختلف عیناً تکرار شده‌اند")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def validate_seo_json(data: dict) -> dict:
    errors, warnings = [], []

    tc = data.get("topic_cluster", [])
    if len(tc) != 5:
        errors.append(f"topic_cluster باید ۵ آیتم داشته باشد، {len(tc)} دریافت شد")

    cg = data.get("content_gap", [])
    if len(cg) != 3:
        warnings.append(f"content_gap باید ۳ آیتم داشته باشد، {len(cg)} دریافت شد")

    lb = data.get("link_building", [])
    if len(lb) != 5:
        warnings.append(f"link_building باید ۵ آیتم داشته باشد، {len(lb)} دریافت شد")

    cal = data.get("calendar", [])
    if len(cal) != 8:
        warnings.append(f"calendar باید ۸ آیتم داشته باشد، {len(cal)} دریافت شد")

    valid_diff = {"Low", "Med", "High"}
    for item in tc:
        if item.get("difficulty") not in valid_diff:
            warnings.append(f"مقدار difficulty نامعتبر: {item.get('difficulty')}")

    return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}


# =============================================
# ادغام اسکلت قطعی + خروجی خلاقانه مدل
# =============================================
def merge_instagram_output(skeleton: dict, data: dict) -> dict:
    feed_by_index = {item.get("day_index"): item for item in data.get("feed_plan", [])}
    merged_feed = []
    for day in skeleton["days"]:
        creative = feed_by_index.get(day["day_index"], {})
        merged_feed.append(
            {
                "روز/تاریخ": day["date_label"],
                "فرمت": day["format"],
                "هدف KPI": day["kpi"],
                "محصول کانونی": day["featured_product"],
                "Hook": creative.get("hook", ""),
                "ایده تصویربرداری": creative.get("shot_idea", ""),
                "CTA": creative.get("cta", ""),
                "UTM": day["utm"],
                "بودجه بوست (تومان)": f"{day['boost_budget']:,}" if day["boost_budget"] else "ارگانیک",
                "Reach ارگانیک": f"{day['reach_organic']:,}",
                "Reach پولی": f"{day['reach_paid']:,}" if day["reach_paid"] else "-",
            }
        )

    story_by_index = {item.get("day_index"): item for item in data.get("story_plan", [])}
    merged_story = []
    for day in skeleton["story_days"]:
        creative_day = story_by_index.get(day["day_index"], {})
        creative_stories = {s.get("story_index"): s for s in creative_day.get("stories", [])}
        for slot_i, slot in enumerate(day["items"], start=1):
            creative = creative_stories.get(slot_i, {})
            merged_story.append(
                {
                    "روز/تاریخ": day["date_label"],
                    "ساعت": slot["time"],
                    "سناریو": creative.get("scenario", ""),
                    "استیکر": creative.get("sticker", ""),
                }
            )

    return {"feed_rows": merged_feed, "story_rows": merged_story}


# =============================================
# تماس با مدل + پارس JSON + یک بار تلاش اصلاحی
# =============================================
def _clean_json_text(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"```$", "", raw).strip()
    return raw


def generate_json_with_repair(
    system_instruction: str,
    base_prompt: str,
    repair_builder,
    validator,
    gen_config,
) -> Dict[str, Any]:
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)

    def _call(prompt: str) -> str:
        full = ""
        stream = model.generate_content(prompt, stream=True, generation_config=gen_config)
        for chunk in stream:
            if chunk.text:
                full += chunk.text
        return full

    raw_output = _call(base_prompt)
    if not raw_output.strip():
        raise ValueError("خروجی خالی از مدل دریافت شد.")

    data: Optional[dict] = None
    parse_errors: List[str] = []
    warnings: List[str] = []

    try:
        data = json.loads(_clean_json_text(raw_output))
    except json.JSONDecodeError as e:
        parse_errors = [f"خطای پارس JSON: {e}"]

    if data is not None:
        result = validator(data)
        parse_errors = result["errors"]
        warnings = result["warnings"]

    if data is None or parse_errors:
        repair_prompt = repair_builder(base_prompt, raw_output, parse_errors)
        raw_output_2 = _call(repair_prompt)
        try:
            data_2 = json.loads(_clean_json_text(raw_output_2))
            result_2 = validator(data_2)
            data = data_2
            warnings = result_2["warnings"]
            parse_errors = result_2["errors"]
        except json.JSONDecodeError as e:
            if data is None:
                raise ValueError(f"خروجی مدل حتی بعد از تلاش مجدد JSON معتبر نبود: {e}")
            warnings = warnings + ["تلاش اصلاحی دوم هم ناموفق بود؛ نسخه اول (با چند خطای جزئی) نمایش داده می‌شود."]

    return {"data": data, "warnings": warnings, "errors": parse_errors, "raw": raw_output}


# =============================================
# خروجی Markdown قابل دانلود
# =============================================
def render_instagram_markdown(brand_name: str, niche: str, skeleton: dict, merged: dict, data: dict) -> str:
    lines = [f"# مدیا پلن اینستاگرام — {brand_name}", "", f"**حوزه فعالیت:** {niche}", ""]

    lines += [
        "## 💰 خلاصه بودجه",
        "",
        f"- بودجه کل کمپین: {skeleton['total_budget']:,} تومان",
        f"- بودجه بوست پست‌ها: {skeleton['boost_pool']:,} تومان",
        f"- بودجه اینفلوئنسر: {skeleton['influencer_budget']:,} تومان",
        f"- ذخیره تولید محتوا/احتیاط: {skeleton['production_reserve']:,} تومان",
        "",
        "## 🎬 تقویم فید و ریلز (۷ روز)",
        "",
    ]

    feed_rows = merged["feed_rows"]
    if feed_rows:
        headers = list(feed_rows[0].keys())
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "---|" * len(headers))
        for row in feed_rows:
            lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    lines.append("")

    lines += ["## 📱 استوری سریالی (۳ روز اول)", ""]
    story_rows = merged["story_rows"]
    if story_rows:
        headers2 = list(story_rows[0].keys())
        lines.append("| " + " | ".join(headers2) + " |")
        lines.append("|" + "---|" * len(headers2))
        for row in story_rows:
            lines.append("| " + " | ".join(str(row[h]) for h in headers2) + " |")
    lines.append("")

    brief = data.get("influencer_brief", {})
    lines += [
        "## 🤝 بریف میکرواینفلوئنسر",
        "",
        f"- رنج فالوور: {brief.get('follower_range', '-')}",
        f"- بودجه پیشنهادی: {skeleton['influencer_budget']:,} تومان",
        f"- ددلاین: {brief.get('deadline', '-')}",
        "",
        "**بایدها:**",
    ]
    for d in brief.get("dos", []):
        lines.append(f"- ✅ {d}")
    lines += ["", "**نبایدها:**"]
    for d in brief.get("donts", []):
        lines.append(f"- ❌ {d}")
    lines += ["", f"**دیالوگ پیشنهادی:** {brief.get('sample_dialogue', '-')}", ""]

    lines += ["## 🚨 ماتریس بحران", ""]
    crisis = data.get("crisis_matrix", [])
    if crisis:
        ch = ["نوع", "پاسخ عمومی", "پاسخ خصوصی", "ددلاین", "اقدام"]
        lines.append("| " + " | ".join(ch) + " |")
        lines.append("|" + "---|" * len(ch))
        for c in crisis:
            lines.append(
                "| "
                + " | ".join(
                    [
                        c.get("type", ""),
                        c.get("public_response", ""),
                        c.get("private_response", ""),
                        c.get("deadline", ""),
                        c.get("action", ""),
                    ]
                )
                + " |"
            )

    return "\n".join(lines)


def render_seo_markdown(brand_name: str, niche: str, data: dict) -> str:
    lines = [f"# کلاستر محتوایی سئو — {brand_name}", "", f"**حوزه فعالیت:** {niche}", ""]

    def _table(title: str, rows: List[dict]) -> List[str]:
        out = [f"## {title}", ""]
        if rows:
            headers = list(rows[0].keys())
            out.append("| " + " | ".join(headers) + " |")
            out.append("|" + "---|" * len(headers))
            for row in rows:
                out.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
        out.append("")
        return out

    lines += _table("📑 معماری Topic Cluster", data.get("topic_cluster", []))
    lines += _table("📝 Content Gap رقبا", data.get("content_gap", []))
    lines += _table("🔗 برنامه لینک‌سازی", data.get("link_building", []))
    lines += _table("📅 تقویم انتشار محتوا (۸ هفته)", data.get("calendar", []))

    return "\n".join(lines)


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
                st.text_input("آدرس ایمیل", placeholder="name@company.com", key="li_email")
                st.text_input("رمز عبور", type="password", placeholder="••••••••", key="li_pass")
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
                st.text_input("آدرس ایمیل", placeholder="name@company.com", key="su_email")
                st.text_input("رمز عبور", type="password", placeholder="حداقل ۶ کاراکتر", key="su_pass")
                st.write("")
                if st.form_submit_button("ایجاد حساب رایگان", use_container_width=True):
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

        credit_color = "#22c55e" if credits > 3 else "#f59e0b" if credits > 0 else "#ef4444"
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
                        <div style='font-size:1.8rem;font-weight:800;color:{credit_color};
                                    line-height:1;font-family:var(--font-data);'>
                            {credits}
                        </div>
                    </div>
                    <div style='
                        background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);
                        border-radius:8px;padding:6px 12px;font-size:.72rem;
                        color:#a5b4fc;font-weight:600;
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
                داده‌های واقعی کسب‌وکار را وارد کنید تا تاریخ، بودجه و Reach به‌صورت ریاضی
                محاسبه شوند — نه حدس مدل
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
        eyebrow("اطلاعات پایه برند", kind="base")

        c1, c2, c3 = st.columns(3)
        with c1:
            brand_name = st.text_input("نام برند", placeholder="مثلاً: پاما")
        with c2:
            niche = st.text_input("حوزه فعالیت", placeholder="مثلاً: کفش چرم طبی")
        with c3:
            target_audience = st.text_input("مخاطب هدف", placeholder="آقایان ۴۰ ساله کارمند")

        st.write("")

        # ══════════════════════════════════════
        # فیلدهای اختصاصی هر مود
        # ══════════════════════════════════════
        if mode == "📱 تقویم اینستاگرام":
            eyebrow("داده‌های استراتژیک اینستاگرام", kind="data")

            c4, c5, c6 = st.columns(3)
            with c4:
                current_followers = st.number_input(
                    "فالوور فعلی پیج", min_value=0, value=1500, step=100,
                    help="مبنای محاسبه Reach ارگانیک",
                )
            with c5:
                total_budget = st.number_input(
                    "بودجه کل کمپین (تومان)", min_value=0, value=10_000_000, step=1_000_000,
                    help="بین بوست پست‌ها، اینفلوئنسر و ذخیره تولید تقسیم می‌شود",
                )
            with c6:
                competitors = st.text_input("رقبای اصلی (پیج اینستاگرام)", placeholder="@novincharm، @charm_mashhad")

            st.write("")
            eyebrow("سبک تولید محتوا", kind="creative")

            c7, c8, c9 = st.columns(3)
            with c7:
                admin_on_camera = st.selectbox(
                    "حضور جلوی دوربین",
                    ["ادمین/مدیر کاملاً جلوی دوربین", "ترکیبی (صداگذاری + کمی چهره)", "فقط محصول (بدون چهره)"],
                )
            with c8:
                campaign_goal = st.selectbox(
                    "هدف اصلی کمپین",
                    ["آگاهی و جذب فالوور (TOFU)", "تعامل و داستان‌سرایی (MOFU)", "فروش مستقیم (BOFU)"],
                )
            with c9:
                campaign_phase = st.selectbox(
                    "فاز کمپین",
                    ["عادی / استمرار (Sustain)", "تیزینگ (Teasing)", "رونمایی / لانچ (Launch)"],
                )

            domain_authority = monthly_traffic = seo_strategy = cms_platform = None
            existing_pages = seed_keywords = main_offer_seo = None

            st.write("")
            with st.expander("🎯 اطلاعات تکمیلی برای دقت بالاتر (اختیاری ولی به‌شدت توصیه می‌شود)"):
                eyebrow("شناخت عمیق‌تر کسب‌وکار", kind="creative")

                fc1, fc2 = st.columns(2)
                with fc1:
                    city = st.text_input("شهر / لوکیشن فعالیت", placeholder="مثلاً: تهران، نیاوران")
                    brand_advantage = st.text_input(
                        "مزیت رقابتی اصلی برند", placeholder="مثلاً: تنها برند با گارانتی ۲ ساله"
                    )
                with fc2:
                    conversion_path = st.selectbox(
                        "مسیر اصلی فروش",
                        ["دایرکت اینستاگرام", "واتساپ", "سایت/فروشگاه آنلاین", "حضوری/تلفنی"],
                    )
                    pain_points = st.text_input(
                        "مهم‌ترین درد/سوال مشتریان (خلاصه)", placeholder="مثلاً: نگرانی از نامناسب بودن سایز"
                    )

                content_notes = st.text_area(
                    "محدودیت‌ها یا نکات اجرایی تولید محتوا",
                    placeholder="مثلاً: فقط با موبایل فیلم می‌گیریم، استودیو نداریم",
                    height=70,
                )

                st.write("")
                eyebrow("محصولات / خدمات کلیدی این هفته", kind="creative")
                num_products = st.number_input(
                    "چند محصول یا خدمت اصلی در تقویم این هفته معرفی شود؟",
                    min_value=1, max_value=5, value=1,
                )
                products: List[Dict[str, str]] = []
                for i in range(int(num_products)):
                    pc1, pc2 = st.columns([1, 2])
                    with pc1:
                        p_name = st.text_input(
                            f"نام محصول/خدمت {i + 1}", key=f"prod_name_{i}",
                            placeholder="مثلاً: کفش طبی مدل آرامش",
                        )
                    with pc2:
                        p_desc = st.text_input(
                            f"توضیح کوتاه محصول/خدمت {i + 1}", key=f"prod_desc_{i}",
                            placeholder="ویژگی یا مزیت اصلی همین محصول",
                        )
                    if p_name:
                        products.append({"name": p_name, "desc": p_desc})

        else:  # SEO mode
            eyebrow("داده‌های استراتژیک سئو", kind="data")

            c4, c5, c6 = st.columns(3)
            with c4:
                domain_authority = st.number_input("Domain Authority سایت", min_value=0, max_value=100, value=15)
            with c5:
                monthly_traffic = st.number_input("ترافیک ماهانه فعلی (بازدید)", min_value=0, value=500, step=100)
            with c6:
                competitors = st.text_input("رقبای اصلی (دامنه سایت)", placeholder="novincharm.com، charm-mashhad.ir")

            st.write("")
            eyebrow("تنظیمات استراتژی سئو", kind="creative")

            c7, c8, c9 = st.columns(3)
            with c7:
                seo_strategy = st.selectbox(
                    "اولویت اصلی سئو",
                    ["پوشش کلمات اطلاعاتی (Blog/Article)", "پوشش کلمات فروشگاهی (Category/Product)", "لینک‌سازی داخلی و رپورتاژ"],
                )
            with c8:
                campaign_goal = st.selectbox(
                    "هدف اصلی محتوا",
                    ["افزایش ترافیک ارگانیک (TOFU)", "جذب لید و مشتری (MOFU)", "افزایش فروش مستقیم (BOFU)"],
                )
            with c9:
                cms_platform = st.selectbox("CMS سایت", ["وردپرس (WordPress)", "شاپیفای (Shopify)", "اختصاصی / سفارشی"])

            current_followers = total_budget = admin_on_camera = campaign_phase = None
            products = []

            st.write("")
            with st.expander("🎯 اطلاعات تکمیلی برای دقت بالاتر (اختیاری ولی به‌شدت توصیه می‌شود)"):
                eyebrow("شناخت عمیق‌تر کسب‌وکار", kind="creative")

                fc1, fc2 = st.columns(2)
                with fc1:
                    city = st.text_input("شهر / لوکیشن فعالیت", placeholder="مثلاً: تهران")
                    main_offer_seo = st.text_input("محصول/خدمت اصلی سایت", placeholder="مثلاً: فروش آنلاین کفش طبی")
                with fc2:
                    brand_advantage = st.text_input("مزیت رقابتی اصلی برند", placeholder="مثلاً: تنها فروشگاه با ارسال رایگان سراسری")
                    pain_points = st.text_input("مهم‌ترین درد/سوال مشتریان", placeholder="مثلاً: نگرانی از نامناسب بودن سایز")

                ec1, ec2 = st.columns(2)
                with ec1:
                    existing_pages = st.text_area(
                        "صفحات/دسته‌بندی‌های فعلی سایت", placeholder="هر مورد را با خط جدید بنویسید...", height=70
                    )
                with ec2:
                    seed_keywords = st.text_area(
                        "Seed Keywords (در صورت وجود)", placeholder="هر کلمه را با خط جدید بنویسید...", height=70
                    )

                conversion_path = None
                content_notes = None

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
                    gen_config_main = genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=16384,
                        top_p=0.9,
                        top_k=40,
                    )

                    # ── اینستاگرام ──
                    if mode == "📱 تقویم اینستاگرام":
                        effective_products = products if products else [{"name": niche, "desc": ""}]

                        skeleton = build_instagram_skeleton(
                            start_date=TODAY,
                            brand_name=brand_name,
                            total_budget=int(total_budget or 0),
                            current_followers=int(current_followers or 0),
                            campaign_goal=campaign_goal,
                            products=effective_products,
                        )

                        base_prompt = build_instagram_prompt(
                            current_date=CURRENT_DATE_STR,
                            brand_name=brand_name,
                            niche=niche,
                            target_audience=target_audience,
                            competitors=competitors,
                            current_followers=int(current_followers or 0),
                            admin_on_camera=admin_on_camera,
                            campaign_goal=campaign_goal,
                            campaign_phase=campaign_phase,
                            skeleton=skeleton,
                            city=city,
                            brand_advantage=brand_advantage,
                            pain_points=pain_points,
                            conversion_path=conversion_path,
                            content_notes=content_notes,
                            products=effective_products,
                        )

                        with st.spinner("در حال تولید پلن …"):
                            result = generate_json_with_repair(
                                system_instruction=INSTAGRAM_SYSTEM_INSTRUCTION,
                                base_prompt=base_prompt,
                                repair_builder=build_instagram_repair_prompt,
                                validator=validate_instagram_json,
                                gen_config=gen_config_main,
                            )

                        data = result["data"]
                        merged = merge_instagram_output(skeleton, data)

                        st.markdown("## 💰 خلاصه بودجه")
                        m1, m2, m3, m4 = st.columns(4)
                        with m1:
                            st.metric("بودجه کل", f"{skeleton['total_budget']:,} ت")
                        with m2:
                            st.metric("بوست پست‌ها", f"{skeleton['boost_pool']:,} ت")
                        with m3:
                            st.metric("اینفلوئنسر", f"{skeleton['influencer_budget']:,} ت")
                        with m4:
                            st.metric("ذخیره تولید", f"{skeleton['production_reserve']:,} ت")

                        st.markdown("## 📅 تقویم ۷ روزه محتوا")
                        st.dataframe(merged["feed_rows"], use_container_width=True, hide_index=True)

                        st.markdown("## 📸 استوری‌ها (۳ روز اول)")
                        st.dataframe(merged["story_rows"], use_container_width=True, hide_index=True)

                        st.markdown("## 🤝 بریف میکرواینفلوئنسر")
                        brief = data.get("influencer_brief", {})
                        if brief:
                            bcol1, bcol2 = st.columns(2)
                            with bcol1:
                                st.markdown(f"**رنج فالوور:** {brief.get('follower_range', '')}")
                                st.markdown(f"**بودجه پیشنهادی:** {skeleton['influencer_budget']:,} تومان")
                                st.markdown(f"**ددلاین:** {brief.get('deadline', '')}")
                                st.markdown("**بایدها:**")
                                for d in brief.get("dos", []):
                                    st.markdown(f"✅ {d}")
                            with bcol2:
                                st.markdown("**نبایدها:**")
                                for d in brief.get("donts", []):
                                    st.markdown(f"❌ {d}")
                                st.markdown("**دیالوگ نمونه:**")
                                st.info(brief.get("sample_dialogue", ""))

                        st.markdown("## 🚨 ماتریس بحران")
                        crisis = data.get("crisis_matrix", [])
                        if crisis:
                            crisis_rows = [
                                {
                                    "نوع": c.get("type", ""),
                                    "پاسخ عمومی": c.get("public_response", ""),
                                    "پاسخ خصوصی": c.get("private_response", ""),
                                    "ددلاین": c.get("deadline", ""),
                                    "اقدام": c.get("action", ""),
                                }
                                for c in crisis
                            ]
                            st.dataframe(crisis_rows, use_container_width=True, hide_index=True)

                        if result["warnings"]:
                            with st.expander(f"⚠️ {len(result['warnings'])} نکته برای بازبینی"):
                                for w in result["warnings"]:
                                    st.warning(w)

                        st.success("✅ تقویم اینستاگرام با موفقیت تولید شد")

                        full_export = {
                            "skeleton": skeleton,
                            "creative": data,
                            "merged": merged,
                        }
                        md_text = render_instagram_markdown(brand_name, niche, skeleton, merged, data)

                        st.write("")
                        dl1, dl2, _ = st.columns([1, 1, 2])
                        with dl1:
                            st.download_button(
                                "📥 دانلود JSON",
                                json.dumps(full_export, ensure_ascii=False, indent=2),
                                f"{brand_name}_plan.json",
                                "application/json",
                                use_container_width=True,
                            )
                        with dl2:
                            st.download_button(
                                "📄 دانلود Markdown",
                                md_text,
                                f"{brand_name}_plan.md",
                                "text/markdown",
                                use_container_width=True,
                            )

                    # ── SEO ──
                    else:
                        base_prompt = build_seo_prompt_main(
                            current_date=CURRENT_DATE_STR,
                            brand_name=brand_name,
                            niche=niche,
                            target_audience=target_audience,
                            competitors=competitors,
                            domain_authority=int(domain_authority or 0),
                            monthly_traffic=int(monthly_traffic or 0),
                            seo_strategy=seo_strategy,
                            campaign_goal=campaign_goal,
                            cms_platform=cms_platform,
                            city=city,
                            main_offer=main_offer_seo,
                            brand_advantage=brand_advantage,
                            pain_points=pain_points,
                            existing_pages=existing_pages,
                            seed_keywords=seed_keywords,
                        )

                        with st.spinner("در حال تولید پلن …"):
                            result = generate_json_with_repair(
                                system_instruction=SEO_SYSTEM_INSTRUCTION,
                                base_prompt=base_prompt,
                                repair_builder=build_seo_repair_prompt,
                                validator=validate_seo_json,
                                gen_config=gen_config_main,
                            )

                        data = result["data"]

                        st.markdown("## 🔍 Topic Cluster")
                        cluster = data.get("topic_cluster", [])
                        if cluster:
                            cluster_rows = [
                                {
                                    "نوع صفحه": item.get("page_type", ""),
                                    "H1": item.get("h1", ""),
                                    "کلمه کلیدی": item.get("primary_keyword", ""),
                                    "Intent": item.get("intent", ""),
                                    "سختی": item.get("difficulty", ""),
                                }
                                for item in cluster
                            ]
                            st.dataframe(cluster_rows, use_container_width=True, hide_index=True)

                        st.markdown("## 📊 Content Gap")
                        gap = data.get("content_gap", [])
                        if gap:
                            gap_rows = [
                                {
                                    "رقیب": item.get("competitor", ""),
                                    "محتوای موجود": item.get("existing_content", ""),
                                    "ضعف": item.get("weakness", ""),
                                    "استراتژی ما": item.get("our_strategy", ""),
                                }
                                for item in gap
                            ]
                            st.dataframe(gap_rows, use_container_width=True, hide_index=True)

                        st.markdown("## 🔗 Link Building")
                        links = data.get("link_building", [])
                        if links:
                            link_rows = [
                                {
                                    "نوع لینک": item.get("link_type", ""),
                                    "منبع": item.get("source", ""),
                                    "Anchor Text": item.get("anchor_text", ""),
                                    "نوع Follow": item.get("follow_type", ""),
                                    "اولویت": item.get("priority", ""),
                                }
                                for item in links
                            ]
                            st.dataframe(link_rows, use_container_width=True, hide_index=True)

                        st.markdown("## 📅 تقویم محتوا (۸ هفته)")
                        calendar = data.get("calendar", [])
                        if calendar:
                            cal_rows = [
                                {
                                    "هفته": item.get("week", ""),
                                    "عنوان": item.get("title", ""),
                                    "کلمه کلیدی": item.get("keyword", ""),
                                    "نوع صفحه": item.get("page_type", ""),
                                    "هدف": item.get("goal", ""),
                                }
                                for item in calendar
                            ]
                            st.dataframe(cal_rows, use_container_width=True, hide_index=True)

                        if result["warnings"]:
                            with st.expander(f"⚠️ {len(result['warnings'])} نکته برای بازبینی"):
                                for w in result["warnings"]:
                                    st.warning(w)

                        st.success("✅ کلاستر SEO با موفقیت تولید شد")

                        md_text = render_seo_markdown(brand_name, niche, data)

                        st.write("")
                        dl1, dl2, _ = st.columns([1, 1, 2])
                        with dl1:
                            st.download_button(
                                "📥 دانلود JSON",
                                json.dumps(data, ensure_ascii=False, indent=2),
                                f"{brand_name}_seo.json",
                                "application/json",
                                use_container_width=True,
                            )
                        with dl2:
                            st.download_button(
                                "📄 دانلود Markdown",
                                md_text,
                                f"{brand_name}_seo.md",
                                "text/markdown",
                                use_container_width=True,
                            )

                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    refund_credit(user.id, credits)
                    st.error(f"خطا در ارتباط با سرور: {e}\nاعتبار شما بازگردانده شد.")
