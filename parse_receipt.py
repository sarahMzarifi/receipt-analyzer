import json
import re
from dateutil import parser  # For flexible date parsing

# Define category keywords
CATEGORY_KEYWORDS = {
    "Food": ["milk", "bread", "cheese", "apples", "chips","chicken","dal","biryani","drinks", "oats", "bean","roti", "fruit"],
    "Transport": ["uber","cab","taxi", "bus", "train", "fuel", "toll"],
    "Groceries": ["vegetable", "grocery", "flour", "snack"],
    "Entertainment": ["movie", "netflix", "spotify", "ticket", "game"],
    "Utilities": ["electricity", "telephone","water", "gas", "internet"],
    "Taxes": ["cgst","sgst","subtotal"],
    "Luxury":["note","phone","headphone","charger","pen drive"],
    "Miscellaneous": ["Lorem"]
}

# 🔹 NEW: Basic word correction
def correct_common_words(name):
    corrections = {
        "bonanas": "bananas",
        "frosh": "fresh",
        "mitk": "milk",
        "juke": "juice",
        "loat": "loaf",
        "rganic": "organic"
    }

    words = name.lower().split()
    corrected = [corrections.get(w, w) for w in words]
    return " ".join(corrected).title()

# Classification function
def classify_item(name: str) -> str:
    name = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name:
                return category
    return "Other"

def extract_receipt_data(text):

    # ---------------- DATE EXTRACTION ----------------
    date_patterns = [
        r'\d{2}[/-]\d{2}[/-]\d{4}',
        r'\d{1,2}\s+\w{3,9},\s+\d{4}',
        r'\w{3,9}\s+\d{1,2},\s+\d{4}'
    ]

    date_candidates = []
    for pattern in date_patterns:
        date_candidates += re.findall(pattern, text)

    extracted_date = "N/A"
    for candidate in date_candidates:
        try:
            parsed_date = parser.parse(candidate, fuzzy=True, dayfirst=True)
            extracted_date = parsed_date.strftime("%d-%m-%Y")
            break
        except Exception:
            continue

    # ---------------- ITEM EXTRACTION ----------------
    lines = text.split('\n')
    items = []

    for line in lines:
        line = line.strip()

        # Clean OCR noise
        line = re.sub(r'[^\w\s₹$.]', '', line)
        line = line.replace('O', '0')

        print("Processing line:", line)

        # Skip irrelevant lines
        if any(word in line.lower().replace('0','o') for word in [
            "address", "phone", "receipt", "customer", "name",
            "description", "quantity", "price", "amount",
            "details", "detais", "deta", "bill"
        ]):
            continue

        # Extract ALL numbers
        numbers = re.findall(r'[\$₹]?([0-9]+(?:\.[0-9]{2})?)', line)

        if numbers:
            raw_num = numbers[-1]
            price = float(raw_num)

            # Decimal correction
            if price > 100 and "." not in raw_num:
                if len(raw_num) >= 3:
                    price = float(raw_num[:-2] + "." + raw_num[-2:])

            # Extract name
            name = re.sub(r'[\$₹]?[0-9]+(?:\.[0-9]{2})?', '', line).strip()

            # Basic cleanup
            name = name.replace("0", "o")
            name = re.sub(r'\b[bI1]+\b', '', name)
            name = re.sub(r'\s+', ' ', name).strip()

            # 🔹 Apply word correction
            name = correct_common_words(name)

            # Skip totals
            clean_name = name.lower().replace('0','o')
            if any(word in clean_name for word in [
                "total", "subtotal", "subttal", "ttal",
                "tax", "discount", "ciscunt"
            ]):
                continue

            if len(name) > 2:
                items.append({
                    "name": name,
                    "price": price,
                    "source_line": line
                })

    # ---------------- FALLBACK ----------------
    if not items:
        print("No items detected — using fallback extraction")

        fallback_items = [
            {"name": "Subtotal", "price": float(re.search(r'Sub\s*Total\s*[\$₹]?([0-9]+(?:\.[0-9]{2})?)', text).group(1))}
            if re.search(r'Sub\s*Total\s*[\$₹]?([0-9]+(?:\.[0-9]{2})?)', text) else None,

            {"name": "CASH", "price": float(re.search(r'CASH\s*[\$₹]?([0-9]+(?:\.[0-9]{2})?)', text).group(1))}
            if re.search(r'CASH\s*[\$₹]?([0-9]+(?:\.[0-9]{2})?)', text) else None,

            {"name": "CHANGE", "price": float(re.search(r'CHANGE\s*[\$₹]?([0-9]+(?:\.[0-9]{2})?)', text).group(1))}
            if re.search(r'CHANGE\s*[\$₹]?([0-9]+(?:\.[0-9]{2})?)', text) else None
        ]

        items.extend([item for item in fallback_items if item])

    # ---------------- TOTAL EXTRACTION ----------------
    total_matches = re.findall(r'TOTAL\s*[\$₹]?([0-9]+(?:\.[0-9]{2})?)', text, re.IGNORECASE)

    if total_matches:
        total = float(total_matches[-1])
    else:
        total = round(sum(i["price"] for i in items), 2)

    # ---------------- CLASSIFICATION ----------------
    for item in items:
        item["category"] = classify_item(item["name"])

    # ---------------- FINAL STRUCTURE ----------------
    receipt_data = {
        "date": extracted_date,
        "items": items,
        "total": total
    }

    return receipt_data


def save_to_json(data, filename='receipts.json'):
    try:
        with open(filename, 'r') as file:
            receipts = json.load(file)
    except FileNotFoundError:
        receipts = []

    receipts.append(data)

    with open(filename, 'w') as file:
        json.dump(receipts, file, indent=4)