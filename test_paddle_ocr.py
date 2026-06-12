import os 
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT'] = '0'

import pypdfium2 as pdfium
import numpy as np
from paddleocr import PaddleOCR
from rapidfuzz import fuzz

ocr = PaddleOCR(lang='en')

def read_text(pdf_path):
    pages = pdfium.PdfDocument(pdf_path)
    counter = 0
    
    for page_number, page in enumerate(pages, start=1):
        pil_image = page.render(scale=4).to_pil()
        numpy_image = np.array(pil_image)
        
        prediction_output = ocr.predict(numpy_image)
        
        page_counter = 0
        print(f"\n--- Page {page_number} ---")
        
        if prediction_output:
            image_result = prediction_output[0]
            
            detected_words = getattr(image_result, 'str_res', [])
            
            if not detected_words and isinstance(image_result, dict):
                detected_words = image_result.get('rec_texts', [])
            
            for word in detected_words:
                word_clean = str(word).lower().strip()
                
                similarity = fuzz.ratio(word_clean, "algae")
                
                if similarity >= 40.0:
                    page_counter += 1
                    counter += 1
                    print(f"   Matched: '{word}' -> (Similarity: {similarity:.1f}%)")
                    
        print(f"--> Page {page_number}: Found {page_counter} instances.")
        
    pages.close()
    return counter
total_algae = read_text('./20220404 Notes.pdf')
print(f"\nFinal Document Total Count: {total_algae}")
