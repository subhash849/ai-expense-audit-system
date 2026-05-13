from ocr import get_ocr_text, is_blurry
from extractor import extract_text
from datetime import datetime
from rag import load_policy, chunk_text, build_index, retrieve
from storage import add_claim
import re

policy_text = load_policy("policy.pdf")   # make sure file exists
policy_chunks = chunk_text(policy_text)
index, embeddings = build_index(policy_chunks)

def convert_to_usd(amount, currency):
    rates = {
        "INR": 0.012,
        "USD": 1
    }
    return amount * rates.get(currency, 1)

def detect_category(purpose):
    purpose = purpose.lower()

    if any(word in purpose for word in ["lunch", "dinner", "food", "meal"]):
        return "meals"
    elif any(word in purpose for word in ["taxi", "uber", "transport"]):
        return "transport"
    elif any(word in purpose for word in ["hotel", "stay", "lodging"]):
        return "lodging"
    
    return "general"


 # 🔥 Date validation
def dates_match(receipt_date, claimed_date):

    # try parsing receipt date
    try:
        r_date = datetime.strptime(receipt_date, "%d-%b-%y")
    except:
        try:
            r_date = datetime.strptime(receipt_date, "%d-%m-%Y")
        except:
            return False

    # parse claimed date (UI format is fixed)
    try:
        c_date = datetime.strptime(claimed_date, "%Y-%m-%d")
    except:
        return False

    return r_date.date() == c_date.date()

def extract_limit(policy_text):
    match = re.search(r'\d+', policy_text)
    if match:
        return int(match.group())
    return None

def detect_prohibited(text, purpose):
    combined = (text + " " + purpose).lower()

    alcohol_words = [
        "beer", "wine", "whiskey", "vodka",
        "rum", "gin", "alcohol", "cocktail"
    ]

    if any(word in combined for word in alcohol_words):
        return "alcohol"
    
    return None

def save_and_return(final_output, purpose):
    claim_data = {
        "Merchant": final_output.get("Merchant"),
        "Amount": final_output.get("Amount"),
        "Currency": final_output.get("Currency"),
        "Date": final_output.get("Date"),
        "AI_Status": final_output.get("Status"),
        "Final_Status": final_output.get("Status"),
        "Reason": final_output.get("Reason"),
        "Policy": final_output.get("Policy", "N/A"),
        "Purpose": purpose,
        "Overridden": False,
        "Notification": f"Claim {final_output.get('Status')}",
        "Notified": False
    }

    add_claim(claim_data)
    return final_output


def process_receipt(image, purpose, claimed_date=None):

    if is_blurry(image):
        final_output = {
        "Merchant": None,
        "Amount": None,
        "Currency": None,
        "Date": None,
        "Status": "Flagged",
        "Reason": "Receipt image is blurry or unreadable",
        "Policy": "N/A"
        }

        return save_and_return(final_output, purpose)

    text = get_ocr_text(image)

    # 🔥 Prohibition check (before everything else)
    prohibited = detect_prohibited(text, purpose)

    if prohibited:
        query = f"{prohibited} reimbursement policy rule"
        policy = retrieve(query, policy_chunks, index, k=1)[0]

        final_output = {
            "Merchant": None,
            "Amount": None,
            "Currency": None,
            "Date": None,
            "Status": "Flagged",
            "Reason": f"{prohibited.capitalize()} expenses are not reimbursable",
            "Policy": policy
            }

        return save_and_return(final_output, purpose)

    if not text.strip():
        final_output = {
            "Merchant": None,
            "Amount": None,
            "Currency": None,
            "Date": None,
            "Status": "Flagged",
            "Reason": "Receipt image is blurry or unreadable",
            "Policy": "N/A"
            }

        return save_and_return(final_output, purpose)

    data = extract_text(text)

    # 🔥 RAG retrieval
    query = f"{purpose} expense reimbursement policy limit"
    results = retrieve(query, policy_chunks, index, k=3)

    category = detect_category(purpose)

    relevant_policy = ""
    for chunk in results:
        if category in chunk.lower():
            relevant_policy = chunk
            break

    if not relevant_policy:
        relevant_policy = results[0]
        
    # 🔥 Date validation (must come early)
    if not data.get("Date") or not data.get("Amount"):
        final_output = {
            "Merchant": None,
            "Amount": None,
            "Currency": None,
            "Date": None,
            "Status": "Flagged",
            "Reason": "date or amount not found",
            "Policy": "N/A"
            }

        return save_and_return(final_output, purpose)

    if claimed_date and not dates_match(data.get("Date"), claimed_date):
        final_output = {
            "Merchant": None,
            "Amount": None,
            "Currency": None,
            "Date": None,
            "Status": "Flagged",
            "Reason": "Claimed date does not match receipt date",
            "Policy": "N/A"
            }

        return save_and_return(final_output, purpose)

    limit = extract_limit(relevant_policy)
    amount = data.get("Amount")
    currency = data.get("Currency")

    amount_usd = convert_to_usd(amount, currency)
    # Default values (IMPORTANT)
    status = "Flagged"
    reason = "Unable to process expense"

    if limit is not None and amount is not None:
        if amount_usd > limit:
            status = "Rejected"
            reason = f"Amount {amount} exceeds allowed limit of {limit}"
        else:
            status = "Approved"
            reason = f"Amount {amount} is within allowed limit of {limit}"
    else:
        reason = "Could not determine policy limit or amount"

    # ✅ ALWAYS define final_output
    final_output = {
        "Merchant": data.get("Merchant") or "Unknown",
        "Amount": amount,
        "Currency": data.get("Currency"),
        "Date": data.get("Date") or "Not Found",
        "Status": status,
        "Reason": reason,
        "Policy": relevant_policy[:300] if relevant_policy else "Not found"
    }


    claim_data = {
        "Merchant": final_output["Merchant"],
        "Amount": final_output["Amount"],
        "Currency": final_output["Currency"],
        "Date": final_output["Date"],
        "AI_Status": final_output["Status"],
        "Final_Status": final_output["Status"],
        "Reason": final_output["Reason"],
        "Policy": final_output["Policy"],
        "Purpose": purpose,
        "Overridden": False,
        "Notification": f"Claim {final_output['Status']}",
        "Notified": False
    }

    add_claim(claim_data)

    return final_output


if __name__ == "__main__":
    image_path = input("enter the image path: ")
    purpose = input("enter your business purpose: ")

    output = process_receipt(image_path, purpose)

    print("\n =======result======")
    for key,value in output.items():
        print(f"{key}: {value}")

