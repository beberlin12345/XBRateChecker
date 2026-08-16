import re
import json
import time

import requests

BASE_URL = "https://api.remitly.io/v3/calculator/estimate"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.remitly.com/",
    "Origin": "https://www.remitly.com",
}

# matches strings like "150BPS-1000CAP" inside the promo code
BPS_RE = re.compile(r"(\d+)BPS")


def _parse_bps(promo_code: str):
    if not promo_code:
        return None
    match = BPS_RE.search(promo_code)
    return float(match.group(1)) if match else None


def get_quote(conduit: str, amount: float, pay_out_method: str = "BANK_DEPOSIT", max_retries: int = 3):
    """
    conduit: e.g. "USA:USD-MEX:MXN"
    amount: send amount in whole USD
    pay_out_method: which estimate to pull from pay_out_price_estimates
                    (falls back to the top-level estimate if not found)
    max_retries: number of retry attempts on 429, with increasing backoff
    Returns a dict matching the snapshots schema, or None on failure.
    """
    params = {
        "conduit": conduit,
        "anchor": "SEND",
        "amount": amount,
        "purpose": "OTHER",
        "customer_segment": "STANDARD",
        "customer_recognition": "UNRECOGNIZED",
        "strict_promo": "false",  # false = surface promo fields if eligible
    }

    resp = None
    for attempt in range(max_retries + 1):
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            break
        if resp.status_code == 429 and attempt < max_retries:
            wait = 15 * (attempt + 1)  # 15s, 30s, 45s
            print(f"[remitly] 429 on attempt {attempt + 1}, waiting {wait}s before retry")
            time.sleep(wait)
            continue
        break

    if resp.status_code != 200:
        print(f"[remitly] {resp.status_code} for {conduit} @ {amount}: {resp.text[:200]}")
        return None

    data = resp.json()
    estimate = data.get("estimate", {})

    # look for the requested payout method among the alternatives, default to top-level estimate
    chosen = estimate
    for alt in data.get("pay_out_price_estimates", {}).get("estimates", []):
        if alt.get("pay_out_method") == pay_out_method:
            chosen = alt
            break

    exch = chosen.get("exchange_rate", {})
    fee = chosen.get("fee", {})
    discount = chosen.get("discount", {})

    standard_rate = float(exch["base_rate"]) if exch.get("base_rate") else None
    welcome_rate = (
        float(exch["promotional_exchange_rate"])
        if exch.get("promotional_exchange_rate")
        else None
    )
    welcome_cap = (
        float(exch["capped_promotional_exchange_rate_amount"])
        if exch.get("capped_promotional_exchange_rate_amount")
        else None
    )

    send_amount = float(chosen["send_amount"])
    receive_amount = float(chosen["receive_amount"])
    effective_rate = receive_amount / send_amount if send_amount else None

    total_fee = float(fee["total_fee_amount"]) if fee.get("total_fee_amount") else None
    fee_discount = (
        float(discount["fee_discount_amount"]) if discount.get("fee_discount_amount") else 0.0
    )
    net_fee = (total_fee - fee_discount) if total_fee is not None else None

    disclaimer = data.get("disclaimer", {}).get("primary", "") or ""
    promo_code_match = re.search(r"\[.*?\]\((.*?promo_code=([\w-]+))\)", disclaimer)
    promo_code = promo_code_match.group(2) if promo_code_match else None
    promo_bps = _parse_bps(promo_code)

    return {
        "provider": "remitly",
        "corridor": conduit,
        "send_amount": send_amount,
        "receive_amount": receive_amount,
        "standard_rate": standard_rate,
        "welcome_rate": welcome_rate,
        "welcome_cap_usd": welcome_cap,
        "effective_rate": effective_rate,
        "fee": total_fee,
        "fee_discount": fee_discount,
        "net_fee": net_fee,
        "total_charge": float(chosen["total_charge_amount"]),
        "pay_out_method": chosen.get("pay_out_method"),
        "promo_code": promo_code,
        "promo_bps": promo_bps,
        "raw_response": json.dumps(data),
    }
