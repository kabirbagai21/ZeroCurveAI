import pyautogui

imgLookup = {
    "N/A": None,
    "Create Sketch": 'newsketch.png',
    "Center Diameter Circle": 'centerdiametercircle.png',
    "Create": 'create.png',
    "Finish Sketch": 'finishsketch.png',
    "Point": 'point.png',
    "Rectangle": 'rectangle.png',
    "Center Rectangle": 'centerrectangle.png',
    "Extrude": 'extrude.png',
    "Objects": 'objects.png',
    "Modify": 'modify.png',
    "Fillet": 'fillet.png',
    "Axis": 'axis.png',
    "Pattern": 'pattern.png',
    "Circular Pattern": 'circularpattern.png',
    "Operation": 'extrudeoperation.png'

    # Add more buttons and their positions as needed
}
hover = ["Pattern", "Rectangle"]
user_action_req = ["Rectangle", "Objects", "Pattern", "Operation", "Axis"]
coordLookup = {}


'''
coordLookup = {
    "N/A": None,
    "Create Sketch": 'newsketch.png',
    "Center Diameter Circle": 'centerdiametercircle.png',
    "Create": 'create.png',
    "Finish Sketch": 'finishsketch',
    "Point": (170, 368),
    "Rectangle": (221, 198),
    "Center Rectangle": (346, 242),
    "Extrude": (192, 125),
    "Objects": (1305, 387),
    "Modify": (616, 154),
    "Axis": (1303, 418)
    # Add more buttons and their positions as needed
}
'''