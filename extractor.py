import re

def extract_amount_and_currency(text):
    lines  = text.split("\n")

    final_amount = None
    currency = None

    currency_symbol = {
        "$": "USD",
        "Rs.": "INR",
        "₹": "INR",
        "€": "EUR"
    }

        
    for line in reversed(lines):
        clean_line = line.lower().strip()

        if not clean_line:
            continue

        if re.search(r'\btotal\b', clean_line) and "rs" in clean_line and not any(word in clean_line for word in ["tax", "gst", "cgst", "sgst"]):

            numbers = re.findall(r'\d[\d,]*\.\d+', clean_line)
            cleaned_numbers = [float(n.replace(",", "")) for n in numbers]

            if cleaned_numbers:
                return max(cleaned_numbers), "INR"

        if any(word in clean_line for word in ["tax", "subtotal", "discount", "cgst", "sgst", "igst", "rate", "value"]):
            continue

        if ("total" in clean_line or "balance" in clean_line) and not any(word in clean_line for word in ["tax", "gst", "cgst", "sgst", "subtotal"]):

            # currency detection
            for symbol in currency_symbol:
                if symbol in clean_line:
                    currency = currency_symbol[symbol]

            if "rs" in clean_line:
                currency = "INR"

            if not currency:
                currency = "INR"

            clean_line = clean_line.replace(")", "").replace("(", "")
            numbers = re.findall(r'-?\d[\d,]*\.\d+|-?\d[\d,]*', clean_line)

            cleaned_numbers = []
            for num in numbers:
                num = num.replace(",", "")
                try:
                    cleaned_numbers.append(float(num))
                except:
                    continue

            if cleaned_numbers:
                final_amount = max(cleaned_numbers)
                return final_amount, currency   

    
    #fallback
    numbers = re.findall(r'-?\d[\d,]*\.\d+|-?\d[\d,]*', text)

    cleaned_numbers = []
    for num in numbers:
        num_clean = num.replace(",", "")
        try:
            val = float(num_clean)

            if val < 10:
                continue

            cleaned_numbers.append(val)

        except:
            continue

    if cleaned_numbers:
        final_amount = max(cleaned_numbers)
    
    return final_amount, currency



def extract_text(text):
    lines = text.split("\n")
    clean_text = re.sub(r'\s+', ' ', text)
    

    ignore_words = ["invoice","tax","bill","receipt"]

    final_amount = None
    date_match = None
    currency = None
    merchant = None

    # merchant detection
    for line in lines[:5]:
        clean_line = line.strip()
        clean_lower = clean_line.lower()

        if not clean_line:
            continue

        # 🔥 improved ignore logic
        if any(word in clean_lower for word in ignore_words):
            continue

        merchant = clean_line
        break

    # 🔥 fallback
    if not merchant:
        merchant = "Unknown"

    final_amount, currency =  extract_amount_and_currency(text)

        # Extract date using regex pattern (dd/mm/yyyy or dd-mm-yyyy)
    date = None

    # 🔥 format: 27-Feb-26
    date_match = re.search(
        r'\d{1,2}[-/](Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/]\d{2,4}',
        text,
        re.IGNORECASE
    )

    # fallback: 12-05-2025
    if not date_match:
        date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)

    # fallback: 12 May 2025
    if not date_match:
        date_match = re.search(
            r'\d{1,2}\s+(Jan|Feb|...)[a-z]*\s+\d{2,4}',
            text,
            re.IGNORECASE
        )


    if date_match:
        date = date_match.group()
        
    return {
        "Merchant": merchant,
        "Currency": currency,
        "Amount": final_amount,
        "Date": date
    }