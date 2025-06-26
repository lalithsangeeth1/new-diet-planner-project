from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# Set the path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🖼️ Function to extract ingredients from images (JPG, PNG)
def extract_ingredients_from_receipt(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    lines = text.split('\n')
    return [line.strip() for line in lines if line.strip()]

# 📄 Function to extract ingredients from PDFs
def extract_ingredients_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)
        full_text += text + "\n"

    lines = full_text.split('\n')
    return [line.strip() for line in lines if line.strip()]
