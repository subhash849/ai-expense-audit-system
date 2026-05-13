import pytesseract
import cv2
from pdf2image import convert_from_path
import numpy as np
import easyocr
from PyPDF2 import PdfReader

reader = easyocr.Reader(['en'], gpu=False)

def extract_pdf_text(path):
        pdf_reader = PdfReader(path)
        text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted

        return text

def preprocess_image(img):
    height, width = img.shape[:2]

    if width < 1000:
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 🔥 Add this
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    return thresh


def is_blurry(image_path, threshold=100):

    img = None  # 👈 initialize

    if ".pdf" in image_path.lower():
        pages = convert_from_path(image_path, dpi=300)

        if not pages:
            return True

        img = np.array(pages[0])

    else:
        img = cv2.imread(image_path)

    if img is None:
        return True  # treat as blurry/unreadable

    gray = preprocess_image(img)

    variance = cv2.Laplacian(gray, cv2.CV_64F).var()

    return variance < threshold


def get_ocr_text(image_path):
    print("FILE PATH:", image_path)

    if ".pdf" in image_path.lower():

    # 🔥 STEP 1: Try direct text extraction
        text = extract_pdf_text(image_path)

        if len(text.strip()) > 30:
            print("✅ Using direct PDF text extraction")
            print("\n===== PDF TEXT =====\n", text, "\n====================\n")
            return text

        # 🔥 STEP 2: Fallback to OCR
        print("⚠️ No text layer → using OCR")

        pages = convert_from_path(image_path, dpi=300)
        text = ""

        for page in pages:
            img = np.array(page)
            gray = preprocess_image(img)

            tesseract_text = pytesseract.image_to_string(gray)

            if len(tesseract_text.strip()) < 30:
                print("⚠️ Tesseract weak → using EasyOCR")
                result = reader.readtext(img)
                text += " ".join([r[1] for r in result])
            else:
                text += tesseract_text

        return text
    
    else:
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError("Image not found or path is incorrect")

        gray = preprocess_image(img)

        tesseract_text = pytesseract.image_to_string(gray)

        if len(tesseract_text.strip()) < 30:
            print("⚠️ Tesseract weak → using EasyOCR")
            result = reader.readtext(img)
            text = " ".join([r[1] for r in result])
        else:
            text = tesseract_text

        print("\n===== OCR TEXT =====\n", text, "\n====================\n")

        return text