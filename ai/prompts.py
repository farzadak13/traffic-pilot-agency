from typing import Dict, Any, List


INSTAGRAM_SYSTEM_INSTRUCTION = """
تو یک Senior Social Media Strategist و Copywriter بومی ایرانی هستی.

قوانین ثابت:
1) لحن تبلیغاتی کلیشه‌ای ممنوع.
از عبارت‌هایی مثل:
"بی‌نظیر"، "فوق‌العاده"، "درخشش"، "لوکس"، "فقط یک ... نیست"، "تجربه‌ای خاص"
و هر جمله شبیه تیزر تلویزیونی استفاده نکن.

2) Hook باید یکی از این 4 مدل باشد:
- درد ملموس مخاطب
- باور غلط رایج
- سوال چالشی
- فکت یا مشاهده غافلگیرکننده

3) لحن کاملاً محاوره‌ای، طبیعی و ایرانی باشد.

4) CTAها مدرن و تعاملی باشند.
حداقل نیمی از CTAها از جنس این الگوها باشند:
- «کلمه X رو کامنت کن تا لینک برات دایرکت بشه»
- «این پست رو سیو کن، بعداً لازم میشه»
- «اگه این مشکل رو داشتی، توی کامنت بگو»

5) رقبا را تخریب نکن.

6) دیالوگ اینفلوئنسر باید نیتیو، روزمره و قابل گفتن باشد؛ نه رسمی و تبلیغاتی.

7) خروجی فقط JSON معتبر باشد. هیچ متن اضافه، توضیح، مقدمه یا کد بلاک ننویس.
"""


SEO_SYSTEM_INSTRUCTION = """
تو یک Senior SEO Content Strategist ایرانی هستی.

قوانین:
1) Search Intent واقعی کاربر ایرانی مبنا باشد.
2) عنوان‌های کلیشه‌ای مثل «راهنمای کامل» یا «همه چیز درباره» ننویس مگر واقعاً لازم باشد.
3) رقبا را تخریب نکن؛ فقط ضعف محتوایی یا خلأ پوشش را تحلیل کن.
4) سختی کلمات را با توجه به DA سایت و وضعیت فعلی آن واقع‌بینانه برچسب بزن.
5) خروجی فقط JSON معتبر باشد. هیچ متن اضافه، توضیح، مقدمه یا کد بلاک ننویس.
"""


MERGER_SYSTEM_INSTRUCTION = """
تو یک Meta-Strategist هستی.
دو خروجی ساختاریافته را می‌گیری و نسخه نهایی را یکپارچه می‌سازی.

قوانین:
1) Hook و CTA قوی‌تر و نیتیوتر را انتخاب کن.
2) اعداد و KPIها را از نسخه منطقی‌تر بردار.
3) ایده‌های تصویربرداری مکمل را ترکیب کن.
4) تکرارها را حذف کن.
5) خروجی فقط JSON معتبر باشد.
"""


def _safe(value: Any, fallback: str = "نامشخص") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _join_lines(items: List[str]) -> str:
    return "\n".join(items)


