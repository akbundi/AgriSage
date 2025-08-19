
from typing import Dict, List, Any

class PolicyTool:
    _schemes = [
        {"name": "PM-KISAN", "type": "income-support", "eligibility": ["Small/Marginal farmer", "Owns cultivable land"], "benefit": "₹6,000/year in 3 installments"},
        {"name": "KCC (Kisan Credit Card)", "type": "credit", "eligibility": ["Cultivator", "Tenant/Sharecropper eligible"], "benefit": "Short-term credit at concessional rate"},
        {"name": "PMFBY (Crop Insurance)", "type": "insurance", "eligibility": ["Notified crops and districts"], "benefit": "Risk coverage for yield loss"},
        {"name": "Soil Health Card", "type": "advisory", "eligibility": ["All farmers"], "benefit": "Soil testing + nutrient recommendation"},
    ]

    def match(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        out = []
        for s in self._schemes:
            score = 0
            if s["name"] == "PM-KISAN" and profile.get("land_owner", False):
                score += 2
            if s["name"] == "KCC (Kisan Credit Card)" and profile.get("cultivator", True):
                score += 2
            if s["name"] == "PMFBY (Crop Insurance)" and profile.get("notified_district", True):
                score += 1
            if s["name"] == "Soil Health Card":
                score += 1
            if score > 0:
                o = dict(s)
                o["fit_score"] = score
                out.append(o)
        out.sort(key=lambda x: x["fit_score"], reverse=True)
        return out
