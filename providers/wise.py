"""
Wise provider module — STUB.

Wise does have a public comparisons page (wise.com/us/compare/send-money) that's
worth checking in dev tools the same way you did for Remitly: open Network tab,
change source/target/amount, and look for the XHR/fetch call it fires.

Historically Wise has exposed something like:
    GET https://wise.com/gateway/v3/comparisons?sourceCurrency=USD&targetCurrency=EUR&sendAmount=5000

...but endpoint paths and params change, so confirm the real one yourself before
trusting this. Once confirmed, fill in get_quote() to match the pattern used in
providers/remitly.py so collect.py can call it the same way.
"""

import json

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def get_quote(source_currency: str, target_currency: str, amount: float):
    """
    Returns a dict matching the snapshots schema, or None on failure.
    TODO: confirm real endpoint + response shape via dev tools, then implement.
    """
    raise NotImplementedError(
        "Confirm Wise's actual comparison endpoint in dev tools, "
        "then fill in this function using providers/remitly.py as a template."
    )
