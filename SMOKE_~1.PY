"""Offline test suite — no network, no real SDKs, no API keys."""
import sys, time, types, asyncio

# ── stub optional SDKs so module imports succeed ─────────────────────────
def _stub(name, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m

genai = _stub("google.generativeai", configure=lambda **k: None,
              types=types.SimpleNamespace(GenerationConfig=lambda **k: k),
              GenerativeModel=lambda *a, **k: None)
google_pkg = _stub("google"); google_pkg.generativeai = genai
_stub("openai", OpenAI=lambda **k: None)
_stub("anthropic", Anthropic=lambda **k: None)

import ai.providers  # triggers @register_provider for gemini/openai/claude
from ai.providers.base import LLMProvider, LLMResponse, ProviderConfig, TransientProviderError, ProviderError
from ai.providers.registry import (ProviderRegistry, register_provider, registered_providers)
from ai.debate.orchestrator import DebateOrchestrator
from ai.debate.context.brand import BrandContext
from ai.debate.gsc.analyzer import GSCAnalyzer
from ai.debate.gsc.strategies import all_strategy_keys

PASS = []
def check(name, cond):
    assert cond, f"FAILED: {name}"
    PASS.append(name); print(f"  ✓ {name}")

# ── fake provider ────────────────────────────────────────────────────────
class FakeProvider(LLMProvider):
    def __init__(self, name, delay=0.0, fail=False, fail_on_role=None,
                 transient_then_ok=0):
        super().__init__(ProviderConfig(api_key="x", model=f"{name}-m",
                                        max_retries=4, backoff_base=0.01, backoff_jitter=0))
        self.name = name; self.delay = delay; self.fail = fail
        self.fail_on_role = fail_on_role; self._left = transient_then_ok; self.calls = 0
    def _raw_generate(self, system, prompt, temperature, max_tokens):
        self.calls += 1
        if self.delay: time.sleep(self.delay)
        role = ("JUDGE" if "Judge" in system else "CRITIQUE" if "Audit" in system else "DRAFT")
        if self._left > 0:
            self._left -= 1; raise TransientProviderError("rate limit 429")
        if self.fail or role == self.fail_on_role:
            raise ProviderError("simulated hard failure")
        return f"### {role}:{self.name}\n| a | b |\n|---|---|\n" + "x"*220

GSC = [{"keys": ["خرید کفش"], "clicks": 5, "impressions": 1200, "ctr": 0.004, "position": 8.0},
       {"keys": ["کفش ورزشی"], "clicks": 40, "impressions": 800, "ctr": 0.05, "position": 2.1},
       {"keys": ["کتانی نایک"], "clicks": 2, "impressions": 300, "ctr": 0.006, "position": 15.0}]
PREV = [{"keys": ["خرید کفش"], "clicks": 30, "impressions": 1100, "ctr": 0.027, "position": 4.0}]
BRAND = BrandContext(brand_name="ت", niche="کفش", search_intent="خرید",
                     business_goals="فروش").add_text("حافظه (Memory)", "کاربر قبلا روی ریلز کلیک کرد")

def reg(*provs):
    r = ProviderRegistry()
    for p in provs: r.register(p.name, p)
    return r

# 1) OCP: decorator registered all three bundled providers
print("[1] provider registry OCP")
check("gemini/openai/claude auto-registered",
      set(["gemini","openai","claude"]).issubset(set(registered_providers())))
@register_provider
class _Deepseek(FakeProvider):
    name="deepseek"; requires_secret="DEEPSEEK_API_KEY"; default_model="ds"
    def __init__(self, cfg=None): super().__init__("deepseek")
check("new provider added with zero orchestrator change", "deepseek" in registered_providers())

# 2) async parallelism — 3 debaters x 0.2s must finish ~0.2s not ~0.6s
print("[2] async parallelism")
r = reg(FakeProvider("gemini", delay=0.2), FakeProvider("openai", delay=0.2), FakeProvider("claude", delay=0.2))
t0 = time.perf_counter()
res = DebateOrchestrator(r).run(GSC, BRAND)
elapsed = time.perf_counter() - t0
# draft round + critique round + judge ~ 3 sequential stages of 0.2 = ~0.6, NOT 1.8 (sequential per-provider)
check(f"parallel fan-out (elapsed={elapsed:.2f}s < 1.0s)", elapsed < 1.0 and res.ok)

# 3) neutral third-party judge
print("[3] judge selection")
r = reg(FakeProvider("gemini"), FakeProvider("openai"), FakeProvider("claude"))
res = DebateOrchestrator(r).run(GSC, BRAND, debater_keys=["gemini","openai"])
check("neutral third party judges", res.judge_key=="claude" and res.bias_mode=="neutral_third_party")

# 3b) anonymized peer when everyone debates
res = DebateOrchestrator(r).run(GSC, BRAND, debater_keys=["gemini","openai"] if False else None)
check("anonymized peer when no neutral", res.bias_mode=="anonymized_peer" and res.judge_key in res.participants)

# 4) degraded: one debater down
print("[4] resilience")
r = reg(FakeProvider("gemini"), FakeProvider("openai", fail=True), FakeProvider("claude"))
res = DebateOrchestrator(r).run(GSC, BRAND, debater_keys=["gemini","openai"])
check("one debater down -> degraded but ok", res.ok and res.degraded)

# 5) judge fails -> fallback to draft
r = reg(FakeProvider("gemini", fail_on_role="JUDGE"), FakeProvider("openai", fail_on_role="JUDGE"))
res = DebateOrchestrator(r).run(GSC, BRAND)
check("judge failure -> draft fallback", res.ok and res.error and "DRAFT" in res.final_plan)

# 6) no providers -> clean error
res = DebateOrchestrator(reg()).run(GSC, BRAND)
check("empty registry -> not ok, no crash", (not res.ok) and res.error)

# 7) retry + backoff on transient errors
print("[5] retry/backoff/timeout")
p = FakeProvider("gemini", transient_then_ok=2)
out = p.generate("sys", "prompt", role="draft")
check("retries transient then succeeds (attempts=3)", out.ok and out.attempts==3 and p.calls==3)
p2 = FakeProvider("openai", transient_then_ok=99)
out2 = p2.generate("sys","prompt")
check("gives up after max_retries -> ok=False", (not out2.ok) and out2.error)

# 8) GSC strategies extensible + period-over-period
print("[6] gsc strategies")
check("all 5 strategies registered",
      set(["quick_wins","low_ctr","high_impressions","declining","new_opportunities"]).issubset(set(all_strategy_keys())))
rendered = GSCAnalyzer().render(GSC, PREV)
check("quick win surfaced", "خرید کفش" in rendered and "Quick-win" in rendered)
check("low CTR surfaced", "CTR" in rendered)
check("declining detected via prev period", "افت" in rendered)
# subset selection works without touching orchestrator
only_low = GSCAnalyzer(strategy_keys=["low_ctr"]).render(GSC)
check("strategy subset selectable", "Quick-win" not in only_low)

# 9) brand context rich + extensible
print("[7] brand context")
txt = BRAND.render()
check("strategic fields rendered", "Search Intent" in txt and "اهداف کسب‌وکار" in txt)
check("extra block (future RAG/Memory) rendered", "حافظه (Memory)" in txt and "ریلز" in txt)
check("empty fields omitted", "Conversion" not in txt)

# 10) async API works directly
print("[8] async entrypoint")
r = reg(FakeProvider("gemini"), FakeProvider("openai"))
res = asyncio.run(DebateOrchestrator(r).arun(GSC, BRAND))
check("arun() produces a plan", res.ok)

print(f"\nALL {len(PASS)} CHECKS PASSED ✅")
