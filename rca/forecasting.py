import math
from typing import List, Dict, Any, Optional
from rca.history import HistoryStore

class ForecastModel:
    def __init__(self, version: str = "1.0.0"):
        self.version = version

    def predict_risk(self, history: List[Dict[str, Any]], scope: str = "system") -> Dict[str, Any]:
        """
        MVP Forecasting: Predicts 'low-verifiability' risk based on rolling trends.
        Higher risk if TSS is declining or missing critical signals are increasing.
        """
        relevant = [h for h in history if h["scope"] == scope][-5:] # Last 5 passes
        if not relevant:
            return {"risk_score": 0.0, "confidence": 0.0, "trend": "neutral", "version": self.version}

        # Features: TSS trend, missing signal stability, anomaly volatility
        tss_vals = [h["tss"] for h in relevant]
        missing_count = [h["missing_traces"] + h["missing_corr_ids"] + h["missing_metrics"] for h in relevant]
        
        # Simple weighted score
        avg_tss = sum(tss_vals) / len(tss_vals)
        latest_tss = tss_vals[-1]
        
        # Risk increases if latest TSS < avg TSS or missing signals exist
        risk_score = 0.0
        if latest_tss < 0.6: risk_score += 0.4
        if latest_tss < avg_tss: risk_score += 0.2
        if missing_count[-1] > 0: risk_score += 0.3
        
        risk_score = min(1.0, risk_score)
        
        return {
            "risk_score": round(risk_score, 2),
            "confidence": 0.7 if len(relevant) >= 3 else 0.4,
            "trend": "degrading" if latest_tss < avg_tss else "stable",
            "version": self.version,
            "horizon": "next 3 passes"
        }

def get_forecast(scope: str = "system") -> Dict[str, Any]:
    """Helper for inference."""
    store = HistoryStore()
    history = store.load_history()
    model = ForecastModel()
    return model.predict_risk(history, scope=scope)

def forecast_impact(incident: Dict[str, Any], topology: Dict[str, Any], claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Continuous Epistemic Falsifier (CEF) extension:
    Predicts verifiability risk based on current incident scope, inferred topology, 
    and established health claims.
    """
    # For MVP, we leverage the rolling trend history. 
    # Future versions can use incident features for more specific impact forecasting.
    return get_forecast(scope="system")
