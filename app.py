import os
import logging
import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from datetime import date

# --- تنظیمات ---
current_date = date.today().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("ENVIRONMENT") == "local":
    os.environ["HTTP_PROXY"] = os.getenv("HTTP_PROXY", "")
    os.environ["HTTPS_PROXY"] = os.getenv("HTTPS_PROXY", "")

# --- پیکربندی صفحه ---
st.set_page_config(
    page_title="Traffic Pilot Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="auto"
)

# =============================================
# CSS
# =============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background: #0f0f1a !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', 'Tahoma', sans-serif !important;
    direction: rtl !important;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(168,85,247,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, rgba(59,130,246,0.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

.main .block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px !important;
}

h1 {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #6366f1, #a855f7, #3b82f6) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    border-bottom: none !important;
    padding-bottom: 0 !important;
    letter-spacing: -0.5px !important;
}

h2, h3 {
    color: #c4b5fd !important;
    font-weight: 600 !important;
}

p, label, .stMarkdown {
    color: #94a3b8 !important;
    line-height: 1.7 !important;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px) !important;
}

section[data-testid="stSidebar"] {
    background: rgba(15,15,30,0.95) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
    backdrop-filter: blur(20px) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.2rem !important;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background: #1a1b26 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: rgba(99,102,241,0.8) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
    background: #1e1e2f !important;
}

input, textarea, select {
    color: #ffffff !important;
    caret-color: #6366f1 !important;
    background-color: transparent !important;
}

input::placeholder, textarea::placeholder {
    color: #64748b !important;
}

div[data-testid="InputInstructions"],
div[data-testid="stTextInputInstructions"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 4px !important;
}

.stButton > button[kind="primary"],
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.45) !important;
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

.stDownloadButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover {
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #c4b5fd !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stRadio"] > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
    gap: 0.5rem !important;
    flex-direction: row !important;
}

div[data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    color: #64748b !important;
    font-weight: 500 !important;
}

div[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3) !important;
}

div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    border-radius: 99px !important;
}

div[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 99px !important;
    height: 6px !important;
}

hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 1.5rem 0 !important;
}

div[data-testid="stTabs"] button {
    color: #64748b !important;
    font-weight: 500 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #6366f1 !important;
    border-bottom: 2px solid #6366f1 !important;
    background: rgba(99,102,241,0.05) !important;
}

div[data-testid="stTabs"] button:hover {
    color: #a5b4fc !important;
    background: rgba(99,102,241,0.05) !important;
}

div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
    backdrop-filter: blur(10px) !important;
}

div[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(99,102,241,0.1) !important;
    border-left: 3px solid #6366f1 !important;
}

div[data-testid="stSpinner"] {
    color: #6366f1 !important;
}

.stMarkdown h3 {
    color: #a5b4fc !important;
    margin-top: 1.5rem !important;
    font-weight: 600 !important;
}

table {
    border-collapse: collapse !important;
    width: 100% !important;
    font-size: 0.875rem !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

thead tr {
    background: linear-gradient(135deg,
        rgba(99,102,241,0.3),
        rgba(168,85,247,0.3)) !important;
}

thead th {
    padding: 12px 16px !important;
    text-align: right !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    border: none !important;
}

tbody tr {
    background: rgba(255,255,255,0.02) !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
    transition: background 0.15s ease !important;
}

tbody tr:hover {
    background: rgba(99,102,241,0.06) !important;
}

tbody td {
    padding: 12px 16px !important;
    color: #cbd5e1 !important;
    border: none !important;
    vertical-align: top !important;
    line-height: 1.6 !important;
}

ul[data-testid="stSelectboxVirtualDropdown"] {
    background: #1e1e35 !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
}

ul[data-testid="stSelectboxVirtualDropdown"] li {
    background-color: #1e1e35 !important;
}

ul[data-testid="stSelectboxVirtualDropdown"] li * {
    color: #e2e8f0 !important;
    background-color: transparent !important;
}

ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] {
    background-color: rgba(99,102,241,0.25) !important;
}

ul[data-testid="stSelectboxVirtualDropdown"] li:hover *,
ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] * {
    color: #ffffff !important;
}

#MainMenu, footer, header { visibility: hidden !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: rgba(99,102,241,0.4);
    border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.7); }

