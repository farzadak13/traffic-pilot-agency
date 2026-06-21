"""
ماژول پرامپت‌ها — فقط مسئول متن و قالب JSON درخواستی از مدل است.
هیچ محاسبه‌ی عددی (تاریخ، بودجه، Reach) اینجا انجام نمی‌شود؛
آن‌ها در app.py به‌صورت قطعی محاسبه و بعداً با خروجی مدل ادغام می‌شوند.
"""

from typing import Any, Dict, List, Optional


# =============================================
# System Instructions
# =============================================

INSTAGRAM_SYSTEM_INSTRUCTION = """
تو یک Senior Social Media Strategist و Copywriter بومی ایرانی هستی.

قوانین ثابت:

1) لحن تبلیغاتی کلیشه‌ای ممنوع.
از عبارت‌هایی مثل: "بی‌نظیر"، "فوق‌العاده"، "درخشش"، "لوکس"، "فقط یک ... نیست"،
"تجربه‌ای خاص" و هر جمله شبیه تیزر تلویزیونی استفاده نکن.

2) Hook باید یکی از این ۴ مدل باشد:
- درد ملموس مخاطب
- باور غلط رایج
- سوال چالشی
- فکت یا مشاهده غافلگیرکننده
هرگز Hook را با توصیف کلی محصول شروع نکن.

3) لحن کاملاً محاوره‌ای، طبیعی و ایرانی باشد؛ نه رسمی و کتابی.

4) CTAها مدرن و تعاملی باشند و در طول هفته تکرار عینی نشوند.
حداقل نیمی از CTAها از جنس این الگوها باشند:
- «کلمه X رو کامنت کن تا لینک برات دایرکت بشه»
- «این پست رو سیو کن، بعداً لازم میشه»
- «اگه این مشکل رو داشتی، توی کامنت بگو»

5) رقبا را تخریب نکن؛ فقط روی نقاط تمایز برند خودمان تمرکز کن.

6) هر روز باید حول یکی از محصولات/خدماتی بچرخد که کاربر معرفی کرده
(در «محصول کانونی این روز» مشخص شده است)، نه به‌صورت کلی و مبهم درباره برند.
از توضیح محصول داده‌شده برای ساخت جزئیات واقعی Hook و ایده تصویربرداری استفاده کن.

7) اگر «دردها و سوالات پرتکرار مشتری» داده شده، حداقل نیمی از Hookها مستقیماً
یکی از همان دردها را هدف بگیرند، نه یک درد عمومی و ساختگی.

8) دیالوگ اینفلوئنسر باید نیتیو، روزمره و قابل گفتن باشد؛ نه رسمی و تبلیغاتی.
اینفلوئنسر باید از چهره و اعتبار خودش به‌عنوان Social Proof استفاده کند،
نه این‌که چهره‌اش را پنهان کند.

9) خروجی فقط JSON معتبر باشد. هیچ متن اضافه، توضیح، مقدمه یا کد بلاک ننویس.
"""

SEO_SYSTEM_INSTRUCTION = """
تو یک Senior SEO Content Strategist ایرانی هستی که بر اساس تکنیک Pillar-Cluster کار می‌کند.

قوانین:
1) Search Intent واقعی کاربر ایرانی مبنا باشد، نه ترجمه کلمه‌به‌کلمه کلمات کلیدی انگلیسی.
2) عنوان‌های کلیشه‌ای مثل «راهنمای کامل» یا «همه چیز درباره» ننویس مگر واقعاً لازم باشد.
3) رقبا را تخریب نکن؛ فقط ضعف محتوایی یا خلأ پوشش را تحلیل کن.
4) سختی کلمات را با توجه به Domain Authority و ترافیک فعلی سایت واقع‌بینانه برچسب بزن؛
برای DA پایین، کلمات با سختی بالا را در اولویت اول قرار نده.
5) اگر محصول/خدمت اصلی و مزیت رقابتی برند داده شده، Topic Cluster را حول همان‌ها بساز،
نه حول کلمات کلیدی عمومی صنعت.
6) اگر دردها/سوالات پرتکرار مشتری داده شده، حداقل چند صفحه Cluster مستقیماً
پاسخ به همان سوالات باشند.
7) خروجی فقط JSON معتبر باشد. هیچ متن اضافه، توضیح، مقدمه یا کد بلاک ننویس.
"""