def build_instagram_creative_prompt(data: Dict[str, Any], skeleton: Dict[str, Any]) -> str:
    day_lines = []
    for day in skeleton["days"]:
        day_lines.append(
            f"- روز {day['day_index']} | تاریخ {day['date']} | فرمت {day['format']} | KPI {day['kpi']} | UTM {day['utm']}"
        )

    story_lines = []
    for day in skeleton["story_days"]:
        times = " / ".join(item["time"] for item in day["items"])
        story_lines.append(
            f"- روز {day['day_index']} | تاریخ {day['date']} | تایم‌های استوری: {times}"
        )

    return f"""
داده‌های کمپین:
- تاریخ شروع: {_safe(data.get("current_date"))}
- برند: {_safe(data.get("brand_name"))}
- حوزه فعالیت: {_safe(data.get("niche"))}
- مخاطب هدف: {_safe(data.get("target_audience"), "بر اساس حوزه حدس بزن")}
- شهر/لوکیشن: {_safe(data.get("city"), "نامشخص")}
- محصول/خدمت اصلی: {_safe(data.get("main_offer"), "نامشخص")}
- مزیت اصلی برند: {_safe(data.get("brand_advantage"), "نامشخص")}
- دردها/سوال‌های پرتکرار: {_safe(data.get("pain_points"), "بر اساس حوزه حدس بزن")}
- رقبای اصلی: {_safe(data.get("competitors"), "نامشخص")}
- فالوور فعلی پیج: {data.get("current_followers", 0):,}
- سبک حضور جلوی دوربین: {_safe(data.get("admin_on_camera"))}
- هدف اصلی کمپین: {_safe(data.get("campaign_goal"))}
- فاز کمپین: {_safe(data.get("campaign_phase"))}
- مسیر تبدیل: {_safe(data.get("conversion_path"), "دایرکت")}
- نکته یا محدودیت اجرایی: {_safe(data.get("content_notes"), "ندارد")}

اسکلت قطعی تقویم که نباید تغییر کند:
{_join_lines(day_lines)}

استوری‌های قطعی:
{_join_lines(story_lines)}

وظیفه تو:
- فقط بخش خلاقه را بساز.
- تاریخ، بودجه، Reach و UTM را تغییر نده چون این‌ها خارج از مدل مدیریت می‌شوند.
- Hook هر روز باید متفاوت باشد.
- CTAها تکراری نباشند.
- سناریوهای استوری کوتاه، اجرایی و قابل پیاده‌سازی باشند.
- دیالوگ اینفلوئنسر طبیعی و گفتنی باشد.
- برای بحران‌ها پاسخ حرفه‌ای، آرام و بدون دفاع تهاجمی بنویس.

فقط JSON معتبر با این ساختار دقیق بده:
{{
  "feed_plan": [
    {{
      "day_index": 1,
      "hook": "",
      "shot_idea": "",
      "cta": ""
    }},
    {{
      "day_index": 2,
      "hook": "",
      "shot_idea": "",
      "cta": ""
    }},
    {{
      "day_index": 3,
      "hook": "",
      "shot_idea": "",
      "cta": ""
    }},
    {{
      "day_index": 4,
      "hook": "",
      "shot_idea": "",
      "cta": ""
    }},
    {{
      "day_index": 5,
      "hook": "",
      "shot_idea": "",
      "cta": ""
    }},
    {{
      "day_index": 6,
      "hook": "",
      "shot_idea": "",
      "cta": ""
    }},
    {{
      "day_index": 7,
      "hook": "",
      "shot_idea": "",
      "cta": ""
    }}
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
    {{
      "type": "",
      "public_response": "",
      "private_response": "",
      "deadline": "",
      "action": ""
    }},
    {{
      "type": "",
      "public_response": "",
      "private_response": "",
      "deadline": "",
      "action": ""
    }},
    {{
      "type": "",
      "public_response": "",
      "private_response": "",
      "deadline": "",
      "action": ""
    }}
  ]
}}

الزامات تکمیلی:
- feed_plan دقیقاً 7 آیتم داشته باشد.
- story_plan دقیقاً 3 روز داشته باشد و هر روز دقیقاً 3 استوری.
- Hookها تبلیغاتی و شعارگونه نباشند.
- CTAها تعاملی و امروزی باشند.
- sample_dialogue باید شبیه حرف زدن یک آدم واقعی باشد.
- هیچ متن اضافه قبل یا بعد از JSON ننویس.
"""


def build_instagram_repair_prompt(base_prompt: str, raw_output: str, errors: List[str]) -> str:
    joined_errors = "\n".join([f"- {e}" for e in errors]) if errors else "- ساختار JSON مشکل داشت."
    return f"""
{base_prompt}

خروجی قبلی این خطاها را داشت:
{joined_errors}

خروجی قبلی:
{raw_output}

حالا فقط همان JSON را به‌صورت کامل، معتبر و بدون هیچ متن اضافه دوباره تولید کن.
"""


