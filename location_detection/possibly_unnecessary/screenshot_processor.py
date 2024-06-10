import cv2
import numpy as np
import pytesseract
import os
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
import config

# Configuration for pytesseract
pytesseract.pytesseract.tesseract_cmd = config.tesseract_path

def find_icons_in_roi(screenshot, icons_folder, roi=(0, 0, 0,0)):
    """
    Match icons from a folder in the screenshot within a specified region of interest (ROI) using template matching.
    The ROI is defined as a tuple (x, y, width, height).
    Returns a list of matches with their positions (adjusted to the full image) and the name of the matched icon file.
    """
    x, y, w, h = roi  # ROI coordinates and size
    roi_img = screenshot[y:y+h, x:x+w]  # Crop the ROI from the screenshot
    
    matches = []
    for icon_filename in os.listdir(icons_folder):
        icon_path = os.path.join(icons_folder, icon_filename)
        icon = cv2.imread(icon_path, 0)
        icon_w, icon_h = icon.shape[::-1]
        res = cv2.matchTemplate(roi_img, icon, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9  # Threshold can be adjusted
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):  # Adjust match positions to the full image
            match_pos = (pt[0] + x, pt[1] + y)
            matches.append({'position': match_pos, 'size': (icon_w, icon_h), 'icon_name': icon_filename})
    return matches


def find_potential_buttons(image): #looks only for rectangular buttons
    """
    Identifies potential buttons in an image with relaxed criteria, aiming to find more candidates by using contours.
    The focus is still on rectangular-like shapes, but with a broader definition.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    potential_buttons = []
    for cnt in contours:
        # Calculate the area and adjust constraints to include smaller and larger potential buttons
        area = cv2.contourArea(cnt)
        if area < 50 or area > 20000:  # Relaxed area constraints
            continue

        # Compute the bounding rectangle of the contour
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Relaxed calculation for aspect ratio and solidity
        aspect_ratio = w / float(h)
        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area
        
        # More inclusive filter based on aspect ratio and solidity
        if 0.5 <= aspect_ratio <= 2.0 and solidity > 0.8:  # Broader aspect ratio and lower solidity
            cv2.drawContours(image, [cnt], -1, (255, 0, 0), 2)
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            potential_buttons.append((x, y, w, h))

    return potential_buttons





def extract_text_and_positions(image):
    """
    Extracts text from an image using OCR (Tesseract) and returns text along with their positions.
    """
    # Convert image to RGB (from BGR)
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

    return text_positions

def process_screenshot(screenshot_path, icons_folder):
    """
    Main function to process the screenshot.
    """
    screenshot = cv2.imread(screenshot_path)
    if screenshot is None:
        print(f"Failed to load screenshot from {screenshot_path}")
        return

    # OCR - Extract Text and Positions
    #text_positions = extract_text_and_positions(screenshot)

    # Icon Matching
    matches = find_icons_in_roi(cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY), icons_folder, (0,0,4000,4000))
    # Iterate through the matches to draw rectangles on the screenshot
    for match in matches:
        match_pos = match['position']
        icon_w, icon_h = match['size']
        cv2.rectangle(screenshot, match_pos, (match_pos[0] + icon_w, match_pos[1] + icon_h), (0, 255, 0), 2)
        cv2.circle(screenshot, match_pos, 2, (0, 255, 0), -1)

    # Find potential buttons
    buttons = find_potential_buttons(screenshot)

    #print("Extracted Text and Positions:", text_positions)
    print("Icon Matches:", matches)
    print("Potential Buttons:", buttons)

    # Display the result with matched icons and text boxes
    cv2.imshow('Processed Screenshot', screenshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
process_screenshot(config.image_path, config.icons_path)