def _safe(value: Any, fallback: str = "نامشخص") -> str:
    text = str(value).strip() if value not in (None, "") else ""
    return text or fallback


def _join_lines(items: List[str]) -> str:
    return "\n".join(items)


def _format_products(products: Optional[List[Dict[str, str]]]) -> str:
    if not products:
        return "- نامشخص"
    lines = []
    for p in products:
        name = _safe(p.get("name"), "محصول/خدمت")
        desc = _safe(p.get("desc"), "")
        if desc and desc != "نامشخص":
            lines.append(f"- {name}: {desc}")
        else:
            lines.append(f"- {name}")
    return _join_lines(lines)


# =============================================
# اینستاگرام
# =============================================

def build_instagram_creative_prompt(data: Dict[str, Any], skeleton: Dict[str, Any]) -> str:
    """
    skeleton از app.py می‌آید و شامل تاریخ، فرمت، KPI، UTM، بودجه و Reach
    از پیش محاسبه‌شده است. مدل فقط اجازه دارد بخش خلاقه را بسازد و
    حق ندارد این مقادیر را تغییر دهد یا حدس بزند.
    """
    day_lines = []
    for day in skeleton["days"]:
        day_lines.append(
            f"- روز {day['day_index']} | {day['date_label']} | فرمت: {day['format']} | "
            f"KPI: {day['kpi']} | محصول کانونی این روز: {day['featured_product']}"
            + (f" ({day['featured_product_desc']})" if day.get("featured_product_desc") else "")
        )

    story_lines = []
    for day in skeleton["story_days"]:
        times = " / ".join(item["time"] for item in day["items"])
        story_lines.append(f"- روز {day['day_index']} | {day['date_label']} | تایم‌های استوری: {times}")

    return f"""
داده‌های کمپین:
- تاریخ شروع: {_safe(data.get("current_date"))}
- برند: {_safe(data.get("brand_name"))}
- حوزه فعالیت: {_safe(data.get("niche"))}
- شهر/لوکیشن فعالیت: {_safe(data.get("city"))}
- مخاطب هدف: {_safe(data.get("target_audience"), "بر اساس حوزه فعالیت حدس بزن")}
- مزیت رقابتی اصلی برند: {_safe(data.get("brand_advantage"))}
- دردها/سوالات پرتکرار مشتریان: {_safe(data.get("pain_points"), "بر اساس حوزه فعالیت حدس بزن")}
- مسیر اصلی تبدیل/فروش: {_safe(data.get("conversion_path"), "دایرکت اینستاگرام")}
- نکات و محدودیت‌های اجرایی تولید محتوا: {_safe(data.get("content_notes"), "ندارد")}
- رقبای اصلی: {_safe(data.get("competitors"))}
- فالوور فعلی پیج: {data.get("current_followers", 0):,}
- سبک حضور جلوی دوربین: {_safe(data.get("admin_on_camera"))}
- هدف اصلی کمپین: {_safe(data.get("campaign_goal"))}
- فاز کمپین: {_safe(data.get("campaign_phase"))}

محصولات/خدماتی که باید در طول هفته معرفی شوند:
{_format_products(data.get("products"))}

اسکلت قطعی تقویم (تاریخ، فرمت، KPI و محصول کانونی هر روز را عیناً همین‌طور نگه دار، تغییرشان نده):
{_join_lines(day_lines)}

استوری‌های قطعی (تاریخ هر روز را عیناً نگه دار):
{_join_lines(story_lines)}

وظیفه تو:
- فقط بخش خلاقه (Hook، ایده تصویربرداری، CTA، سناریوی استوری، بریف اینفلوئنسر، ماتریس بحران) را بساز.
- تاریخ، فرمت، KPI و محصول کانونی هر روز از قبل مشخص شده و تغییرناپذیر است.
- Hook هر روز باید متفاوت و مرتبط با محصول کانونی همان روز باشد.
- CTAها در طول هفته تکراری نباشند.
- سناریوهای استوری کوتاه، اجرایی و قابل پیاده‌سازی با موبایل باشند.
- دیالوگ اینفلوئنسر طبیعی، محاوره‌ای و قابل گفتن باشد.
- برای بحران‌ها پاسخ حرفه‌ای، آرام و بدون لحن دفاعی/تهاجمی بنویس.

فقط JSON معتبر با این ساختار دقیق بده (آرایه‌ها باید دقیقاً همین طول را داشته باشند):
{{
  "feed_plan": [
    {{"day_index": 1, "hook": "", "shot_idea": "", "cta": ""}},
    {{"day_index": 2, "hook": "", "shot_idea": "", "cta": ""}},
    {{"day_index": 3, "hook": "", "shot_idea": "", "cta": ""}},
    {{"day_index": 4, "hook": "", "shot_idea": "", "cta": ""}},
    {{"day_index": 5, "hook": "", "shot_idea": "", "cta": ""}},
    {{"day_index": 6, "hook": "", "shot_idea": "", "cta": ""}},
    {{"day_index": 7, "hook": "", "shot_idea": "", "cta": ""}}
  ],
  "story_plan": [
    {{
      "day_index": 1,
      "stories": [
        {{"story_index": 1, "scenario": "", "sticker": ""}},
        {{"story_index": 2, "scenario": "", "sticker": ""}},
        {{"story_index": 3, "scenario": "", "sticker": ""}}
      ]
    }},
    {{
      "day_index": 2,
      "stories": [
        {{"story_index": 1, "scenario": "", "sticker": ""}},
        {{"story_index": 2, "scenario": "", "sticker": ""}},
        {{"story_index": 3, "scenario": "", "sticker": ""}}
      ]
    }},
    {{
      "day_index": 3,
      "stories": [
        {{"story_index": 1, "scenario": "", "sticker": ""}},
        {{"story_index": 2, "scenario": "", "sticker": ""}},
        {{"story_index": 3, "scenario": "", "sticker": ""}}
      ]
    }}
  ],
  "influencer_brief": {{
    "follower_range": "",
    "deadline": "",
    "dos": ["", "", ""],
    "donts": ["", "", ""],
    "sample_dialogue": ""
  }},
  "crisis_matrix": [
    {{"type": "", "public_response": "", "private_response": "", "deadline": "", "action": ""}},
    {{"type": "", "public_response": "", "private_response": "", "deadline": "", "action": ""}},
    {{"type": "", "public_response": "", "private_response": "", "deadline": "", "action": ""}}
  ]
}}

الزامات تکمیلی:
- feed_plan دقیقاً ۷ آیتم داشته باشد، با day_index از ۱ تا ۷.
- story_plan دقیقاً ۳ روز داشته باشد و هر روز دقیقاً ۳ استوری.
- Hookها تبلیغاتی و شعارگونه نباشند.
- هیچ متن اضافه قبل یا بعد از JSON ننویس.
"""


