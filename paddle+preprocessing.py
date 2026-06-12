import os
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT'] = '0'

import cv2
import pypdfium2 as pdfium
import numpy as np
from paddleocr import PaddleOCR
from rapidfuzz import fuzz

ocr = PaddleOCR(lang='en')

TARGET = "algae"
REJECT_WORDS = {"gage"}

def clean_word(word):
    return (
        str(word)
        .lower()
        .strip()
        .strip(".,;:-_()[]{}")
    )

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Mild contrast improvement
    gray = cv2.equalizeHist(gray)

    # Convert back to RGB for Paddle
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

def get_detected_words(prediction_output):
    if not prediction_output:
        return []

    image_result = prediction_output[0]

    detected_words = getattr(image_result, 'str_res', [])

    if not detected_words and isinstance(image_result, dict):
        detected_words = image_result.get('rec_texts', [])

    return detected_words

def is_algae_match(word):
    word_clean = clean_word(word)
    similarity = fuzz.ratio(word_clean, TARGET)

    if word_clean in REJECT_WORDS:
        return False, similarity

    if similarity >= 78.0:
        return True, similarity

    return False, similarity

def read_text(pdf_path):
    pages = pdfium.PdfDocument(pdf_path)
    counter = 0

    for page_number, page in enumerate(pages, start=1):
        pil_image = page.render(scale=3).to_pil().convert("RGB")
        image = np.array(pil_image)

        page_counter = 0
        seen_matches = set()

        print(f"\n--- Page {page_number} ---")

        image_versions = [
            ("original", image),
            ("preprocessed", preprocess_image(image)),
        ]

        for version_name, image_version in image_versions:
            prediction_output = ocr.predict(image_version)
            detected_words = get_detected_words(prediction_output)

            for word in detected_words:
                matched, similarity = is_algae_match(word)

                if matched:
                    word_clean = clean_word(word)

                    # Avoid double-counting same OCR text from original + preprocessed
                    match_key = word_clean

                    if match_key not in seen_matches:
                        seen_matches.add(match_key)
                        page_counter += 1
                        counter += 1

                        print(
                            f"   Matched: '{word}' "
                            f"-> cleaned='{word_clean}' "
                            f"similarity={similarity:.1f}% "
                            f"source={version_name}"
                        )

        print(f"--> Page {page_number}: Found {page_counter} instances.")

    pages.close()
    return counter


total_algae = read_text("./20220404 Notes.pdf")
print(f"\nFinal Document Total Count: {total_algae}")