.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(99,102,241,0.2);
}

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

div[data-testid="metric-container"] label {
    color: #64748b !important;
    font-size: 0.8rem !important;
}

div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}

@media (max-width: 768px) {
    .main .block-container { padding: 1rem 1rem !important; }
    h1 { font-size: 1.5rem !important; }
    h2, h3 { font-size: 1.1rem !important; }
    div[data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: 0.5rem !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
    }
    div[data-testid="stRadio"] > div { flex-direction: column !important; }
    .stButton > button, .stDownloadButton > button {
        font-size: 0.85rem !important; padding: 0.65rem 1rem !important;
    }
    table {
        display: block !important; overflow-x: auto !important;
        white-space: nowrap !important; font-size: 0.72rem !important;
        -webkit-overflow-scrolling: touch !important;
    }
    thead th, tbody td { padding: 8px 10px !important; }
}

@media (max-width: 480px) {
    .main .block-container { padding: 0.75rem 0.6rem !important; }
    h1 { font-size: 1.25rem !important; }
    .stButton > button, .stDownloadButton > button {
        font-size: 0.8rem !important; padding: 0.6rem 0.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --- اتصال به سرویس‌ها ---
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
supabase_admin: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY) if SERVICE_ROLE_KEY else supabase
genai.configure(api_key=GEMINI_API_KEY)

# --- import validators بعد از اتصال به سرویس‌ها ---
try:
    from core.validators import validate_budget, validate_reach
    VALIDATORS_AVAILABLE = True
except ImportError:
    logger.warning("core/validators.py پیدا نشد. اعتبارسنجی غیرفعال است.")
    VALIDATORS_AVAILABLE = False

if 'user' not in st.session_state:
    st.session_state.user = None

# =============================================
# System Instructions
# =============================================

INSTAGRAM_SYSTEM_INSTRUCTION = """
نقش تو: یک Senior Social Media Strategist و Copywriter بومی ایرانی هستی که سال‌ها در آژانس‌های
دیجیتال مارکتینگ تهران کار کرده. تو متن تیزر تلویزیونی یا بیلبورد نمی‌نویسی؛ تو می‌دونی که کاربر
اینستاگرام در کسری از ثانیه تصمیم می‌گیره اسکرول کنه یا بمونه.

### قانون ۱ — ممنوعیت لحن تبلیغاتی کلیشه‌ای
استفاده از این کلمات و الگوها مطلقاً ممنوع است: "بی‌نظیر"، "فوق‌العاده"، "عاشقانه"،
"درخشش"، "یک بیانیه است"، "تجربه‌ای لوکس"، "کیفیت بی‌نظیر"، یا هر جمله‌ای که شبیه گوینده
تیزر تلویزیونی باشد.

### قانون ۲ — قلاب (Hook) یعنی شکستن باور یا لمس درد، نه توصیف محصول
هر Hook باید روی یکی از این‌ها بنا شود:
- شکستن یک باور غلط رایج
- یک درد یا مشکل ملموس روزمره مخاطب
- یک سوال چالشی
- یک فکت یا آمار غافلگیرکننده

### قانون ۳ — لحن محاوره‌ای و صمیمی
جملات باید طوری نوشته شوند که انگار یک آدم واقعی با مخاطب حرف می‌زند.

### قانون ۴ — CTA مدرن و اتوماسیون‌محور
حداقل نیمی از CTAها باید از تکنیک‌های تعامل/اتوماسیون استفاده کنند.

### قانون ۵ — منطق محاسبه داده
- ریلز: حداقل ۳ برابر Reach ارگانیک پست معمولی
- کاروسل: حدود ۱.۵ برابر پست تک‌عکسی
- Reach پولی = (بودجه بوست ÷ ۳۰,۰۰۰) × ۱,۰۰۰
- هیچ دو روزی Reach یکسان نداشته باشند

### قانون ۶ — بریف اینفلوئنسر
دیالوگ پیشنهادی باید طبیعی و نیتیو باشد.

### قانون ۷ — احترام حرفه‌ای به رقبا
هرگز رقبا را تخریب نکن.

### قانون ۸ — پیوستگی تاریخ بین جداول
استوری‌ها باید دقیقاً همان ۳ روز اول جدول تقویم را پوشش دهند.

### قانون ۹ — فرمت خروجی
اولین کاراکتر خروجی باید "###" باشد. فقط جداول مارک‌داون.
"""

SEO_SYSTEM_INSTRUCTION = """
نقش تو: یک Senior SEO Content Strategist ایرانی هستی که بر اساس تکنیک Pillar-Cluster کار می‌کند.

قوانین:
- از کلمات کلیدی و عناوین کلیشه‌ای پرهیز کن.
- هرگز رقبا را تخریب نکن.
- سختی کلمه کلیدی را با توجه به DA سایت واقع‌بینانه تخمین بزن.
- اولین کاراکتر خروجی باید "###" باشد. فقط جداول مارک‌داون.
"""

# =============================================
# Helper Functions
# =============================================

def get_user_profile(user_id: str) -> dict:
    try:
        res = supabase_admin.table("user_profiles")\
            .select("credits")\
            .eq("id", user_id)\
            .execute()
        return res.data[0] if res.data else {"credits": 0}
    except Exception as e:
        logger.error(f"DB error: {e}")
        return {"credits": 0}

def deduct_credit(user_id: str, current_credits: int) -> bool:
    try:
        supabase_admin.table("user_profiles")\
            .update({"credits": current_credits - 1})\
            .eq("id", user_id)\
            .execute()
        return True
    except Exception as e:
        logger.error(f"Credit deduction error: {e}")
        return False

def refund_credit(user_id: str, credits_before: int):
    try:
        supabase_admin.table("user_profiles")\
            .update({"credits": credits_before})\
            .eq("id", user_id)\
            .execute()
    except Exception as e:
        logger.error(f"Credit refund error: {e}")

def build_instagram_prompt(
    current_date, brand_name, niche, target_audience,
    competitors, current_followers, total_budget,
    admin_on_camera, campaign_goal, campaign_phase
) -> str:
    influencer_budget = int(total_budget * 0.30)
    boost_budget = total_budget - influencer_budget

    return f"""
داده‌های این کمپین:
- تاریخ شروع: {current_date}
- برند: {brand_name}
- حوزه فعالیت: {niche}
- مخاطب هدف: {target_audience or "بر اساس حوزه فعالیت حدس بزن"}
- رقبای اصلی: {competitors or "نامشخص"}
- فالوور فعلی پیج: {current_followers:,}
- بودجه کل کمپین: {total_budget:,} تومان
- سبک حضور جلوی دوربین: {admin_on_camera}
- هدف اصلی کمپین: {campaign_goal}
- فاز کمپین: {campaign_phase}

═══════════════════════════════════
قوانین اجباری بودجه (باید دقیقاً رعایت شود):
═══════════════════════════════════

بودجه کل: {total_budget:,} تومان
سهم اینفلوئنسر (جدول 3): {influencer_budget:,} تومان (۳۰٪)
سهم بوست پست‌ها (جدول 1): {boost_budget:,} تومان (۷۰٪)

قانون ۱: ستون "بودجه بوست" برای تمام ۷ ردیف جدول ۱ باید عدد صریح داشته باشد. هیچ سلولی خالی نباشد.
قانون ۲: جمع ستون "بودجه بوست" در جدول ۱ باید دقیقاً {boost_budget:,} تومان باشد.
قانون ۳: بودجه اینفلوئنسر در جدول ۳ باید دقیقاً {influencer_budget:,} تومان باشد.
قانون ۴: بودجه روزهای ریلز باید بیشتر از پست معمولی باشد (ریلز > کاروسل > تک‌عکس).
قانون ۵: هیچ دو روزی بودجه یکسان نداشته باشند.
قانون ۶: در آخرین سطر جدول ۱، یک ردیف "جمع کل" اضافه کن که جمع ستون بودجه بوست را نشان دهد.

═══════════════════════════════════
قوانین Reach:
═══════════════════════════════════

قانون ۷: Reach ارگانیک ریلز = حداقل ۳ برابر پست تک‌عکس همان هفته.
قانون ۸: Reach ارگانیک کاروسل = حدود ۱.۵ برابر پست تک‌عکس.
قانون ۹: Reach پولی = (بودجه بوست آن روز ÷ ۳۰,۰۰۰) × ۱,۰۰۰
قانون ۱۰: هیچ دو روزی Reach ارگانیک یکسان نداشته باشند.

═══════════════════════════════════

### 🎬 جدول 1: تقویم فید و ریلز (7 روز)
| روز/تاریخ | فرمت | هدف KPI | Hook (کلمه‌به‌کلمه) | ایده تصویربرداری | CTA | UTM | بودجه بوست (تومان) | Reach ارگانیک | Reach پولی |

### 📱 جدول 2: استوری سریالی (همان 3 روز اول × 3 استوری)
| روز/تاریخ | ساعت | سناریو دقیق | استیکر | UTM |

### 🤝 جدول 3: بریف میکرواینفلوئنسر
| فالوور رنج | بودجه | دیدلاین | Dos | Don'ts | دیالوگ پیشنهادی |

### 🚨 جدول 4: ماتریس بحران (3 سناریو)
| نوع بحران | پاسخ عمومی | پاسخ خصوصی | مهلت | اقدام |
"""

def build_seo_prompt(
    current_date, brand_name, niche, target_audience,
    competitors, domain_authority, monthly_traffic,
    seo_strategy, campaign_goal, cms_platform
) -> str:
    return f"""
داده‌های این پروژه سئو:
- تاریخ: {current_date}
- برند: {brand_name}
- حوزه فعالیت: {niche}
- مخاطب هدف: {target_audience or "بر اساس حوزه فعالیت حدس بزن"}
- رقبای اصلی: {competitors or "نامشخص"}
- Domain Authority سایت: {domain_authority}
- ترافیک ماهانه فعلی: {monthly_traffic:,} بازدید
- اولویت سئو: {seo_strategy}
- هدف محتوا: {campaign_goal}
- CMS: {cms_platform}

### 📑 جدول 1: معماری Topic Cluster (5 صفحه)
| نوع صفحه (Pillar/Cluster) | عنوان H1 | کلمه کلیدی اصلی | LSI Keywords | Search Intent | سختی (Low/Med/High) | لینک داخلی به |

### 📝 جدول 2: Content Gap رقبا
| رقیب | محتوای موجود رقیب | نقطه ضعف محتوایی | فرصت ما |

### 🔗 جدول 3: برنامه لینک‌سازی (Link Building)
| نوع لینک | منبع پیشنهادی | Anchor Text | DoFollow/NoFollow | اولویت |

### 📊 جدول 4: تقویم انتشار محتوا (8 هفته)
| هفته | عنوان مقاله | کلمه کلیدی | نوع صفحه | هدف این هفته |
"""

# =============================================
# صفحه لاگین
# =============================================
if not st.session_state.user:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""
            <div style='text-align:center; padding: 3rem 0 2rem;'>
                <div style='font-size:3rem; margin-bottom:1rem;'>🚀</div>
                <h1 style='font-size:2rem !important; margin-bottom:0.5rem;'>Traffic Pilot</h1>
                <p style='color:#475569; font-size:0.95rem;'>
                    پلتفرم تدوین استراتژی محتوای داده‌محور
                </p>
            </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["ورود به حساب", "ایجاد حساب"])

        with tab1:
            with st.form("login_form"):
                st.text_input("آدرس ایمیل", placeholder="name@company.com", key="li_email")
                st.text_input("رمز عبور", type="password", placeholder="••••••••", key="li_pass")
                st.write("")
                if st.form_submit_button("ورود به سیستم", use_container_width=True):
                    try:
                        res = supabase.auth.sign_in_with_password({
                            "email": st.session_state.li_email,
                            "password": st.session_state.li_pass
                        })
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        logger.warning(f"Login failed: {e}")
                        st.error("ایمیل یا رمز عبور اشتباه است.")

        with tab2:
            with st.form("signup_form"):
                st.text_input("آدرس ایمیل", placeholder="name@company.com", key="su_email")
                st.text_input("رمز عبور", type="password",
                              placeholder="حداقل ۶ کاراکتر", key="su_pass")
                st.write("")
                if st.form_submit_button("ایجاد حساب رایگان", use_container_width=True):
                    try:
                        supabase.auth.sign_up({
                            "email": st.session_state.su_email,
                            "password": st.session_state.su_pass
                        })
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
        st.markdown(f"""
            <div style='text-align:center; padding: 1.5rem 0 1rem;'>
                <div style='
                    width: 56px; height: 56px;
                    background: linear-gradient(135deg,#6366f1,#a855f7);
                    border-radius: 50%;
                    display: flex; align-items: center;
                    justify-content: center;
                    margin: 0 auto 12px;
                    font-size: 1.5rem;
                    box-shadow: 0 4px 15px rgba(99,102,241,0.4);
                '>🚀</div>
                <div style='font-weight:700; font-size:1.1rem;
                            color:#e2e8f0;'>Traffic Pilot</div>
                <div style='font-size:0.75rem; color:#475569;
                            margin-top:2px;'>Agency Standard</div>
            </div>
            <hr style='border-color:rgba(255,255,255,0.06); margin:0.5rem 0 1.5rem;'/>
        """, unsafe_allow_html=True)

        credit_color = "#22c55e" if credits > 3 else "#f59e0b" if credits > 0 else "#ef4444"
        st.markdown(f"""
            <div style='
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 14px;
                padding: 1.2rem;
                margin-bottom: 1rem;
            '>
                <div style='display:flex; align-items:center;
                            gap:8px; margin-bottom:12px;'>
                    <div style='
                        width:32px; height:32px;
                        background:rgba(99,102,241,0.15);
                        border-radius:8px;
                        display:flex; align-items:center;
                        justify-content:center; font-size:1rem;
                    '>👤</div>
                    <div>
                        <div style='font-size:0.85rem; font-weight:600; color:#e2e8f0;'>
                            {user.email.split('@')[0]}
                        </div>
                        <div style='font-size:0.72rem; color:#475569;'>
                            {user.email}
                        </div>
                    </div>
                </div>
                <div style='
                    background: rgba(255,255,255,0.03);
                    border-radius: 10px; padding: 12px;
                    display: flex; justify-content: space-between;
                    align-items: center;
                '>
                    <div>
                        <div style='font-size:0.72rem; color:#475569; margin-bottom:2px;'>
                            اعتبار باقی‌مانده
                        </div>
                        <div style='font-size:1.8rem; font-weight:800;
                                    color:{credit_color}; line-height:1;'>
                            {credits}
                        </div>
                    </div>
                    <div style='
                        background: rgba(99,102,241,0.1);
                        border: 1px solid rgba(99,102,241,0.2);
                        border-radius: 8px; padding: 6px 12px;
                        font-size: 0.72rem; color: #a5b4fc; font-weight: 500;
                    '>استراتژیست</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.progress(min(credits / 10, 1.0))
        st.write("")

        if st.button("خروج از سیستم", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # ── Header ──
    st.markdown("""
        <div style='margin-bottom: 2rem;'>
            <h1>تدوین مدیا پلن آژانسی</h1>
            <p style='color:#475569; margin-top:0.5rem; font-size:0.95rem;'>
                داده‌های واقعی کسب‌وکار را وارد کنید تا KPIها به صورت ریاضی محاسبه شوند
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Mode Selector ──
    mode = st.radio(
        "نوع خروجی:",
        ["📱 تقویم اینستاگرام", "🔍 کلاستر محتوایی سایت (SEO)"],
        horizontal=True
    )
    st.write("")

    # ── فرم ──
    with st.container():
        st.markdown("""
            <div style='font-size:0.8rem; font-weight:600; color:#475569;
                        text-transform:uppercase; letter-spacing:1px;
                        margin-bottom:1rem;'>
                اطلاعات پایه برند
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            brand_name = st.text_input("نام برند", placeholder="مثلاً: پاما")
        with c2:
            niche = st.text_input("حوزه فعالیت", placeholder="مثلاً: کفش چرم طبی")
        with c3:
            target_audience = st.text_input(
                "مخاطب هدف",
                placeholder="آقایان ۴۰ ساله کارمند"
            )

        st.write("")

        if mode == "📱 تقویم اینستاگرام":
            st.markdown("""
                <div style='font-size:0.8rem; font-weight:600; color:#475569;
                            text-transform:uppercase; letter-spacing:1px;
                            margin-bottom:1rem;'>
                    📊 داده‌های استراتژیک اینستاگرام
                </div>
            """, unsafe_allow_html=True)

            c4, c5, c6 = st.columns(3)
            with c4:
                current_followers = st.number_input(
                    "فالوور فعلی پیج", min_value=0, value=1500, step=100
                )
            with c5:
                total_budget = st.number_input(
                    "بودجه کل کمپین (تومان)", min_value=0,
                    value=10_000_000, step=1_000_000
                )
            with c6:
                competitors = st.text_input(
                    "رقبای اصلی (پیج اینستاگرام)",
                    placeholder="@novincharm، @charm_mashhad"
                )

            st.write("")
            st.markdown("""
                <div style='font-size:0.8rem; font-weight:600; color:#475569;
                            text-transform:uppercase; letter-spacing:1px;
                            margin-bottom:1rem;'>
                    🎬 سبک تولید محتوا
                </div>
            """, unsafe_allow_html=True)

            c7, c8, c9 = st.columns(3)
            with c7:
                admin_on_camera = st.selectbox(
                    "حضور جلوی دوربین",
                    [
                        "ادمین/مدیر کاملاً جلوی دوربین",
                        "ترکیبی (صداگذاری + کمی چهره)",
                        "فقط محصول (بدون چهره)"
                    ]
                )
            with c8:
                campaign_goal = st.selectbox(
                    "هدف اصلی کمپین",
                    [
                        "آگاهی و جذب فالوور (TOFU)",
                        "تعامل و داستان‌سرایی (MOFU)",
                        "فروش مستقیم (BOFU)"
                    ]
                )
            with c9:
                campaign_phase = st.selectbox(
                    "فاز کمپین",
                    [
                        "عادی / استمرار (Sustain)",
                        "تیزینگ (Teasing)",
                        "رونمایی / لانچ (Launch)"
                    ]
                )

            domain_authority = None
            seo_strategy = None
            monthly_traffic = None
            cms_platform = None

        else:
            st.markdown("""
                <div style='font-size:0.8rem; font-weight:600; color:#475569;
                            text-transform:uppercase; letter-spacing:1px;
                            margin-bottom:1rem;'>
                    📊 داده‌های استراتژیک سئو
                </div>
            """, unsafe_allow_html=True)

            c4, c5, c6 = st.columns(3)
            with c4:
                domain_authority = st.number_input(
                    "Domain Authority سایت", min_value=0, max_value=100, value=15
                )
            with c5:
                monthly_traffic = st.number_input(
                    "ترافیک ماهانه فعلی (بازدید)", min_value=0, value=500, step=100
                )
            with c6:
                competitors = st.text_input(
                    "رقبای اصلی (دامنه سایت)",
                    placeholder="novincharm.com، charm-mashhad.ir"
                )

            st.write("")
            st.markdown("""
                <div style='font-size:0.8rem; font-weight:600; color:#475569;
                            text-transform:uppercase; letter-spacing:1px;
                            margin-bottom:1rem;'>
                    🔍 تنظیمات استراتژی سئو
                </div>
            """, unsafe_allow_html=True)

            c7, c8, c9 = st.columns(3)
            with c7:
                seo_strategy = st.selectbox(
                    "اولویت اصلی سئو",
                    [
                        "پوشش کلمات اطلاعاتی (Blog/Article)",
                        "پوشش کلمات فروشگاهی (Category/Product)",
                        "لینک‌سازی داخلی و رپورتاژ"
                    ]
                )
            with c8:
                campaign_goal = st.selectbox(
                    "هدف اصلی محتوا",
                    [
                        "افزایش ترافیک ارگانیک (TOFU)",
                        "جذب لید و مشتری (MOFU)",
                        "افزایش فروش مستقیم (BOFU)"
                    ]
                )
            with c9:
                cms_platform = st.selectbox(
                    "CMS سایت",
                    [
                        "وردپرس (WordPress)",
                        "شاپیفای (Shopify)",
                        "اختصاصی / سفارشی"
                    ]
                )

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
                st.write("")
                try:
                    generation_config = genai.types.GenerationConfig(
                        temperature=0.9,
                        max_output_tokens=8192,
                    )

                    if mode == "📱 تقویم اینستاگرام":
                        system_instruction = INSTAGRAM_SYSTEM_INSTRUCTION
                        user_prompt = build_instagram_prompt(
                            current_date, brand_name, niche, target_audience,
                            competitors, current_followers, total_budget,
                            admin_on_camera, campaign_goal, campaign_phase
                        )
                    else:
                        system_instruction = SEO_SYSTEM_INSTRUCTION
                        user_prompt = build_seo_prompt(
                            current_date, brand_name, niche, target_audience,
                            competitors, domain_authority, monthly_traffic,
                            seo_strategy, campaign_goal, cms_platform
                        )

                    model = genai.GenerativeModel(
                        "gemini-2.5-flash",
                        system_instruction=system_instruction
                    )

                    st.markdown("""
                        <div style='font-size:0.8rem; font-weight:600;
                                    color:#6366f1; text-transform:uppercase;
                                    letter-spacing:1px; margin-bottom:1rem;'>
                            📊 خروجی آژانسی
                        </div>
                    """, unsafe_allow_html=True)

                    output_placeholder = st.empty()
                    full_content = ""

                    with st.spinner("در حال پردازش..."):
                        response_stream = model.generate_content(
                            user_prompt,
                            stream=True,
                            generation_config=generation_config
                        )
                        for chunk in response_stream:
                            if chunk.text:
                                full_content += chunk.text
                                output_placeholder.markdown(full_content)

                    if not full_content.strip():
                        raise ValueError("خروجی خالی از مدل دریافت شد.")

                    # =============================================
                    # اعتبارسنجی بودجه و Reach (فقط اینستاگرام)
                    # =============================================
                    # =============================================
                    # اعتبارسنجی بودجه و Reach (فقط اینستاگرام)
                    # =============================================
                    if mode == "📱 تقویم اینستاگرام" and VALIDATORS_AVAILABLE:
                        budget_check = validate_budget(full_content, total_budget)
                        all_errors = budget_check["errors"]
                        
                        # اگر خطای بحرانی بودجه داریم، یک بار دیگر تلاش کن
                        if all_errors:
                            st.warning("⚠️ بودجه‌ها اشتباه محاسبه شدند. در حال تصحیح خودکار...")
                            
                            fix_prompt = f"""
خروجی قبلی شما دارای این خطاها در بودجه بود:
{chr(10).join(all_errors)}

لطفاً فقط جدول 1 (تقویم ۷ روز) و جدول 3 (اینفلوئنسر) را با این اعداد دقیق دوباره بنویس:

بودجه کل کمپین: {total_budget:,} تومان
- جدول 3 اینفلوئنسر: دقیقاً {int(total_budget * 0.30):,} تومان
- جدول 1 بوست: دقیقاً {int(total_budget * 0.70):,} تومان (بین ۷ روز تقسیم شود)

فرمت دقیق:
| روز/تاریخ | فرمت | هدف KPI | Hook | ایده تصویربرداری | CTA | UTM | بودجه بوست (تومان) | Reach ارگانیک | Reach پولی |
| جمع کل | - | - | - | - | - | - | {int(total_budget * 0.70):,} | - | - |

فقط جداول را خروجی بده. بدون توضیح اضافه.
"""
                            try:
                                fix_response = model.generate_content(
                                    fix_prompt,
                                    generation_config=genai.types.GenerationConfig(
                                        temperature=0.3,  # دمای کمتر برای دقت
                                        max_output_tokens=4096,
                                    )
                                )
                                if fix_response.text:
                                    # جایگزینی جداول اصلاح‌شده
                                    # (این بخش ساده‌سازی شده است؛ در نسخه نهایی نیاز به parse دقیق‌تر دارد)
                                    full_content += "\n\n### ✅ نسخه تصحیح‌شده بودجه:\n" + fix_response.text
                                    st.markdown(fix_response.text)
                            except Exception as fix_err:
                                logger.error(f"Auto-fix failed: {fix_err}")
                    # ── دکمه‌های دانلود ──
                    st.write("")
                    dl1, dl2, _ = st.columns([1, 1, 2])
                    with dl1:
                        st.download_button(
                            "📥 دانلود Markdown",
                            full_content,
                            f"{brand_name}_plan.md",
                            "text/markdown",
                            use_container_width=True
                        )
                    with dl2:
                        st.download_button(
                            "📄 دانلود TXT",
                            full_content,
                            f"{brand_name}_plan.txt",
                            "text/plain",
                            use_container_width=True
                        )

                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    refund_credit(user.id, credits)
                    st.error("خطا در ارتباط با سرور. اعتبار شما بازگردانده شد.")