def build_instagram_prompt(
    current_date: str,
    brand_name: str,
    niche: str,
    target_audience: str,
    competitors: str,
    current_followers: int,
    admin_on_camera: str,
    campaign_goal: str,
    campaign_phase: str,
    skeleton: Dict[str, Any],
    city: Optional[str] = None,
    brand_advantage: Optional[str] = None,
    pain_points: Optional[str] = None,
    conversion_path: Optional[str] = None,
    content_notes: Optional[str] = None,
    products: Optional[List[Dict[str, str]]] = None,
) -> str:
    """ساخت prompt کامل برای تولید بخش خلاقه تقویم اینستاگرام (اسکلت از قبل در app.py ساخته شده)."""
    data = {
        "current_date": current_date,
        "brand_name": brand_name,
        "niche": niche,
        "target_audience": target_audience,
        "city": city,
        "brand_advantage": brand_advantage,
        "pain_points": pain_points,
        "conversion_path": conversion_path,
        "content_notes": content_notes,
        "competitors": competitors,
        "current_followers": current_followers,
        "admin_on_camera": admin_on_camera,
        "campaign_goal": campaign_goal,
        "campaign_phase": campaign_phase,
        "products": products,
    }
    return build_instagram_creative_prompt(data, skeleton)


def build_instagram_repair_prompt(base_prompt: str, raw_output: str, errors: List[str]) -> str:
    joined_errors = "\n".join(f"- {e}" for e in errors) if errors else "- ساختار JSON مشکل داشت."
    return f"""
{base_prompt}

خروجی قبلی این خطاها را داشت:
{joined_errors}

خروجی قبلی:
{raw_output}

حالا فقط همان JSON را به‌صورت کامل، معتبر و بدون هیچ متن اضافه دوباره تولید کن.
ساختار و طول دقیق آرایه‌ها (۷ روز فید، ۳ روز استوری × ۳ استوری) را رعایت کن.
"""


