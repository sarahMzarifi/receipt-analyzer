import cv2
import pytesseract
from preprocess import binarize
from parse_receipt import extract_receipt_data, save_to_json
import platform

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # for most Linux servers


def process_receipt(image_path):
    original_image = cv2.imread(image_path)

    if original_image is None:
        raise ValueError(f"Error: Cannot read image at {image_path}")

    # Preprocess image
    preprocessed_image = binarize(original_image)

    custom_config = r'--oem 3 --psm 6'

    # BOTH OCR outputs
    raw_text = pytesseract.image_to_string(original_image, config=custom_config)
    processed_text = pytesseract.image_to_string(preprocessed_image, config=custom_config)

    # Debug output
    print("\n--- RAW OCR TEXT ---\n")
    print(raw_text)

    print("\n--- PROCESSED OCR TEXT ---\n")
    print(processed_text)

    # Use processed text
    text = processed_text

    # Parse structured data
    receipt_data = extract_receipt_data(text)

    # Ensure categories exist
    for item in receipt_data.get("items", []):
        if "category" not in item:
            item["category"] = "Uncategorized"

    return receipt_data

if __name__ == "__main__":
    image_path = "sample5.png"  # For standalone testing
    try:
        receipt_data = process_receipt(image_path)

        # Print structured receipt info
        print("\nParsed Receipt Data:")
        for item in receipt_data["items"]:
            print(f"- {item['name']}: ₹{item['price']:.2f} ({item['category']})")
        print(f"\nDate: {receipt_data['date']}")
        print(f"Total: ₹{receipt_data['total']:.2f}")

        # Save to JSON
        save_to_json(receipt_data, filename="receipts.json")

    except Exception as e:
        print("Error:", str(e))