def build_seo_prompt(data: Dict[str, Any]) -> str:
    return f"""
داده‌های پروژه:
- تاریخ: {_safe(data.get("current_date"))}
- برند: {_safe(data.get("brand_name"))}
- حوزه فعالیت: {_safe(data.get("niche"))}
- مخاطب هدف: {_safe(data.get("target_audience"), "بر اساس حوزه حدس بزن")}
- شهر/لوکیشن: {_safe(data.get("city"), "نامشخص")}
- محصول/خدمت اصلی: {_safe(data.get("main_offer"), "نامشخص")}
- مزیت اصلی برند: {_safe(data.get("brand_advantage"), "نامشخص")}
- دردها/سوال‌های پرتکرار: {_safe(data.get("pain_points"), "بر اساس حوزه حدس بزن")}
- رقبای اصلی: {_safe(data.get("competitors"), "نامشخص")}
- Domain Authority: {data.get("domain_authority", 0)}
- ترافیک ماهانه فعلی: {data.get("monthly_traffic", 0):,}
- اولویت سئو: {_safe(data.get("seo_strategy"))}
- هدف محتوا: {_safe(data.get("campaign_goal"))}
- CMS: {_safe(data.get("cms_platform"))}
- صفحات/دسته‌بندی‌های فعلی: {_safe(data.get("existing_pages"), "نامشخص")}
- Seed Keywords: {_safe(data.get("seed_keywords"), "نامشخص")}

وظیفه تو:
- یک Topic Cluster واقع‌بینانه بساز.
- intent واقعی کاربر ایرانی را مبنا قرار بده.
- اگر نام رقبا نامشخص بود، از الگوهای رایج SERP فارسی همان حوزه استفاده کن.
- ضعف رقبا را به‌صورت تحلیلی بگو، نه تخریبی.
- Difficulty را فقط با یکی از این مقادیر بنویس: Low / Med / High
- ساختار را دقیق نگه دار.

فقط JSON معتبر با این ساختار بده:
{{
  "topic_cluster": [
    {{
      "page_type": "Pillar",
      "h1": "",
      "primary_keyword": "",
      "lsi_keywords": ["", ""],
      "intent": "",
      "difficulty": "Med",
      "internal_links_to": ["", ""]
    }},
    {{
      "page_type": "Cluster",
      "h1": "",
      "primary_keyword": "",
      "lsi_keywords": ["", ""],
      "intent": "",
      "difficulty": "Low",
      "internal_links_to": ["", ""]
    }},
    {{
      "page_type": "Cluster",
      "h1": "",
      "primary_keyword": "",
      "lsi_keywords": ["", ""],
      "intent": "",
      "difficulty": "Low",
      "internal_links_to": ["", ""]
    }},
    {{
      "page_type": "Cluster",
      "h1": "",
      "primary_keyword": "",
      "lsi_keywords": ["", ""],
      "intent": "",
      "difficulty": "Med",
      "internal_links_to": ["", ""]
    }},
    {{
      "page_type": "Cluster",
      "h1": "",
      "primary_keyword": "",
      "lsi_keywords": ["", ""],
      "intent": "",
      "difficulty": "Med",
      "internal_links_to": ["", ""]
    }}
  ],
  "content_gap": [
    {{
      "competitor": "",
      "existing_content": "",
      "weakness": "",
      "our_strategy": ""
    }},
    {{
      "competitor": "",
      "existing_content": "",
      "weakness": "",
      "our_strategy": ""
    }},
    {{
      "competitor": "",
      "existing_content": "",
      "weakness": "",
      "our_strategy": ""
    }}
  ],
  "link_building": [
    {{
      "link_type": "",
      "source": "",
      "anchor_text": "",
      "follow_type": "DoFollow",
      "priority": ""
    }},
    {{
      "link_type": "",
      "source": "",
      "anchor_text": "",
      "follow_type": "NoFollow",
      "priority": ""
    }},
    {{
      "link_type": "",
      "source": "",
      "anchor_text": "",
      "follow_type": "DoFollow",
      "priority": ""
    }},
    {{
      "link_type": "",
      "source": "",
      "anchor_text": "",
      "follow_type": "NoFollow",
      "priority": ""
    }},
    {{
      "link_type": "",
      "source": "",
      "anchor_text": "",
      "follow_type": "DoFollow",
      "priority": ""
    }}
  ],
  "calendar": [
    {{
      "week": 1,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }},
    {{
      "week": 2,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }},
    {{
      "week": 3,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }},
    {{
      "week": 4,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }},
    {{
      "week": 5,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }},
    {{
      "week": 6,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }},
    {{
      "week": 7,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }},
    {{
      "week": 8,
      "title": "",
      "keyword": "",
      "page_type": "",
      "goal": ""
    }}
  ]
}}

الزامات:
- topic_cluster دقیقاً 5 آیتم داشته باشد.
- بهتر است 1 Pillar و 4 Cluster باشد.
- content_gap دقیقاً 3 آیتم داشته باشد.
- link_building دقیقاً 5 آیتم داشته باشد.
- calendar دقیقاً 8 آیتم داشته باشد.
- عنوان‌ها نباید کلیشه‌ای باشند.
- هیچ متن اضافه قبل یا بعد از JSON ننویس.
"""


