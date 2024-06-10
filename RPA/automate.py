import pyautogui
import time
pyautogui.FAILSAFE = True
from coordLookup import coordLookup, hover


def moveMouse(xLoc, yLoc):
    pyautogui.moveTo(xLoc, yLoc, duration=0.25)

def makeClick(xLoc, yLoc):
    pyautogui.moveTo(xLoc, yLoc, duration=1)
    pyautogui.click()
    #takeScreenshot()

def takeScreenshot(region=None):
    screenshot = pyautogui.screenshot(region=region)
    save_path = "screenshot.png"
    screenshot.save(save_path)

def getRelativeMousePosition():
    screenX, screenY = pyautogui.size()
    xPos, yPos = pyautogui.position()
    return xPos / screenX, yPos / screenY


'''
print(pyautogui.size()) # current screen resolution width and height

#cofirm button automated click
pyautogui.confirm('This displays text and has an OK and Cancel button.')

#types text at cursor location
pyautogui.typewrite('Hello world!\n', interval=0.5)


#prompts the user for text to write
pyautogui.prompt('This lets the user type in a string and press OK.')



buttonx, buttony = button_point
pyautogui.click(buttonx, buttony)

#moves mouse to specific coordinates
pyautogui.moveTo(500, 500, duration=1)

#exits and enters fullscreen
pyautogui.hotkey('control', 'command', 'f')

user_input = input("Enter the text you want to type: ")

# Add a delay to switch to the target window
time.sleep(5)

# Type the input using PyAutoGUI
pyautogui.typewrite(user_input)
'''
def locate_button(button, button_path):
    button_path = 'button_pics/' + button_path
    button_loc = pyautogui.locateOnScreen(button_path, grayscale=False, confidence=0.9)
    pixelRatio = pyautogui.screenshot().size[0] / pyautogui.size().width
    button_point = pyautogui.center(button_loc)
    x = button_point.x / pixelRatio
    y = button_point.y / pixelRatio
    print(x, y)
    coordLookup[button] = (x, y)
    if button in hover:
        moveMouse(x, y)
    else:
        makeClick(x, y)




print(pyautogui.size())
print(pyautogui.position())