# =============================================
# SEO
# =============================================

def build_seo_prompt(data: Dict[str, Any]) -> str:
    return f"""
داده‌های پروژه:
- تاریخ: {_safe(data.get("current_date"))}
- برند: {_safe(data.get("brand_name"))}
- حوزه فعالیت: {_safe(data.get("niche"))}
- شهر/لوکیشن فعالیت: {_safe(data.get("city"))}
- مخاطب هدف: {_safe(data.get("target_audience"), "بر اساس حوزه فعالیت حدس بزن")}
- محصول/خدمت اصلی: {_safe(data.get("main_offer"))}
- مزیت رقابتی اصلی برند: {_safe(data.get("brand_advantage"))}
- دردها/سوالات پرتکرار مشتریان: {_safe(data.get("pain_points"), "بر اساس حوزه فعالیت حدس بزن")}
- رقبای اصلی: {_safe(data.get("competitors"))}
- Domain Authority سایت: {data.get("domain_authority", 0)}
- ترافیک ماهانه فعلی: {data.get("monthly_traffic", 0):,} بازدید
- اولویت سئو: {_safe(data.get("seo_strategy"))}
- هدف محتوا: {_safe(data.get("campaign_goal"))}
- CMS: {_safe(data.get("cms_platform"))}
- صفحات/دسته‌بندی‌های فعلی سایت: {_safe(data.get("existing_pages"))}
- Seed Keywords (در صورت وجود): {_safe(data.get("seed_keywords"))}

وظیفه تو:
- یک Topic Cluster واقع‌بینانه و مرتبط با محصول/خدمت اصلی و مزیت رقابتی برند بساز.
- intent واقعی کاربر ایرانی را مبنا قرار بده.
- اگر نام رقبا نامشخص بود، از الگوهای رایج SERP فارسی همان حوزه استفاده کن، نه نام واقعی رقیب ساختگی.
- ضعف رقبا را به‌صورت تحلیلی بگو، نه تخریبی.
- Difficulty را فقط با یکی از این مقادیر بنویس: Low / Med / High
- ساختار را دقیق نگه دار.

فقط JSON معتبر با این ساختار بده:
{{
  "topic_cluster": [
    {{"page_type": "Pillar", "h1": "", "primary_keyword": "", "lsi_keywords": ["", ""], "intent": "", "difficulty": "Med", "internal_links_to": ["", ""]}},
    {{"page_type": "Cluster", "h1": "", "primary_keyword": "", "lsi_keywords": ["", ""], "intent": "", "difficulty": "Low", "internal_links_to": ["", ""]}},
    {{"page_type": "Cluster", "h1": "", "primary_keyword": "", "lsi_keywords": ["", ""], "intent": "", "difficulty": "Low", "internal_links_to": ["", ""]}},
    {{"page_type": "Cluster", "h1": "", "primary_keyword": "", "lsi_keywords": ["", ""], "intent": "", "difficulty": "Med", "internal_links_to": ["", ""]}},
    {{"page_type": "Cluster", "h1": "", "primary_keyword": "", "lsi_keywords": ["", ""], "intent": "", "difficulty": "Med", "internal_links_to": ["", ""]}}
  ],
  "content_gap": [
    {{"competitor": "", "existing_content": "", "weakness": "", "our_strategy": ""}},
    {{"competitor": "", "existing_content": "", "weakness": "", "our_strategy": ""}},
    {{"competitor": "", "existing_content": "", "weakness": "", "our_strategy": ""}}
  ],
  "link_building": [
    {{"link_type": "", "source": "", "anchor_text": "", "follow_type": "DoFollow", "priority": ""}},
    {{"link_type": "", "source": "", "anchor_text": "", "follow_type": "NoFollow", "priority": ""}},
    {{"link_type": "", "source": "", "anchor_text": "", "follow_type": "DoFollow", "priority": ""}},
    {{"link_type": "", "source": "", "anchor_text": "", "follow_type": "NoFollow", "priority": ""}},
    {{"link_type": "", "source": "", "anchor_text": "", "follow_type": "DoFollow", "priority": ""}}
  ],
  "calendar": [
    {{"week": 1, "title": "", "keyword": "", "page_type": "", "goal": ""}},
    {{"week": 2, "title": "", "keyword": "", "page_type": "", "goal": ""}},
    {{"week": 3, "title": "", "keyword": "", "page_type": "", "goal": ""}},
    {{"week": 4, "title": "", "keyword": "", "page_type": "", "goal": ""}},
    {{"week": 5, "title": "", "keyword": "", "page_type": "", "goal": ""}},
    {{"week": 6, "title": "", "keyword": "", "page_type": "", "goal": ""}},
    {{"week": 7, "title": "", "keyword": "", "page_type": "", "goal": ""}},
    {{"week": 8, "title": "", "keyword": "", "page_type": "", "goal": ""}}
  ]
}}

الزامات:
- topic_cluster دقیقاً ۵ آیتم داشته باشد (۱ Pillar و ۴ Cluster).
- content_gap دقیقاً ۳ آیتم داشته باشد.
- link_building دقیقاً ۵ آیتم داشته باشد.
- calendar دقیقاً ۸ آیتم داشته باشد.
- عنوان‌ها نباید کلیشه‌ای باشند.
- هیچ متن اضافه قبل یا بعد از JSON ننویس.
"""


