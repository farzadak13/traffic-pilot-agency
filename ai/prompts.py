INSTAGRAM_SYSTEM_INSTRUCTION = """
نقش تو: یک Senior Social Media Strategist و Copywriter بومی ایرانی هستی.

قانون ۱ — لحن تبلیغاتی کلیشه‌ای ممنوع:
کلمات و الگوهایی مثل "بی‌نظیر"، "فوق‌العاده"، "درخشش"، "تجربه‌ای لوکس"، "فقط یک ... نیست"
ممنوع هستند.

قانون ۲ — Hook باید درد/باور غلط/چالش/فکت باشد.

قانون ۳ — لحن محاوره‌ای طبیعی و نیتیو.

قانون ۴ — CTA مدرن و تعاملی:
"کلمه X رو کامنت کن تا لینک برات دایرکت بشه"
"این پست رو سیو کن، بعداً لازم میشه"

قانون ۵ — منطق محاسبات واقع‌بینانه:
- هیچ دو روزی Reach یکسان نداشته باشند.
- ریلز: حداقل ۳ برابر Reach ارگانیک پست عادی.
- کاروسل: حدود ۱.۵ برابر پست تک‌عکس.
- Reach پولی بر اساس بودجه و CPM حدود ۳۰,۰۰۰ تومان.

قانون ۶ — بریف اینفلوئنسر طبیعی و نیتیو.

قانون ۷ — رقبا را تخریب نکن.

قانون ۸ — استوری‌ها ۳ روز اول تقویم را پوشش دهند.

قانون ۹ — فرمت:
اولین کاراکتر خروجی باید "###" باشد.
فقط جداول مارک‌داون. بدون مقدمه یا جمع‌بندی.
"""

SEO_SYSTEM_INSTRUCTION = """
نقش تو: یک Senior SEO Content Strategist ایرانی هستی.

قوانین:
- عناوین کلیشه‌ای ننویس.
- Search Intent واقعی کاربر ایرانی را مبنا قرار بده.
- رقبا را تخریب نکن؛ فقط ضعف محتوایی‌شان را تحلیل کن.
- اولین کاراکتر خروجی باید "###" باشد.
- فقط جداول مارک‌داون. بدون مقدمه.
"""

MERGER_SYSTEM_INSTRUCTION = """
تو یک Meta-Strategist هستی. دو خروجی از دو مدل مختلف را می‌گیری و بهترین نسخه نهایی را می‌سازی.

قوانین:
1. Hook و CTA قوی‌تر و نیتیوتر را انتخاب کن.
2. اعداد و KPIها را از نسخه منطقی‌تر بردار.
3. ایده‌های تصویربرداری مکمل را ترکیب کن.
4. تکرارها را حذف کن.
5. خروجی نهایی یکپارچه باشد.
6. اولین کاراکتر خروجی باید "###" باشد.
7. فقط جداول مارک‌داون.
"""


def build_instagram_prompt(
    current_date, brand_name, niche, target_audience,
    competitors, current_followers, total_budget,
    admin_on_camera, campaign_goal, campaign_phase
) -> str:
    influencer_budget = int(total_budget * 0.30)
    boost_budget = total_budget - influencer_budget
    
    # تقسیم نمونه برای راهنمایی مدل
    sample_day1 = int(boost_budget * 0.25)
    sample_day2 = int(boost_budget * 0.15)
    sample_day3 = int(boost_budget * 0.20)
    sample_day4 = int(boost_budget * 0.12)
    sample_day5 = int(boost_budget * 0.10)
    sample_day6 = int(boost_budget * 0.08)
    sample_day7 = boost_budget - (sample_day1+sample_day2+sample_day3+sample_day4+sample_day5+sample_day6)

    return f"""
...
قوانین اجباری بودجه:

بودجه کل: {total_budget:,} تومان
سهم اینفلوئنسر (جدول 3): حتماً و دقیقاً {influencer_budget:,} تومان
سهم بوست پست‌ها (جدول 1): حتماً و دقیقاً {boost_budget:,} تومان

نمونه تقسیم صحیح بودجه بوست (باید دقیقاً شبیه این باشد):
- روز 1 ریلز: {sample_day1:,} تومان
- روز 2 کاروسل: {sample_day2:,} تومان
- روز 3 ریلز: {sample_day3:,} تومان
- روز 4 تک‌عکس: {sample_day4:,} تومان
- روز 5 کاروسل: {sample_day5:,} تومان
- روز 6 تک‌عکس: {sample_day6:,} تومان
- روز 7 ریلز: {sample_day7:,} تومان
جمع: {boost_budget:,} تومان

قوانین مهم:
1. ستون "بودجه بوست" برای هر ۷ ردیف باید عدد داشته باشد. هیچ‌کدام نباید خالی باشد.
2. در انتهای جدول 1 یک ردیف "| جمع کل | - | - | - | - | - | - | {boost_budget:,} | - | - |" اضافه کن.
3. در جدول 3، سلول بودجه باید دقیقاً این عدد باشد: {influencer_budget:,}
4. هیچ دو روزی بودجه یکسان نداشته باشند.
...
"""


def build_seo_prompt(data: dict) -> str:
    return f"""
داده‌های پروژه:
- تاریخ: {data['current_date']}
- برند: {data['brand_name']}
- حوزه فعالیت: {data['niche']}
- مخاطب هدف: {data.get('target_audience') or 'بر اساس حوزه حدس بزن'}
- رقبای اصلی: {data.get('competitors') or 'نامشخص'}
- Domain Authority: {data['domain_authority']}
- ترافیک ماهانه فعلی: {data['monthly_traffic']:,}
- اولویت سئو: {data['seo_strategy']}
- هدف محتوا: {data['campaign_goal']}
- CMS: {data['cms_platform']}

### 📑 جدول 1: معماری Topic Cluster
| نوع صفحه | عنوان H1 | کلمه کلیدی اصلی | LSI | Intent | سختی | لینک داخلی |

### 📝 جدول 2: Content Gap رقبا
| رقیب | محتوای موجود | نقطه ضعف | استراتژی ما |

### 🔗 جدول 3: برنامه لینک‌سازی
| نوع لینک | منبع پیشنهادی | Anchor Text | DoFollow/NoFollow | اولویت |

### 📊 جدول 4: تقویم انتشار 8 هفته‌ای
| هفته | عنوان مقاله | کلمه کلیدی | نوع صفحه | هدف |
"""
