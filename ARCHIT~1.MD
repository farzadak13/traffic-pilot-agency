# Traffic Pilot — Multi-Agent SEO Debate (v2)

## ساختار
```
ai/
├── providers/                 # لایه مدل‌ها (vendor-agnostic, async, retry/backoff)
│   ├── base.py                # LLMProvider + generate/agenerate + retry+jitter+timeout
│   ├── registry.py            # @register_provider  (Open/Closed)
│   ├── gemini_provider.py
│   ├── openai_provider.py
│   └── anthropic_provider.py  # Claude — نمونه‌ی افزودن مدل سوم
├── debate/
│   ├── orchestrator.py        # هسته async: gather روی Draft و Critique
│   ├── judge.py               # انتخاب داور + کاهش سوگیری (neutral / anonymized)
│   ├── prompts.py             # سیستم‌پرامپت‌های Draft / Critique / Judge
│   ├── gsc/                   # تحلیل Search Console (Strategy pattern)
│   │   ├── models.py          # GSCRow, Insight
│   │   ├── strategies.py      # quick_wins, low_ctr, high_impressions, declining, new_opportunities
│   │   └── analyzer.py        # GSCAnalyzer.render()
│   └── context/               # Brand Context قابل توسعه
│       ├── brand.py           # BrandContext (فیلدهای استراتژیک)
│       └── blocks.py          # ContextBlock protocol  ← قلاب RAG/Memory/Tools
└── merger.py                  # facade: run_seo_debate / arun_seo_debate
```

## جریان داده
1. `GSCAnalyzer.render(rows, prev_rows)` → جدول + Insightهای هر استراتژی
2. **Round 1 Draft** — `asyncio.gather` روی همه debaterها (موازی واقعی)
3. **Round 2 Critique** — `asyncio.gather`؛ هر مدل، draftهای رقبا را نقد می‌کند
4. **Round 3 Judge** — `JudgeStrategy` داور را انتخاب می‌کند:
   - اگر مدلی خارج از debaterها باشد (مثل Claude) → داورِ **بی‌طرف**
   - وگرنه → داورِ peer با **ناشناس‌سازی + بُر زدن** drafts (کاهش self-bias)
5. خروجی: `DebateResult.final_plan` + شفافیت کامل راندها

## نقاط توسعه (بدون Refactor هسته)
- **مدل جدید (Claude/DeepSeek/Grok):** فایل provider + `@register_provider` + یک import در `providers/__init__.py`.
- **لنز تحلیلی جدید GSC:** subclass از `GSCStrategy` + `@register_strategy`.
- **RAG / Memory / Tools:** بلاکی با `title()/render()` بساز و `brand.add_block(...)` کن؛
  یا یک `GSCStrategy`/استراتژی داور جدید تزریق کن. Orchestrator دست‌نخورده می‌ماند.
- **داور Ensemble:** کلاسی با متد `plan(...)` بنویس و به `DebateOrchestrator(judge_strategy=...)` بده.

## تست
`python smoke_test.py` — ۱۹ چک آفلاین (SDKها mock می‌شوند): موازی‌بودن async،
انتخاب داور، تاب‌آوری، retry/backoff، استراتژی‌های GSC، context و OCP.
