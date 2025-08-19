import hashlib
from typing import Dict, Any

class MarketTool:
    _avg = {
        "wheat": (18.0, 24.0),
        "paddy": (14.0, 22.0),
        "onion": (10.0, 30.0),
        "tomato": (6.0, 20.0),
        "soybean": (25.0, 45.0),
    }

    def price_band(self, commodity: str, district: str) -> Dict[str, Any]:
        base = self._avg.get(commodity.lower(), (12.0, 20.0))
        shift = ((int(hashlib.md5(district.encode()).hexdigest(), 16) % 500) - 250) / 100.0
        lo = max(2.0, base[0] + shift)
        hi = max(lo + 1.5, base[1] + shift)
        return {"commodity": commodity, "district": district, "min": round(lo, 2), "max": round(hi, 2), "unit": "₹/kg", "source": "MOCK_MARKET"}

    def hold_or_sell(self, price_band: Dict[str, Any], storage_cost_per_week: float = 0.5) -> Dict[str, Any]:
        spread = price_band["max"] - price_band["min"]
        if spread > (storage_cost_per_week + 3.0):
            return {"recommendation": "Consider holding 5–7 days if storage is safe", "rationale": f"Potential upside ≈ ₹{spread:.1f}/kg vs. storage ≈ ₹{storage_cost_per_week:.1f}/kg"}
        return {"recommendation": "Sell within 48–72 hours", "rationale": "Limited upside vs. storage costs / spoilage risk"}
