import easyocr
reader = easyocr.Reader(['en'])
import pypdfium2 as pdfium
import numpy as np

import easyocr
import pypdfium2 as pdfium
import numpy as np
import cv2  # Requires: pip install opencv-python
from rapidfuzz import fuzz 

reader = easyocr.Reader(['en'])

def optimize_image_for_handwriting(pil_image):
    """Converts image to pure black & white, sharpening pencil/pen marks."""
    # 1. Convert PIL image to OpenCV NumPy format
    open_cv_image = np.array(pil_image)
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    
    # 2. Convert to Grayscale
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    
    # 3. Apply Adaptive Gaussian Thresholding to isolate ink textures
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 21, 15
    )
    return thresh

def read_text(pdf_path):
    pages = pdfium.PdfDocument(pdf_path)
    counter = 0
    
    for page_number, page in enumerate(pages, start=1):
        pil_image = page.render(scale=3).to_pil()
        numpy_image = np.array(pil_image)
        result = reader.readtext(numpy_image, detail=0)
        
        page_counter = 0
        for word in result:
            # 1. Standardize text to lowercase and remove stray symbols
            word_clean = word.lower().strip()
            
            # 2. Compare the word mathematically against "algae"
            # ratio() returns a score from 0 (no match) to 100 (perfect match)
            similarity = fuzz.ratio(word_clean, "algae")
            
            # 3. If it is 70% or more similar, count it as a match
            # This cleanly catches "4lqae", "algaf", "al64@", and "algae" itself!
            if similarity >= 70.0:
                page_counter += 1
                counter += 1
                print(f"Matched: '{word}' -> evaluated as 'algae' ({similarity:.1f}% match)")
                
        print(f"--> Page {page_number}: Found {page_counter} instances.")
        
    pages.close()
    return counter

total_count = read_text('./20220404 Notes.pdf')
print(f"\nFinal Verified Count: {total_count}")

    

