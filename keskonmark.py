from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont
import imghdr
import math
import pathlib


# ------------------------------ STYLE --------------------------------- #

BLACK = "#020202"
WHITE = "#f1f1f1"
CRIMSON = "#dc142c"
TITLE_FONT_NAME = "Courier"


# ---------------------------- WATERMARK ------------------------------- #

OUTPUT_PATH = "output/"
PLACEHOLDER = "-> Type Here <-"  # (Must be within MAX_LENGTH)
MAX_LENGTH = 15
WATERMARK_FONT = "arial.ttf"
selected_files_path = []  # Do Not Touch!


# --------------------------- FUNCTIONS -------------------------------- #

def watermark(image_file, text_watermark):
    img_type = imghdr.what(image_file)
    if img_type == "jpeg" or img_type == "png":
        # get an image
        with Image.open(image_file).convert("RGBA") as base:
            filename = image_file.split('/')[-1].split('.')[0]
            # make a blank image for the text, initialized to transparent text color
            txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
            # get a font
            font_size = int(base.width * 0.08)
            fnt = ImageFont.truetype(WATERMARK_FONT, font_size)
            # get a drawing context
            d = ImageDraw.Draw(txt)
            # calculate text height and width
            left, top, right, bottom = d.textbbox(text=text_watermark, font=fnt, xy=(0, 0))
            text_width = right - left
            text_height = bottom - top
            # calculate text position (centralized)
            x = base.width / 2 - text_width / 2
            y = base.height / 2 - text_height * 0.75
            # calculate stroke width
            stroke_width = math.ceil(font_size * 0.04)
            # draw text, half opacity
            d.text((x, y), text_watermark, font=fnt, fill=(255, 255, 255, 51),
                   stroke_width=stroke_width, stroke_fill=(0, 0, 0, 26))
            # apply text watermark to base image
            out = Image.alpha_composite(base, txt)
            # save result image
            out.save(f'{OUTPUT_PATH}{filename}.png', format="png")

        return True


def select_files():
    f_types = [('Image Files', ['*.jpg', '*.png'])]   # type of files to select
    global selected_files_path
    selected_files_path = filedialog.askopenfilename(multiple=True, filetypes=f_types)
    selected_files_num_label.config(text=f"{len(selected_files_path)} Files Selected")
    if len(selected_files_path) != 0:
        start_button.config(state="normal")
    else:
        start_button.config(state="disabled")


def watermark_all():
    # Get Watermark Text
    text_watermark = watermark_entry.get()
    # Create Output Folder
    path = pathlib.Path(OUTPUT_PATH)
    # path.mkdir(exist_ok=True)
    try:
        path.mkdir(exist_ok=True)
    except PermissionError as err:
        # Show Error Message and Exit
        messagebox.showerror(title="KESKONMARK - Permission Error",
                             message=f"You don't have permission to write to disk.\r{err}")
        exit()
    # Watermark Images
    errors = []
    if text_watermark != PLACEHOLDER and text_watermark != "":
        selected_files_num_label.config(text=f"WORKING...")
        selected_files_num_label.update()
        for image in selected_files_path:
            if not watermark(image, text_watermark):
                errors.append(image)
        if errors:
            num_errors = len(errors)
            error_message = f"{num_errors} Invalid Images. \nCheck error.log for details."
            with open("error_log.txt", "w") as log:
                log.write("\n".join(errors))
            messagebox.showerror(title="KESKONMARK", message=error_message)
        selected_files_num_label.config(text=f"ALL DONE")
    else:
        messagebox.showwarning(title="KESKONMARK", message="Don't Forget to Type in the Watermark!")


def clear_entry(event):
    if watermark_entry.get() == PLACEHOLDER:
        watermark_entry.delete(0, END)


def validate_entry(text):
    if len(text) <= MAX_LENGTH:  # Specify the desired length limit here
        return True
    else:
        return False


# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
validate_func = window.register(validate_entry)  # Register the validation function

window.title("KESKONMARK - Watermark Your Images!")
window.config(padx=50, pady=50, bg=BLACK)
window.geometry('+500+100')


# Row 0
title_label = Label(text="KESKONMARK", fg=CRIMSON, bg=BLACK, font=(TITLE_FONT_NAME, 28, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 50))


# Row 1
watermark_entry = Entry(width=16, fg=WHITE, bg=BLACK, insertbackground=WHITE, borderwidth=0,
                        highlightthickness=2, highlightcolor=CRIMSON, highlightbackground=CRIMSON,
                        font=(TITLE_FONT_NAME, 16, "bold"), justify="center",
                        validate="key", validatecommand=(validate_func, "%P"))
watermark_entry.grid(row=1, column=0, columnspan=2)
watermark_entry.insert(0, PLACEHOLDER)
watermark_entry.bind("<FocusIn>", clear_entry)


# Row 2
selected_files_num_label = Label(text="Select Images", fg=WHITE, bg=BLACK, font=(TITLE_FONT_NAME, 16, "normal"))
selected_files_num_label.grid(row=2, column=0, columnspan=2, pady=(50, 10))


# Row 3
select_button = Button(text="SELECT", height='2', width=18, font=("Arial", 10, "bold"), bg=CRIMSON, fg=WHITE,
                       activebackground=BLACK, activeforeground=CRIMSON, highlightthickness=0,
                       command=select_files)
select_button.grid(row=3, column=0, columnspan=1, pady=(40, 0))

start_button = Button(text="GET SOME!", height='2', width=18, font=("Arial", 10, "bold"), bg=CRIMSON, fg=WHITE,
                      disabledforeground=BLACK, activebackground=BLACK, activeforeground=CRIMSON, highlightthickness=0,
                      state="disabled", command=watermark_all)
start_button.grid(row=3, column=1, columnspan=1, pady=(40, 0))


window.mainloop()
