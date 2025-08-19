
from typing import Dict, Any, List
from pydantic import BaseModel
from .rag_store import MiniVectorStore, Doc
from .tools.weather import WeatherTool
from .tools.market import MarketTool
from .tools.policy import PolicyTool
from .tools.soil import SoilTool

SUPPORTED_LANG_HINTS = {
    "hi": ["कब", "सिंचाई", "बीज", "कीमत", "योजना", "कर्ज", "बारिश", "ठंड"],
    "en": ["when", "irrigate", "seed", "price", "scheme", "loan", "rain", "frost"],
}

def detect_language(text: str) -> str:
    lower = text.lower()
    for lang, hints in SUPPORTED_LANG_HINTS.items():
        for h in hints:
            if h in lower:
                return lang
    return "en"

def classify_intent(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["irrigate", "irrigation", "सिंचाई"]):
        return "irrigation"
    if any(k in t for k in ["frost", "temperature", "ठंड"]):
        return "frost_risk"
    if any(k in t for k in ["price", "mandi", "sell", "बेचना", "कीमत"]):
        return "market"
    if any(k in t for k in ["scheme", "subsidy", "loan", "kcc", "policy", "योजना", "कर्ज"]):
        return "policy"
    if any(k in t for k in ["soil", "npk", "ph", "soil card"]):
        return "soil"
    return "general"

class AgentResponse(BaseModel):
    answer: str
    intent: str
    language: str
    confidence: float
    citations: List[Dict[str, Any]]
    steps: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]
    raw: Dict[str, Any]

class AgriAgent:
    def __init__(self, store: MiniVectorStore):
        self.store = store
        self.weather = WeatherTool()
        self.market = MarketTool()
        self.policy = PolicyTool()
        self.soil = SoilTool()

    def _retrieve(self, query: str, k: int = 4):
        return [d for d, _ in self.store.top_k(query, k)]

    def _citations(self, docs):
        cits = []
        for d in docs:
            cits.append({"id": d.id, "title": d.meta.get("title", d.id), "source": d.meta.get("source", "local"), "snippet": d.text[:200]})
        return cits

    def _conf_from_evidence(self, signals):
        if not signals:
            return 0.55
        base = min(0.95, max(0.4, sum(signals) / len(signals)))
        return round(base, 2)

    def answer(self, query: str, context: Dict[str, Any]) -> AgentResponse:
        lang = detect_language(query)
        intent = classify_intent(query)
        steps = [f"Detected language={lang}", f"Classified intent={intent}"]
        retrieved = self._retrieve(query, k=4)
        citations = self._citations(retrieved)
        steps.append(f"Retrieved {len(retrieved)} documents for grounding")

        location = context.get("location", "Sikar, Rajasthan")
        crop = context.get("crop", "wheat")
        stage = context.get("stage", "vegetative")
        district = context.get("district", "Sikar")
        soil_card = context.get("soil_card")
        profile = context.get("profile", {"land_owner": True, "cultivator": True, "notified_district": True})

        raw = {}
        warnings = []
        signals = []

        if intent == "irrigation":
            fc = self.weather.forecast(location)
            hint = self.weather.irrigation_hint(crop=crop, stage=stage, forecast=fc)
            if hint["action"] == "delay":
                answer = "Delay irrigation by ~24–48h due to near-term rain risk."
                signals.append(0.8)
            elif hint["action"] == "increase":
                answer = "Increase irrigation frequency slightly due to upcoming heat stress."
                signals.append(0.75)
            else:
                answer = "Maintain normal irrigation schedule; monitor soil moisture."
                signals.append(0.65)
            answer += f" (Crop: {crop}, Stage: {stage}, Location: {location})"
            raw.update({"forecast": fc, "irrigation_hint": hint})

        elif intent == "frost_risk":
            fc = self.weather.forecast(location)
            is_frost = self.weather.frost_risk(fc)
            answer = ("Frost risk likely; protect sensitive crops with mulching/cover and avoid late-evening irrigation."
                      if is_frost else "No significant frost risk in the next 7 days based on current forecast.")
            raw.update({"forecast": fc, "frost": is_frost})
            signals.append(0.7 if is_frost else 0.6)

        elif intent == "market":
            pb = self.market.price_band(commodity=crop, district=district)
            strat = self.market.hold_or_sell(pb)
            answer = f"{strat['recommendation']}. Rationale: {strat['rationale']} (Est. band in {district}: {pb['min']}–{pb['max']} {pb['unit']})."
            raw.update({"price_band": pb, "strategy": strat})
            signals.append(0.65)

        elif intent == "policy":
            schemes = self.policy.match(profile)
            if not schemes:
                answer = "No obvious scheme matches found. Check your local CSC/Bank for assistance."
                signals.append(0.5)
            else:
                top = schemes[:3]
                bullets = [f"- {s['name']} ({s['type']}): {s['benefit']}" for s in top]
                answer = "Likely eligible schemes:\n" + "\n".join(bullets)
                signals.append(0.7)
            raw.update({"schemes": schemes})

        elif intent == "soil" and soil_card:
            interp = self.soil.interpret(soil_card)
            answer = f"Soil summary: pH={interp['summary']['ph']}, N={interp['summary']['n']}, P={interp['summary']['p']}, K={interp['summary']['k']}."
            answer += " Advice: " + " ".join(interp["advice"])
            raw.update({"soil_interpretation": interp})
            signals.append(0.7)

        else:
            text_bits = [d.text for d in retrieved[:2]]
            base = text_bits[0] if text_bits else "I can assist with irrigation, seed choices, frost risk, market timing, and scheme eligibility."
            answer = base + " For precise help, provide district, crop, and stage."
            signals.append(0.55)

        if retrieved:
            signals.append(0.05)
        confidence = self._conf_from_evidence(signals)

        if intent in {"irrigation", "frost_risk", "market"}:
            warnings.append("Validate critical actions with local agri officer/FPO; conditions can change quickly.")

        return AgentResponse(answer=answer, intent=intent, language=lang, confidence=confidence, citations=citations, steps=steps, warnings=warnings, metrics={"retrieved_docs": len(retrieved)}, raw=raw)
