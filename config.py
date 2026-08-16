"""
Central config for corridors and amount tiers.
Add new corridors here once you've confirmed the conduit string in dev tools.
"""

# amount tiers in USD, chosen to straddle known promo caps (1000 for MXN, 1500 for EUR)
AMOUNT_TIERS = [200, 1000, 2500, 5000, 10000]

# corridor: (remitly_conduit, wise source/target, label)
CORRIDORS = {
    "USD-MXN": {
        "remitly_conduit": "USA:USD-MEX:MXN",
        "wise_source": "USD",
        "wise_target": "MXN",
    },
    "USD-EUR": {
        "remitly_conduit": None,  # TODO: confirm exact conduit string via dev tools (Spain vs generic EUR)
        "wise_source": "USD",
        "wise_target": "EUR",
    },
}

DB_PATH = "remittance_tracker.db"
