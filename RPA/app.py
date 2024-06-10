from curses import window
from email.mime import message
from tkinter import *
from turtle import window_height, window_width
import time
from automate import takeScreenshot
from demo import execute_clicks
import openai
import base64
import requests
import subprocess
import os
from PIL import Image, ImageDraw
import re
from msgbox import InstructionPopup
# tutorial: https://www.youtube.com/watch?v=RNEcewpVZUQ

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = '#EAECEE'

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

class ChatApplication:

    def __init__(self):
        self.message_sent = False
        self.window = Tk()
        self._setup_main_window()
        self._set_attributes()

    def run(self):
        while True:
            if self.message_sent:
                # This is our hardcoded clicking for the demo
                # execute_clicks()
                self.message_sent = False
            self.window.update_idletasks()
            self.window.update()

    def _get_logic_pro_pid(self):
        # Replace 'Logic Pro' with the actual name of the Logic Pro window
        result = subprocess.run(['pgrep', '-f', 'Logic Pro'], capture_output=True, text=True)
        if result.returncode == 0:
            pid = result.stdout.strip()
            return int(pid)
        return None

    def _set_attributes(self):

        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.8)  # Adjust transparency as needed
        #self.window.attributes("-type", "dock")  # Keep the window always visible
            # Set Tkinter window as transient to the Logic Pro window
            # self.window.wm_transient(logic_pro_pid)

    def _setup_main_window(self):
        self.window.title("Chat")
        self.window.resizable(width=False, height=False)
        window_width = 500
        window_height = 550
        screen_width = self.window.winfo_screenwidth()
        self.window.geometry(f"{window_width}x{window_height}+{screen_width - window_width}+0")
        self.window.configure(width=window_width, height=window_height, bg=BG_COLOR)
        # Set window attributes for a popup-like behavior

        head_label = Label(self.window, bg=BG_COLOR,
                           fg=TEXT_COLOR, text="Welcome", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)
        line = Label(self.window, width=window_width - 10, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)

        # text widget
        self.text_widget = Text(self.window, width=20, height=2, background=BG_COLOR,
                                foreground=TEXT_COLOR, font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)

        # scroll bar
        # scrollbar = Scrollbar(self.text_widget)
        # scrollbar.place(relheight=1, relx=0.974)
        # scrollbar.configure(command=self.text_widget.yview)

        # bottom container
        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        # message entry box
        self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        # send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

    def convert_percentage_to_pixel(self, coordinate_ratios, img_width, img_height):
        # Unpack the coordinates
        x1, y1, x2, y2 = coordinate_ratios

        # Convert the coordinates from ratios to pixels
        x1_pixel = int(x1 * img_width)
        y1_pixel = int(y1 * img_height)
        x2_pixel = int(x2 * img_width)
        y2_pixel = int(y2 * img_height)

        return (x1_pixel, y1_pixel, x2_pixel, y2_pixel)

    def getInstructions(self, filename):
        with open(filename, 'r') as file:
            instructions = [line.strip().split(',') for line in file.readlines()]
            return instructions

    def getInstructionsBot(self, filename):
        with open(filename, 'r') as file:
            instructions = ''
            for line in file.readlines():
                instructions += line.strip() + '\n'
            return instructions

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "You")
        self.message_sent = True
        instructions = self.getInstructions('instructions.txt')
        buttons = self.getInstructions('buttons.txt')
        print(buttons)
        InstructionPopup(instructions, buttons)

    # Function to encode the image
    '''
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
    '''
    def get_response_from_gpt4(self, prompt_text):
        # Be sure to handle exceptions and errors in production code
        # Path to your image
        image_path = "RPA/screenshot.png"
        # Getting the base64 string
        base64_image = self.encode_image(image_path)
        preface = (

        )
        full_prompt = preface + prompt_text
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=800,
        )

        answer = response.choices[0].message.content
        # Find all tuples of the form (a,b,c,d) in the string
        tuples_list = re.findall(r'\((-?\d+\.\d+),\s*(-?\d+\.\d+),\s*(-?\d+\.\d+),\s*(-?\d+\.\d+)\)', answer)

        # Convert tuples to float and create a list of tuples with float numbers
        float_tuples_list = [(float(a), float(b), float(c), float(d)) for a, b, c, d in tuples_list]
        print(float_tuples_list)
        # Load the image
        image_path = 'RPA/screenshot.png'
        with Image.open(image_path) as img:
            # Create a drawing object
            draw = ImageDraw.Draw(img)
            img_width, img_height = img.size

            # Define the color and width of the rectangles
            color = 'red'
            width = 3

            # Draw rectangles around the estimated button locations
            for coords in float_tuples_list:
                draw.rectangle(self.convert_percentage_to_pixel(coords, img_width, img_height), outline=color,
                               width=width)

            # Save the modified image
            highlighted_image_path = 'RPA/ss_with_bounding_boxes.png'
            img.save(highlighted_image_path)

        return answer

    def _insert_message(self, msg, sender):
        if not msg:
            return
        takeScreenshot()
        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)
        bot_message = self.getInstructionsBot('instructions.txt')
        #bot_message = self.get_response_from_gpt4(msg)
        time.sleep(4)
        msg2 = f"Zerocurve bot: {bot_message}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg2)
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)


if __name__ == "__main__":
    app = ChatApplication()
    app.run()