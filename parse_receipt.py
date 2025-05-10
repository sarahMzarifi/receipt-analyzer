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

# Classification function
def classify_item(name: str) -> str:
    name = name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name:
                return category
    return "Other"

def extract_receipt_data(text):
    # Standardize all dates to dd-mm-yyyy
    date_patterns = [
        r'\d{2}[/-]\d{2}[/-]\d{4}',         # dd/mm/yyyy or mm/dd/yyyy
        r'\d{1,2}\s+\w{3,9},\s+\d{4}',      # 02 May, 2021
        r'\w{3,9}\s+\d{1,2},\s+\d{4}'       # May 2, 2021
    ]

    date_candidates = []
    for pattern in date_patterns:
        date_candidates += re.findall(pattern, text)

    extracted_date = "N/A"
    for candidate in date_candidates:
        try:
            parsed_date = parser.parse(candidate, fuzzy=True, dayfirst=True)  # Ensures dd-mm-yyyy is interpreted correctly
            extracted_date = parsed_date.strftime("%d-%m-%Y")
            break
        except Exception:
            continue

    lines = text.split('\n')
    items = []

    for line in lines:
        match = re.match(r"(.+?)\s+\$([0-9]+\.[0-9]{2})", line.strip())
        if match:
            name = match.group(1).strip()
            price = float(match.group(2))
            items.append({"name": name, "price": price})

    if not items:
        fallback_items = [
            {"name": "Subtotal", "price": float(re.search(r'Sub Total\s*[\$₹]?([0-9]+\.[0-9]{2})', text).group(1))} if re.search(r'Sub Total\s*[\$₹]?([0-9]+\.[0-9]{2})', text) else None,
            {"name": "CASH", "price": float(re.search(r'CASH\s*[\$₹]?([0-9]+\.[0-9]{2})', text).group(1))} if re.search(r'CASH\s*[\$₹]?([0-9]+\.[0-9]{2})', text) else None,
            {"name": "CHANGE", "price": float(re.search(r'CHANGE\s*[\$₹]?([0-9]+\.[0-9]{2})', text).group(1))} if re.search(r'CHANGE\s*[\$₹]?([0-9]+\.[0-9]{2})', text) else None
        ]
        items.extend([item for item in fallback_items if item])

    total_match = re.search(r'TOTAL\s*[\$₹]?([0-9]+\.[0-9]{2})', text, re.IGNORECASE)
    total = float(total_match.group(1)) if total_match else round(sum(i["price"] for i in items), 2)

    for item in items:
        item["category"] = classify_item(item["name"])

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