def build_seo_prompt_main(
    current_date: str,
    brand_name: str,
    niche: str,
    target_audience: str,
    competitors: str,
    domain_authority: int,
    monthly_traffic: int,
    seo_strategy: str,
    campaign_goal: str,
    cms_platform: str,
    city: Optional[str] = None,
    main_offer: Optional[str] = None,
    brand_advantage: Optional[str] = None,
    pain_points: Optional[str] = None,
    existing_pages: Optional[str] = None,
    seed_keywords: Optional[str] = None,
) -> str:
    """ساخت prompt کامل برای تولید کلاستر SEO."""
    data = {
        "current_date": current_date,
        "brand_name": brand_name,
        "niche": niche,
        "target_audience": target_audience,
        "city": city,
        "main_offer": main_offer,
        "brand_advantage": brand_advantage,
        "pain_points": pain_points,
        "competitors": competitors,
        "domain_authority": domain_authority,
        "monthly_traffic": monthly_traffic,
        "seo_strategy": seo_strategy,
        "campaign_goal": campaign_goal,
        "cms_platform": cms_platform,
        "existing_pages": existing_pages,
        "seed_keywords": seed_keywords,
    }
    return build_seo_prompt(data)


def build_seo_repair_prompt(base_prompt: str, raw_output: str, errors: List[str]) -> str:
    joined_errors = "\n".join(f"- {e}" for e in errors) if errors else "- ساختار JSON مشکل داشت."
    return f"""
{base_prompt}

خروجی قبلی این خطاها را داشت:
{joined_errors}

خروجی قبلی:
{raw_output}

حالا فقط همان JSON را به‌صورت کامل، معتبر و بدون هیچ متن اضافه دوباره تولید کن.
طول دقیق هر آرایه (۵ / ۳ / ۵ / ۸) را رعایت کن.
"""
