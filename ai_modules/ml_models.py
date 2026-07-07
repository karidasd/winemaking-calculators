import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def predict_fermentation_curve(historical_data, current_brix, target_brix=0.0):
    """
    Predicts the fermentation curve using Polynomial Regression based on recent readings.
    historical_data: List of dicts [{'day': int, 'brix': float}, ...]
    """
    if len(historical_data) < 2:
        return {"error": "Need at least 2 data points for prediction."}

    # Prepare data
    X = np.array([d['day'] for d in historical_data]).reshape(-1, 1)
    y = np.array([d['brix'] for d in historical_data])

    # For wine fermentation, a polynomial degree 2 fits well usually (starts slow, drops fast, slows down at end)
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y)

    # Predict future days
    last_day = max(X)[0]
    future_days = np.arange(last_day + 1, last_day + 20).reshape(-1, 1)
    future_days_poly = poly.transform(future_days)
    predictions = model.predict(future_days_poly)

    # Find when it hits target brix
    curve = []
    days_to_dry = None
    for day, pred in zip(future_days.flatten(), predictions):
        curve.append({"day": int(day), "brix": round(float(pred), 2)})
        if pred <= target_brix and days_to_dry is None:
            days_to_dry = int(day)
            break
        # Stop predicting if it starts going up (bad poly fit)
        if len(curve) > 1 and curve[-1]['brix'] > curve[-2]['brix']:
            break

    # Calculate stuck fermentation risk (if rate of drop is too slow)
    recent_drop_rate = y[-2] - y[-1] if len(y) >= 2 else 1.0
    risk = "Low"
    if recent_drop_rate < 0.3 and current_brix > 5.0:
        risk = "High"
    elif recent_drop_rate < 0.6 and current_brix > 5.0:
        risk = "Medium"

    return {
        "days_to_dry_total": days_to_dry,
        "days_remaining": days_to_dry - last_day if days_to_dry else None,
        "stuck_risk": risk,
        "projected_curve": curve
    }
