import json
import os

FILE_PATH = "claims.json"


def load_claims():
    if not os.path.exists(FILE_PATH):
        return []
    
    with open(FILE_PATH, "r") as f:
        return json.load(f)


def save_claims(claims):
    with open(FILE_PATH, "w") as f:
        json.dump(claims, f, indent=4)


def add_claim(claim):
    claims = load_claims()

    # assign ID
    claim["id"] = len(claims) + 1

    claims.append(claim)
    save_claims(claims)


def update_claim(claim_id, updated_data):
    claims = load_claims()

    for claim in claims:
        if claim["id"] == claim_id:
            claim.update(updated_data)
            break

    save_claims(claims)