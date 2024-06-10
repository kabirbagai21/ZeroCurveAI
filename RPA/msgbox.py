import tkinter as tk

import pyautogui

from RPA.automate import locate_button, moveMouse, makeClick
from coordLookup import imgLookup, coordLookup, user_action_req

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = '#EAECEE'

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

class InstructionPopup:
    def __init__(self, instructions, buttons):
        self.instructions = instructions
        self.buttons = buttons
        self.index = 0

        self.popup = tk.Toplevel()
        self.popup.title("Instructions")
        self.popup.geometry("300x200")
        self.popup.resizable(width=False, height=False)
        self.popup.configure(width=300, height=200, bg=BG_COLOR)

        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()

        # Calculate the coordinates for bottom-left corner
        x_coord = 0
        y_coord = screen_height - self.popup.winfo_reqheight()

        # Set the geometry of the popup window
        self.popup.geometry(f"+{x_coord}+{y_coord}")

        self.instruction_label = tk.Label(self.popup, text="\n".join(self.instructions[self.index]), wraplength=280)
        self.instruction_label.pack(padx=10, pady=10)

        self.prev_button = tk.Button(self.popup, text="Prev", command=self.show_prev_instruction)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(self.popup, text="Next", bg=BG_GRAY, command=self.show_next_instruction)
        self.next_button.pack(side=tk.RIGHT, padx=10, pady=10)
        self.popup.wm_attributes("-topmost", True)

    def show_next_instruction(self):
        if self.index < len(self.instructions) - 1:
            button_list = self.buttons[self.index]
            self.index += 1
            instruction_text = "\n".join(self.instructions[self.index])
            self.instruction_label.config(text=instruction_text)
            for idx, button in enumerate(button_list):
                if button in coordLookup.keys():
                    if idx == 0: pyautogui.confirm('Press ENTER to allow bot to make click', buttons=['Cancel'])
                    makeClick(coordLookup[button][0], coordLookup[button][1])
                else:
                    button_path = imgLookup[button]
                    if button_path:
                        if idx == 0: pyautogui.confirm('Press ENTER to allow bot to make click', buttons=['Cancel'])
                        locate_button(button, button_path)

            if button != 'N/A' and button not in user_action_req:
                self.next_button.invoke()
                '''
                self.next_button.focus()  # Set focus to the "Next" button
                next_button_x, next_button_y = self.next_button.winfo_rootx(), self.next_button.winfo_rooty()
                makeClick(next_button_x+10, next_button_y+10)  # Adjust offset as needed
                '''

    def show_prev_instruction(self):
        if self.index > 0:
            self.index -= 1
            instruction_text = "\n".join(self.instructions[self.index])
            self.instruction_label.config(text=instruction_text)
'''
# Example instructions
instructions = [
    "Step 1: Do this.",
    "Step 2: Then do that.",
    "Step 3: Finally, do this other thing."
]

# Create the main application window
root = tk.Tk()
root.withdraw()  # Hide the main window

# Create the popup with instructions immediately
InstructionPopup(root, instructions)

# Start the main event loop
root.mainloop()
'''