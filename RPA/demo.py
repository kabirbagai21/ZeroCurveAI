import pyautogui
import time
from pynput import keyboard

# List of mouse clicks
clicks = [('left', 634.0172729492188, 439.89666748046875), ('right', 599.1036987304688, 402.8764343261719), ('left', 634.0172729492188, 439.89666748046875), ('left', 65.42155456542969, 1135.4954833984375), ('left', 74.26194763183594, 510.5936279296875), ('left', 117.52796936035156, 441.94061279296875), ('right', 801.845947265625, 259.61004638671875), ('left', 867.941650390625, 274.0029296875)]
# Function to execute mouse clicks
def execute_clicks():
    for click in clicks:
        button, x, y = click
        pyautogui.moveTo(x, y, duration=1.5)  # Move mouse pointer to the specified location slowly
        pyautogui.click(button=button)  # Perform the click after moving to the locations

# Function to handle key press events
def on_press(key):
    try:
        # Check if the pressed key is 'd'
        if key.char == 'd':
            print("Key 'd' pressed, executing workflow...")
            execute_clicks()
            # Stop listening for key press events
            return False
    except AttributeError:
        # Ignore non-character key presses
        pass

# Example usage
if __name__ == "__main__":
    # Wait for the letter "d" to be pressed
    print("Press 'd' to execute the workflow...")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

