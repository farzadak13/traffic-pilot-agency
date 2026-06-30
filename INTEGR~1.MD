# اتصال به app.py (Search Console SEO mode)

```python
from integrations.search_console import SearchConsoleClient
from ai.merger import run_seo_debate          # یا: arun_seo_debate برای اپ async
from ai.debate.context.brand import BrandContext

# 1) واکشی داده‌ی GSC (دوره فعلی + دوره قبل برای Declining/NewOpportunities)
sc = SearchConsoleClient(credentials=st.session_state["gsc_credentials"])
ok = sc.connect()
gsc_rows  = sc.get_top_queries(site_url, days=90, limit=50)  if ok else []
prev_rows = sc.get_top_queries(site_url, days=180, limit=50) if ok else []  # اختیاری

# 2) Brand Context غنی (هر فیلدی نبود، نادیده گرفته می‌شود)
brand = BrandContext(
    brand_name=form["brand_name"], site_url=site_url, niche=form["niche"],
    search_intent=form.get("search_intent"),
    target_persona=form.get("target_persona"),
    business_goals=form.get("business_goals"),
    conversion_goals=form.get("conversion_goals"),
    competitor_context=form.get("competitors"),
    internal_linking_context=form.get("internal_linking"),
    existing_content_summary=form.get("existing_content"),
)
# آینده: برای RAG/Memory فقط یک بلاک اضافه کن، بدون تغییر هسته:
# brand.add_text("اسناد بازیابی‌شده (RAG)", retrieved_docs_text)

# 3) اجرای دیبیت
result = run_seo_debate(
    gsc_rows=gsc_rows,
    brand_context=brand,
    secrets=st.secrets,                 # هر Mapping: st.secrets / os.environ / dict تست
    debater_keys=["gemini", "openai"],  # claude (در صورت وجود کلید) داورِ بی‌طرف می‌شود
    previous_gsc_rows=prev_rows,
    strategy_keys=None,                 # None = هر ۵ استراتژی؛ یا ["quick_wins","low_ctr"]
    preferred_judge="claude",
)

# 4) نمایش
if result.ok:
    st.markdown(result.final_plan)
    st.caption(f"داور: {result.judge_key} · حالت ضدسوگیری: {result.bias_mode}")
    if result.degraded:
        st.warning(f"حالت تخریب‌شده — مشارکت‌کننده‌ها: {result.participants}")
    with st.expander("شفافیت دیبیت (Drafts & Critiques)"):
        for k, r in result.rounds.drafts.items():
            st.caption(f"Draft — {k} ({r.attempts} تلاش، {r.latency_ms}ms)")
            st.markdown(r.text or f"❌ {r.error}")
        for k, r in result.rounds.critiques.items():
            st.caption(f"Critique — {k}"); st.markdown(r.text or f"❌ {r.error}")
else:
    st.error(f"تولید پلن ناموفق بود: {result.error}")
```
