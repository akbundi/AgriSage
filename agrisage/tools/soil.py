
from typing import Dict, Any

class SoilTool:
    def interpret(self, soil_card: Dict[str, Any]) -> Dict[str, Any]:
        ph = soil_card.get("ph", 7.0)
        n = soil_card.get("n", "medium")
        p = soil_card.get("p", "medium")
        k = soil_card.get("k", "medium")
        tips = []
        if ph < 6.0:
            tips.append("Soil is acidic; consider liming.")
        if ph > 7.8:
            tips.append("Alkaline soil; prefer sulfur-based amendments and organic matter.")
        for nutrient, level in [("N", n), ("P", p), ("K", k)]:
            if str(level).lower() == "low":
                tips.append(f"{nutrient} is low; adjust fertilization schedule accordingly.")
        return {"summary": {"ph": ph, "n": n, "p": p, "k": k}, "advice": tips or ["Soil is balanced; follow standard fertigation."]}
