import detect_text.ocr as ocr
from detect_text.Text import Text
import numpy as np
import cv2
import json
import time
import os
from os.path import join as pjoin
import pytesseract
import os
import sys

current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the config.py by navigating up to the desired directory
config_dir = os.path.abspath(os.path.join(current_script_dir, '../../../'))
# Add the config directory to sys.path if it's not already there
if config_dir not in sys.path:
    sys.path.append(config_dir)
import config_main as config

# Configuration for pytesseract
pytesseract.pytesseract.tesseract_cmd = config.tesseract_path

def save_detection_json(file_path, texts, img_shape):
    f_out = open(file_path, 'w')
    output = {'img_shape': img_shape, 'texts': []}
    for text in texts:
        c = {'id': text.id, 'content': text.content}
        loc = text.location
        c['column_min'], c['row_min'], c['column_max'], c['row_max'] = loc['left'], loc['top'], loc['right'], loc['bottom']
        c['width'] = text.width
        c['height'] = text.height
        output['texts'].append(c)
    json.dump(output, f_out, indent=4)


def visualize_texts(org_img, texts, shown_resize_height=None, show=False, write_path=None):
    img = org_img.copy()
    for text in texts:
        text.visualize_element(img, line=2)

    img_resize = img
    if shown_resize_height is not None:
        img_resize = cv2.resize(img, (int(shown_resize_height * (img.shape[1]/img.shape[0])), shown_resize_height))

    if show:
        cv2.imshow('texts', img_resize)
        cv2.waitKey(0)
        cv2.destroyWindow('texts')
    if write_path is not None:
        cv2.imwrite(write_path, img)


def text_sentences_recognition(texts):
    '''
    Merge separate words detected by Google ocr into a sentence
    '''
    changed = True
    while changed:
        changed = False
        temp_set = []
        for text_a in texts:
            merged = False
            for text_b in temp_set:
                if text_a.is_on_same_line(text_b, 'h', bias_justify=0.2 * min(text_a.height, text_b.height), bias_gap=2 * max(text_a.word_width, text_b.word_width)):
                    text_b.merge_text(text_a)
                    merged = True
                    changed = True
                    break
            if not merged:
                temp_set.append(text_a)
        texts = temp_set.copy()

    for i, text in enumerate(texts):
        text.id = i
    return texts


def merge_intersected_texts(texts):
    '''
    Merge intersected texts (sentences or words)
    '''
    changed = True
    while changed:
        changed = False
        temp_set = []
        for text_a in texts:
            merged = False
            for text_b in temp_set:
                if text_a.is_intersected(text_b, bias=2):
                    text_b.merge_text(text_a)
                    merged = True
                    changed = True
                    break
            if not merged:
                temp_set.append(text_a)
        texts = temp_set.copy()
    return texts


def text_cvt_orc_format(ocr_result):
    print(ocr_result)
    texts = []
    if ocr_result is not None:
        for i, result in enumerate(ocr_result):
            error = False
            x_coordinates = []
            y_coordinates = []
            text_location = result['boundingPoly']['vertices']
            content = result['description']
            for loc in text_location:
                if 'x' not in loc or 'y' not in loc:
                    error = True
                    break
                x_coordinates.append(loc['x'])
                y_coordinates.append(loc['y'])
            if error: continue
            location = {'left': min(x_coordinates), 'top': min(y_coordinates),
                        'right': max(x_coordinates), 'bottom': max(y_coordinates)}
            texts.append(Text(i, content, location))
    return texts

def text_cvt_orc_format_tesseract(data):
    text_positions = []
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > 60:  # Confidence threshold
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            content = data['text'][i]
            if len(content)==0:
                continue
            location = {'left': x, 'top': y,
                        'right': x+w, 'bottom': y+h}
            text_positions.append(Text(i, content, location))
    return text_positions

def text_cvt_orc_format_paddle(paddle_result):
    texts = []
    for i, line in enumerate(paddle_result):
        points = np.array(line[0])
        location = {'left': int(min(points[:, 0])), 'top': int(min(points[:, 1])), 'right': int(max(points[:, 0])),
                    'bottom': int(max(points[:, 1]))}
        content = line[1][0]
        texts.append(Text(i, content, location))
    return texts


def text_filter_noise(texts):
    valid_texts = []
    for text in texts:
        if len(text.content) <= 1 and text.content.lower() not in ['a', ',', '.', '!', '?', '$', '%', ':', '&', '+']:
            continue
        valid_texts.append(text)
    return valid_texts


def text_detection(input_file='../data/input/30800.jpg', output_file='../data/output', show=False, method='pytesseract', paddle_model=None):
    '''
    :param method: google or paddle
    :param paddle_model: the preload paddle model for paddle ocr
    '''
    start = time.time()
    name = input_file.split('/')[-1][:-4]
    ocr_root = pjoin(output_file, 'ocr')
    img = cv2.imread(input_file)
    if method == 'google':
        print('*** Detect Text through Google OCR ***')
        ocr_result = ocr.ocr_detection_google(input_file)
        texts = text_cvt_orc_format(ocr_result)
        texts = merge_intersected_texts(texts)
        texts = text_filter_noise(texts)
        texts = text_sentences_recognition(texts)
    elif method == 'tesseract':
        print('*** Detect Text through Pytesseract ***')
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #Trying to upscale to improve OCR
        """
        # Define the scale factor
        scale_factor = 4
        # Upscale the image because OCR isn't workin for Low res images!
        image_rgb = cv2.resize(image_rgb, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
        cv2.imwrite("test_sample.jpg", image_rgb)
        """
        ocr_result = pytesseract.image_to_data(image_rgb, output_type=pytesseract.Output.DICT)
        texts = text_cvt_orc_format_tesseract(ocr_result)
        texts = merge_intersected_texts(texts)
        texts = text_filter_noise(texts)
        texts = text_sentences_recognition(texts)
        print("this part done")
    elif method == 'paddle':
        # The import of the paddle ocr can be separate to the beginning of the program if you decide to use this method
        from paddleocr import PaddleOCR
        print('*** Detect Text through Paddle OCR ***')
        if paddle_model is None:
            paddle_model = PaddleOCR(use_angle_cls=True, lang="ch")
        result = paddle_model.ocr(input_file, cls=True)
        texts = text_cvt_orc_format_paddle(result)
    else:
        raise ValueError('Method has to be "google" or "paddle" or "tesseract"!')
    print("pre-visualization done")
    visualize_texts(img, texts, shown_resize_height=800, show=False, write_path=pjoin(ocr_root, name+'.png'))
    print("pre-saving done")
    save_detection_json(pjoin(ocr_root, name+'.json'), texts, img.shape)
    print("[Text Detection Completed in %.3f s] Input: %s Output: %s" % (time.time() - start, input_file, pjoin(ocr_root, name+'.json')))
    

    """
    Extracts text from an image using OCR (Tesseract) and returns text along with their positions.
    """
    # Convert image to RGB (from BGR)
    image = cv2.imread(input_file)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Using pytesseract to get bounding box for each text region
    data = pytesseract.image_to_data(rgb_image, output_type=pytesseract.Output.DICT)
    
    text_positions = []
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        if int(data['conf'][i]) > 60:  # Confidence threshold
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            text_positions.append({'text': data['text'][i], 'position': (x, y, w, h)})
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    #return text_positions

# text_detection()

