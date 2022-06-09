# Import libraries
from PIL import Image
from pytesseract import image_to_string
from pytesseract import pytesseract
import tempfile
import cv2
import sys
from pdf2image import convert_from_path
import os
from time import perf_counter
from helpers import strip_non_printable_chars
import json
  
# Path of the pdf
PDF_file = "d.pdf"
image_preprocessing_enabled = False  
# Store all the pages of the PDF in a variable
with tempfile.TemporaryDirectory() as path:
    debut = perf_counter()

    print('Preparing PDF for OCR. Please wait...')
    pages = convert_from_path(PDF_file, 300, output_folder=path, poppler_path=r".\\lib\\poppler-22.04.0\\Library\\bin", first_page=1, last_page=5, thread_count=1, fmt='jpeg')
  
    image_counter = 1
    
    for page in pages:
    
        filename = "page_"+str(image_counter)+".jpg"
        page.save(path + "\\" + filename, 'JPEG')
        image_counter = image_counter + 1

    filelimit = image_counter-1
    outfile = "out_text.txt"

    pytesseract.tesseract_cmd = r".\\lib\\Tesseract-OCR\\tesseract.exe"
    
    f = open(outfile, "a")
    f.write("[")
    # Iterate from 1 to total number of pages
    for i in range(1, filelimit + 1):
        print(f'processing page {i} of {filelimit}...\r', end="")
        filename = path + "\page_"+str(i)+".jpg"
            
        if image_preprocessing_enabled:
            # grayscale, Gaussian blur, Otsu's threshold
            image = cv2.imread(filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (3,3), 0)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
            invert = 255 - opening
            text = image_to_string(invert, lang='eng', config='--psm 6')
        else:
            text = str(((image_to_string(Image.open(filename)))))
        
        text = text.replace('-\n', '')
        text = strip_non_printable_chars(text)

        data = {
            'page_number': i,
            'text': text
        }
    
        # Finally, write the processed text to the file.
        json.dump(data, f)
        f.write(',')

    
    # Close the file after writing all the text.
    f.write(']')
    f.close()
    fin = perf_counter()
    print("")
    print(f"Completed in {fin - debut:0.2f}s")