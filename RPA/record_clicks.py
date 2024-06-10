import pyautogui
from pynput.mouse import Listener
import time 

# List to store mouse clicks and positions
clicks = []

# Function to record mouse clicks
def on_click(x, y, button, pressed):
    if pressed:
        clicks.append((button.name, x, y))
        print(clicks)

# Example usage
if __name__ == "__main__":
    # Start recording mouse clicks
    with Listener(on_click=on_click) as listener:
        listener.join()


#[('right', 655.1328735351562, 360.06488037109375), ('left', 689.3743286132812, 370.47454833984375), ('left', 86.73486328125, 372.710205078125), ('left', 78.24765014648438, 324.60443115234375), ('left', 90.28570556640625, 309.57501220703125), ('right', 802.779296875, 255.6685333251953), ('left', 832.1708984375, 290.6407470703125)]