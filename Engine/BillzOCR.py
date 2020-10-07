import json
from PIL.ImagePalette import raw
from tesserocr import PyTessBaseAPI, PSM
from tesserocr import tesseract_version
from PIL import Image, ImageFilter, ImageDraw
from tesserocr import PyTessBaseAPI, RIL
import sys
from Engine.ocr_helper import *
from Engine.bills_parser import *
import os
import traceback
import random

VERSION = "1.0.2"

supported_ext = [
    '.jpg',
    '.jpeg',
    '.pdf'
]

tesseract_path = "resources/"  # "/usr/local/Cellar/tesseract/4.1.1/share/tessdata/"
#debug = False
debug = True
pending_queue= dict()


def debug_log(msg):
    if debug:
        print(msg)


def get_comp(input_name):
    image = Image.open(input_name)
    with PyTessBaseAPI(path=tesseract_path, lang='heb') as api:
        image = preprocess_image(image)
        api.SetImage(image)
        boxes = api.GetComponentImages(RIL.TEXTLINE, True)
        debug_log('Found {} textline image components.'.format(len(boxes)))
        for i, (im, box, _, _) in enumerate(boxes):
            # im is a PIL image object
            # box is a dict with x, y, w and h keys
            api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
            ocrResult = api.GetUTF8Text()
            conf = api.MeanTextConf()
            debug_log(u"Box[{0}]: x={x}, y={y}, w={w}, h={h}, "
                      "confidence: {1}, text: {2}".format(i, conf, ocrResult, **box))


def preprocess_image(image, output_name):
    #threshold
    gray = image.convert('L')
    blackwhite = gray.point(lambda x: 0 if x < 180 else 255, '1')
    blackwhite.save(output_name + "_bw.jpg")
    img_filtered = blackwhite.filter(ImageFilter.MaxFilter(size=1))
    img_filtered.save(output_name + "_filtered.jpg")
    width, height = img_filtered.size

    # Setting the points for cropped image
    left = width * 0.4
    top = height * 0.5
    right = width * 0.6
    bottom = height * 0.4

    #img_filtered = img_filtered.crop((left, top, right, bottom))
    #img_filtered.show()

    #return blackwhite

    return img_filtered


def crop_price(im, bill_type):
    width, height = im.size

    #print("w:", width, "h:", height)

    if bill_type == BillType.Electricity:
        left = width * 0.37 #650
        top = height * 0.45 #1150
        right = width - left
        bottom = height - top + (height * 0.012)
    if bill_type == BillType.Arnona_TelAviv:
        left = width * 0.25 #650
        top = height * 0.35
        right = width * 0.45
        bottom = height * 0.40

    # Setting the points for cropped image
    #left = 650
    #top = 1150
    #right = width - 650
    #bottom = height - 1120

    im = im.crop((left, top, right, bottom))

    #im.show()

    return im


def main():
    if len(sys.argv) < 2:
        raise ValueError('Input file was not specified')

    debug_log(f'Input file is {sys.argv[1]}')

    input_name = sys.argv[1]
    filename, file_extension = os.path.splitext(input_name)
    if file_extension not in supported_ext:
        raise ValueError(f'Unsupported file type - {supported_ext}')

    # if the file is pdf file
    if file_extension == ".pdf":
        image = extract_firstpage_from_pdf(input_name)
    else:
        image = Image.open(input_name)

    processed_image = preprocess_image(image, filename)
    bill_type = get_bill_type(processed_image)

    output_name = filename + "_out.txt"
    # read_details(image, bill_type, output_name)

    output_name = filename + "_m_out.txt"
    client_id, date = read_details(processed_image, bill_type)

    price_img = crop_price(processed_image, bill_type)
    price = read_price(price_img)

    debug_log("Done!")

    result = {
        "type": bill_type.name,
        "client_id": client_id,
        "date": date,
        "price": price
    }

    print(json.dumps(result))

    return json.dumps(result)


def read_price(image, output_name=""):
    with PyTessBaseAPI(path=tesseract_path, psm=PSM.SINGLE_BLOCK, lang='eng') as api:
        api.SetVariable("tessedit_char_whitelist", ".0123456789")
        api.SetVariable("tessedit_char_blacklist",
                        "!?@#$%&*()<>_-+=/:;'\"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
        api.SetVariable("classify_bln_numeric_mode", "1")

        api.SetImage(image)
        raw_text = api.GetUTF8Text()
        res = ''.join(filter(str.isdigit, raw_text))

        if "." not in res:
            res = res[:-2] + "." + res[-2:]

        debug_log("bill price is: " + res)

        return res

        if output_name != "":
            with open(output_name, "w", encoding="utf-8") as f:
                f.write(raw_text)
                print("save output as " + output_name + "...")
            f.close()


def get_bill_type(image):
    with PyTessBaseAPI(path=tesseract_path, lang='heb') as api:
        api.SetImage(image)
        raw_text = api.GetUTF8Text()
        return identify_bill_type(raw_text)


def read_details(image, billtype, output_name=""):
    # psm=PSM.AUTO , psm=PSM.SINGLE_BLOCK
    with PyTessBaseAPI(path=tesseract_path, lang='heb') as api:
        api.SetImage(image)
        raw_text = api.GetUTF8Text()
        details = parse_bill_raw(raw_text, billtype)

        if output_name != "":
            with open(output_name, "w", encoding="utf-8") as f:
                f.write(raw_text)
                debug_log("save output as " + output_name + "...")
            f.close()
        return details

        boxes = api.GetComponentImages(RIL.TEXTLINE, True)
        debug_log('Found {} textline image components.'.format(len(boxes)))

        for i, (im, box, _, _) in enumerate(boxes):
            # im is a PIL image object
            # box is a dict with x, y, w and h keys
            api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
            ocrResult = api.GetUTF8Text()
            conf = api.MeanTextConf()
            debug_log(u"Box[{0}]: x={x}, y={y}, w={w}, h={h}, "
                  "confidence: {1}, text: {2}".format(i, conf, ocrResult, **box))


def process_file(file_path, requestId):
    global pending_queue
    pending_queue[requestId] = ""
    input_name = file_path
    filename, file_extension = os.path.splitext(input_name)
    if file_extension not in supported_ext:
        raise ValueError(f'Unsupported file type - {supported_ext}')

    # if the file is pdf file
    if file_extension == ".pdf":
        image = extract_firstpage_from_pdf(input_name)
    else:
        image = Image.open(input_name)

    processed_image = preprocess_image(image, filename)
    bill_type = get_bill_type(processed_image)

    output_name = filename + "_out.txt"
    # read_details(image, bill_type, output_name)

    output_name = filename + "_m_out.txt"
    client_id, date = read_details(processed_image, bill_type)

    price_img = crop_price(processed_image, bill_type)
    price = read_price(price_img)

    debug_log("Done!")

    result = {
        "type": bill_type.name,
        "client_id": client_id,
        "date": date,
        "price": price
    }

    print(json.dumps(result))
    pending_queue[requestId] = json.dumps(result)
    return json.dumps(result)


def generate_id_for_pending_queue():
    id = "%06d" % random.randint(0, 1000000)
    while id in pending_queue.keys():
        id = "%06d" % random.randint(0, 1000000)
    return id


def try_process_file(file_path):
    try:
        parse_id = generate_id_for_pending_queue()
        res = process_file(file_path, parse_id)
    except Exception as e:
         print("Unable to parse {}".format(file_path))
         #traceback.print_tb()
         res = ""
    return res

if __name__ == '__main__':
    main()
