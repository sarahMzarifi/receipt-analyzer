import cv2
import pytesseract
from preprocess import binarize
from parse_receipt import extract_receipt_data, save_to_json

# Set Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
def process_receipt(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Error: Cannot read image at {image_path}")

    # Preprocess the image
    image = binarize(image)

    # OCR text extraction
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)

    print("\nExtracted Text:\n")
    print(text)

    # Parse the extracted text into structured data
    receipt_data = extract_receipt_data(text)

    # Ensure each item has a category (optional feature support)
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
