# agrisage/tools/weather.py
import hashlib
from typing import Dict, Any

class WeatherTool:
    """Mock weather tool — replace with IMD / OpenWeather integration."""

    def forecast(self, location: str) -> Dict[str, Any]:
        seed = int(hashlib.sha256(location.encode()).hexdigest(), 16) % 7
        days = []
        for i in range(7):
            tmin = 16 + ((seed + i) % 6)
            tmax = 28 + ((seed * 2 + i) % 8)
            rain = ((seed + 3 * i) % 10) / 10.0
            days.append({"day": i + 1, "tmin": tmin, "tmax": tmax, "rain_prob": round(rain, 2)})
        return {"location": location, "days": days, "source": "MOCK_WEATHER"}

    def irrigation_hint(self, crop: str, stage: str, forecast: Dict[str, Any]) -> Dict[str, Any]:
        risk_notes = []
        days = forecast["days"]
        rain_next2 = sum(1 for d in days[:2] if d["rain_prob"] > 0.6)
        hot_next3 = sum(1 for d in days[:3] if d["tmax"] >= 34)
        action = "normal"
        if rain_next2 >= 1:
            action = "delay"
            risk_notes.append("High chance of rain soon; irrigation can be delayed 24–48h.")
        if hot_next3 >= 2:
            if action == "delay":
                risk_notes.append("Heat may stress plants; monitor soil moisture closely.")
            else:
                action = "increase"
                risk_notes.append("Upcoming heat; consider increasing irrigation frequency.")
        return {"action": action, "notes": risk_notes}

    def frost_risk(self, forecast: Dict[str, Any]) -> bool:
        return any(d["tmin"] <= 5 for d in forecast["days"])
