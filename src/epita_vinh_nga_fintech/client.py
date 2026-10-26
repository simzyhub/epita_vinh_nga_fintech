import requests
from epita_vinh_nga_fintech.config import config

def fetch_live_data() -> dict:
    config.validate()
    url = "https://api.stripe.com/v1/balance"
    headers = {"Authorization": f"Bearer {config.api_key}"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    avail = data.get("available", [{}])[0]
    return {
        "status": "LIVE_SUCCESS",
        "currency": avail.get("currency", "usd").upper(),
        "available_balance": avail.get("amount", 0) / 100.0,
        "livemode": data.get("livemode", False)
    }
