import os

import pytesseract
import pdf2image
try:
    from PIL import Image
except ImportError:
    import Image


def ocr_core(file):
    text = pytesseract.image_to_string(file)
    return text


def print_pages(pdf_file):
    images = pdf_to_img(pdf_file)
    for pg, img in enumerate(images):
        print(ocr_core(img))


def pdf_to_img(pdf_file):
    return pdf2image.convert_from_path(pdf_file)


def extract_firstpage_from_pdf(input_name, save=False):
    pages = pdf_to_img(input_name)
    name, ext = os.path.splitext(input_name)

    image_counter = 1

    if save:
        for page in pages:
            filename = "files\\page_"+str(image_counter)+".jpg"
            page.save(filename, 'JPEG')
            image_counter = image_counter + 1

    return pages[0]

    #with PyTessBaseAPI(path='C:/Users/OKait/Google Drive/MTA/Project/OCR/tesseract/tesserocr-master/tessdata/tessdata_best-master', lang='eng') as api:
    #    images = pdf2image.convert_from_path('page_1.jpg')
    #    for pg, img in enumerate(images):
    #        api.SetImageFile(img)
    #        print(api.GetUTF8Text())