def build_seo_repair_prompt(base_prompt: str, raw_output: str, errors: List[str]) -> str:
    joined_errors = "\n".join([f"- {e}" for e in errors]) if errors else "- ساختار JSON مشکل داشت."
    return f"""
{base_prompt}

خروجی قبلی این خطاها را داشت:
{joined_errors}

خروجی قبلی:
{raw_output}

حالا فقط همان JSON را به‌صورت کامل، معتبر و بدون هیچ متن اضافه دوباره تولید کن.
"""

def build_instagram_prompt(
    current_date: str,
    brand_name: str,
    niche: str,
    target_audience: str,
    competitors: str,
    current_followers: int,
    total_budget: int,
    admin_on_camera: str,
    campaign_goal: str,
    campaign_phase: str,
) -> str:
    """
    ساخت prompt کامل برای تولید تقویم اینستاگرام
    """
    
    # محاسبه بودجه‌ها
    boost_budget = int(total_budget * 0.70)
    influencer_budget = int(total_budget * 0.30)
    
    # تقویم 7 روزه
    days_skeleton = []
    for day in range(1, 8):
        days_skeleton.append({
            "day_index": day,
            "date": f"روز {day}",
            "format": "Feed Post" if day % 2 == 1 else "Reel",
            "kpi": "Reach/Engagement",
            "utm": f"utm_source=ig&utm_campaign=day{day}"
        })
    
    # استوری‌های 3 روز اول
    story_skeleton = []
    for day in [1, 2, 3]:
        story_skeleton.append({
            "day_index": day,
            "date": f"روز {day}",
            "items": [
                {"time": "09:00"},
                {"time": "14:00"},
                {"time": "20:00"}
            ]
        })
    
    # داده‌های مرحله
    data = {
        "current_date": current_date,
        "brand_name": brand_name,
        "niche": niche,
        "target_audience": target_audience,
        "competitors": competitors,
        "current_followers": current_followers,
        "admin_on_camera": admin_on_camera,
        "campaign_goal": campaign_goal,
        "campaign_phase": campaign_phase,
    }
    
    skeleton = {
        "days": days_skeleton,
        "story_days": story_skeleton
    }
    
    # فراخوانی تابع خلاقه
    return build_instagram_creative_prompt(data, skeleton)


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
) -> str:
    """
    ساخت prompt کامل برای تولید کلاستر SEO
    """
    
    data = {
        "current_date": current_date,
        "brand_name": brand_name,
        "niche": niche,
        "target_audience": target_audience,
        "competitors": competitors,
        "domain_authority": domain_authority,
        "monthly_traffic": monthly_traffic,
        "seo_strategy": seo_strategy,
        "campaign_goal": campaign_goal,
        "cms_platform": cms_platform,
    }
    
    return build_seo_prompt(data)
