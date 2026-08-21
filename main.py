# **** DEPENDENCIES

import sys
import os
import shutil
import configparser
import tkinter as tk
from tkinter import messagebox, font, filedialog, colorchooser, ttk

try:
    from PIL import Image, ImageTk, ImageFont, ImageDraw
    import matplotlib.font_manager as fm
except ImportError as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Dependency Error",
        f"A required library is missing: {e}.\n\n"
        "Please install the required libraries using:\n"
        "pip install Pillow matplotlib configparser"
    )
    sys.exit(1)

# **** PATHS & CONSTANTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, 'resources')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(BASE_DIR, 'watermarker.ini')
PROGRAM_NAME = 'WaterMarker'
PROGRAM_VERSION = '1.0.0'
PROGRAM_DESCRIPTION = 'Set a text watermark\nthe easy way\n\nProgram by @edfasano70'

# **** VARIABLES

root_dir = BASE_DIR
save_dir = BASE_DIR
save_flag = False
text_color = (0, 0, 0)
font_selected = None
display_image_path = os.path.join(RESOURCES_DIR, 'checkers.png')
image1_width = 0
image1_height = 0
updating_controls = False

# **** FUNCTIONS

def show_about():
    about_window = tk.Toplevel(win)
    about_window.title("About")
    about_window.geometry("300x320")
    about_window.iconphoto(False, icon)
    about_window.resizable(False, False)
    about_window.attributes("-topmost", True)

    # Add splash image with reference retention
    splash_path = os.path.join(RESOURCES_DIR, 'splash.png')
    if os.path.exists(splash_path):
        about_image = ImageTk.PhotoImage(Image.open(splash_path))
        image_label = tk.Label(about_window, image=about_image)
        image_label.image = about_image  # Retain reference to prevent GC
        image_label.pack(pady=(10, 5))

    # Texts below the image
    name_label = tk.Label(about_window, text=PROGRAM_NAME, font=font.Font(family='Arial', size=15, weight='bold'))
    name_label.pack()

    version_label = tk.Label(about_window, text=f"v{PROGRAM_VERSION}", font=font.Font(family='Arial', size=10, weight='bold'))
    version_label.pack()

    description_label = tk.Label(about_window, text=PROGRAM_DESCRIPTION, font=font.Font(family='Arial', size=9, weight='normal'))
    description_label.pack(pady=5)

    # Exit button
    exit_button = tk.Button(about_window, text="Close", command=about_window.destroy, width=10)
    exit_button.pack(side=tk.BOTTOM, pady=10)

    # Make the "About" window modal
    about_window.transient(win)
    about_window.grab_set()
    about_window.focus()
    win.wait_window(about_window)

def show_help():
    help_window = tk.Toplevel(win)
    help_window.title("Help - WaterMarker")
    help_window.geometry("390x340")
    help_window.iconphoto(False, icon)
    help_window.resizable(False, False)
    help_window.attributes("-topmost", True)

    help_frame = tk.Frame(help_window, padx=16, pady=16)
    help_frame.pack(fill="both", expand=True)

    title_label = tk.Label(
        help_frame,
        text="How to use WaterMarker",
        font=font.Font(family='Arial', size=12, weight='bold')
    )
    title_label.pack(anchor="w", pady=(0, 10))

    instructions = (
        "1. Open an image using File -> Open.\n"
        "2. Enter your watermark text in the Text field.\n"
        "3. Choose a font from the Font list.\n"
        "4. Adjust Size, Transparency, and Angle using the sliders or +/- buttons.\n"
        "5. Click on the Color box to choose a text color.\n"
        "6. Save your watermarked image using File -> Save.\n\n"
        "Preferences and recent folders are automatically saved on exit."
    )
    text_label = tk.Label(
        help_frame,
        text=instructions,
        justify="left",
        wraplength=350,
        font=font.Font(family='Arial', size=9)
    )
    text_label.pack(anchor="w", fill="both", expand=True)

    close_btn = tk.Button(help_frame, text="Close", command=help_window.destroy, width=10)
    close_btn.pack(side=tk.BOTTOM, pady=(10, 0))

    help_window.transient(win)
    help_window.grab_set()
    help_window.focus()
    win.wait_window(help_window)

def center_window():
    global win, controls_frame, image1_width, image1_height
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    window_width = controls_frame.winfo_reqwidth() + 15 + image1_width
    window_height = max(320, image1_height + 20)
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    win.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

def on_font_size_scale(val):
    global updating_controls
    if updating_controls:
        return
    int_val = int(round(float(val)))
    if font_size_variable.get() != str(int_val):
        font_size_variable.set(str(int_val))
        refresh()

def on_transparency_scale(val):
    global updating_controls
    if updating_controls:
        return
    int_val = int(round(float(val)))
    if transparency_variable.get() != str(int_val):
        transparency_variable.set(str(int_val))
        refresh()

def on_angle_scale(val):
    global updating_controls
    if updating_controls:
        return
    int_val = int(round(float(val)))
    if angle_variable.get() != str(int_val):
        angle_variable.set(str(int_val))
        refresh()

def icon_plus_command(dummy=None):
    global updating_controls
    value = int(font_size_variable.get()) + 2
    if value > 150:
        value = 150
    font_size_variable.set(str(value))
    updating_controls = True
    font_size_scale.set(value)
    updating_controls = False
    refresh()

def icon_minus_command(dummy=None):
    global updating_controls
    value = int(font_size_variable.get()) - 2
    if value < 2:
        value = 2
    font_size_variable.set(str(value))
    updating_controls = True
    font_size_scale.set(value)
    updating_controls = False
    refresh()

def transparency_icon_plus_command(dummy=None):
    global updating_controls
    value = int(transparency_variable.get()) + 5
    if value > 255:
        value = 255
    transparency_variable.set(str(value))
    updating_controls = True
    transparency_scale.set(value)
    updating_controls = False
    refresh()

def transparency_icon_minus_command(dummy=None):
    global updating_controls
    value = int(transparency_variable.get()) - 5
    if value < 0:
        value = 0
    transparency_variable.set(str(value))
    updating_controls = True
    transparency_scale.set(value)
    updating_controls = False
    refresh()

def angle_icon_plus_command(dummy=None):
    global updating_controls
    value = int(angle_variable.get()) + 5
    if value > 360:
        value = 360
    angle_variable.set(str(value))
    updating_controls = True
    angle_scale.set(value)
    updating_controls = False
    refresh()

def angle_icon_minus_command(dummy=None):
    global updating_controls
    value = int(angle_variable.get()) - 5
    if value < 0:
        value = 0
    angle_variable.set(str(value))
    updating_controls = True
    angle_scale.set(value)
    updating_controls = False
    refresh()

def change_font(dummy=None):
    global font_selected
    selection = listbox_fonts.curselection()
    if selection:
        font_selected = fonts[selection[0]]
    elif fonts:
        font_selected = fonts[0]
    refresh()

def watermark_text_variable_command(var, index, mode):
    refresh()

def open_image(dummy=None):
    global root_dir, save_flag, display_image_path
    options = {
        'title': 'Select Image File',
        'filetypes': [("Image Files", ('*.png', '*.jpg', '*.jpeg', '*.gif'))],
        'initialdir': root_dir
    }

    filename = filedialog.askopenfilename(**options)
    if filename:
        display_image_path = filename
        refresh()
        center_window()
        root_dir = os.path.dirname(filename)
        save_flag = True

def save_image(dummy=None):
    global save_dir
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        initialdir=save_dir
    )
    if file_path:
        temp_out = os.path.join(TMP_DIR, 'out.png')
        if os.path.exists(temp_out):
            shutil.copy(temp_out, file_path)
            save_dir = os.path.dirname(file_path)
            messagebox.showinfo("Info", "Image saved successfully")
        else:
            messagebox.showerror("Error", "Watermarked image could not be found.")

def refresh():
    global image_photo, image_display_label, image1_width, image1_height
    global watermark_text_variable, font_size_variable, display_image_path
    global font_selected, text_color, transparency_variable, angle_variable

    if not os.path.exists(display_image_path):
        return

    win.config(cursor="watch")
    win.update_idletasks()

    try:
        base_image = Image.open(display_image_path).convert("RGBA")
    except Exception as e:
        win.config(cursor='')
        messagebox.showerror("Error", f"Failed to open image:\n{e}")
        return

    image1_width, image1_height = base_image.size
    if image1_width > 600 or image1_height > 600:
        base_image.thumbnail((600, 600))
        image1_width, image1_height = base_image.size

    text_layer = Image.new('RGBA', base_image.size, (255, 255, 255, 0))

    # Font handling
    font_size = int(font_size_variable.get())
    if font_selected and font_selected[1] and os.path.exists(font_selected[1]):
        try:
            font_obj = ImageFont.truetype(font_selected[1], font_size)
        except Exception:
            font_obj = ImageFont.load_default()
    else:
        font_obj = ImageFont.load_default()

    draw = ImageDraw.Draw(text_layer)
    text = watermark_text_variable.get()

    # Modern text bounding box calculation (Oportunidad 2)
    if text:
        bbox = draw.textbbox((0, 0), text, font=font_obj)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        width, height = base_image.size
        x = (width - text_width) / 2 - bbox[0]
        y = (height - text_height) / 2 - bbox[1]

        fill_color = (text_color[0], text_color[1], text_color[2], int(transparency_variable.get()))
        draw.text((x, y), text, fill=fill_color, font=font_obj)

    rotated_text_layer = text_layer.rotate(int(angle_variable.get()))

    # Combining Original Image with Text and Saving to TMP_DIR
    watermarked = Image.alpha_composite(base_image, rotated_text_layer)
    temp_out_path = os.path.join(TMP_DIR, 'out.png')
    watermarked.save(temp_out_path)

    image_photo = ImageTk.PhotoImage(watermarked)
    image_display_label.config(image=image_photo)
    image_display_label.image = image_photo  # Retain reference to prevent garbage collection

    win.config(cursor='')

def dialog_select_color(dummy=None, title='Select color'):
    global text_color
    color, hex_color = colorchooser.askcolor(title=title, color=color_value_hex_variable.get())
    if color and hex_color:
        text_color = tuple(map(int, color))
        color_value_hex_variable.set(hex_color)
        color_swatch.config(bg=hex_color)
        refresh()
        return True
    return False

def save_preferences():
    """Saves current settings to an INI file."""
    config = configparser.ConfigParser()
    config['Settings'] = {
        'text': watermark_text_variable.get(),
        'font_name': font_selected[0] if font_selected else '',
        'font_size': font_size_variable.get(),
        'transparency': transparency_variable.get(),
        'angle': angle_variable.get(),
        'color_rgb': ','.join(map(str, text_color)),
        'color_hex': color_value_hex_variable.get()
    }
    config['Paths'] = {
        'last_image': display_image_path,
        'last_save_dir': save_dir,
        'last_open_dir': root_dir
    }
    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    except IOError as e:
        print(f"Error saving preferences: {e}")

def load_preferences():
    """Loads settings from an INI file."""
    global text_color, display_image_path, save_dir, root_dir, font_selected, updating_controls
    if not os.path.exists(CONFIG_FILE):
        return

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    if 'Settings' in config:
        settings = config['Settings']
        watermark_text_variable.set(settings.get('text', watermark_text_variable.get()))
        
        saved_size = settings.get('font_size', font_size_variable.get())
        font_size_variable.set(saved_size)
        
        saved_transp = settings.get('transparency', transparency_variable.get())
        transparency_variable.set(saved_transp)
        
        saved_angle = settings.get('angle', angle_variable.get())
        angle_variable.set(saved_angle)

        updating_controls = True
        try:
            font_size_scale.set(int(saved_size))
            transparency_scale.set(int(saved_transp))
            angle_scale.set(int(saved_angle))
        except ValueError:
            pass
        updating_controls = False

        try:
            rgb_str = settings.get('color_rgb', '0,0,0')
            text_color = tuple(map(int, rgb_str.split(',')))
            hex_str = settings.get('color_hex', '#000000')
            color_value_hex_variable.set(hex_str)
            color_swatch.config(bg=hex_str)
        except (ValueError, IndexError):
            text_color = (0, 0, 0)
            color_value_hex_variable.set('#000000')
            color_swatch.config(bg='#000000')

        font_name_to_load = settings.get('font_name')
        if font_name_to_load and fonts:
            for i, font_item in enumerate(fonts):
                if font_item[0].lower() == font_name_to_load.lower():
                    listbox_fonts.select_clear(0, tk.END)
                    listbox_fonts.select_set(i)
                    listbox_fonts.see(i)
                    font_selected = fonts[i]
                    break

    if 'Paths' in config:
        paths = config['Paths']
        last_image_path = paths.get('last_image', display_image_path)
        if os.path.exists(last_image_path):
            display_image_path = last_image_path
        save_dir = paths.get('last_save_dir', save_dir)
        root_dir = paths.get('last_open_dir', root_dir)

def on_closing():
    """Handles window closing event to save preferences."""
    save_preferences()
    win.destroy()

# **** MAIN PROGRAM INITIALIZATION

system_fonts = fm.findSystemFonts(fontpaths=None, fontext='ttf')

fonts = []
for font_path in system_fonts:
    if '.ttf' in font_path.lower():
        font_name = os.path.splitext(os.path.basename(font_path))[0].capitalize()
        fonts.append([font_name, font_path])

fonts.sort(key=lambda x: x[0])

if not fonts:
    fonts.append(["Default", ""])

font_selected = fonts[0]

win = tk.Tk()
win.title(f'{PROGRAM_NAME}')
win.resizable(False, False)

icon_path = os.path.join(RESOURCES_DIR, 'logo.png')
if os.path.exists(icon_path):
    icon = ImageTk.PhotoImage(Image.open(icon_path))
    win.iconphoto(False, icon)
    win.icon = icon
else:
    icon = None

win.protocol("WM_DELETE_WINDOW", on_closing)

# **** MENU BAR

menu_bar = tk.Menu(win)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_image)
file_menu.add_command(label="Save", command=save_image)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=on_closing)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Help", command=show_help)
help_menu.add_command(label="About", command=show_about)

menu_bar.add_cascade(label="File", menu=file_menu)
menu_bar.add_cascade(label="Help", menu=help_menu)

win.config(menu=menu_bar)

# **** FRAMES

controls_frame = tk.Frame(win, bg=None)
image_frame = tk.Frame(win, bg=None)

controls_frame.pack(side='left', fill='y', expand=False, padx=8, pady=8)
image_frame.pack(side='right', fill='both', expand=True, padx=8, pady=8)

# **** TEXT

text_label = tk.Label(controls_frame, text="Text")
watermark_text_variable = tk.StringVar(value='The Lazy Fox')
watermark_text_variable.trace_add('write', watermark_text_variable_command)
text_entry = tk.Entry(controls_frame, textvariable=watermark_text_variable, width=24)

text_label.grid(row=0, column=0, sticky='e', padx=(0, 5), pady=3)
text_entry.grid(row=0, column=1, sticky='w', pady=3)

# **** FONT

font_label = tk.Label(controls_frame, text="Font")
font_label.grid(row=1, column=0, sticky='ne', padx=(0, 5), pady=3)

font_selection_frame = tk.Frame(controls_frame)
font_selection_frame.grid(row=1, column=1, sticky='w', pady=3)

listbox_fonts = tk.Listbox(
    font_selection_frame,
    selectmode=tk.BROWSE,
    height=6,
    width=21
)
for font_item in fonts:
    listbox_fonts.insert(tk.END, font_item[0])

listbox_fonts.select_set(0)
listbox_fonts.bind('<<ListboxSelect>>', change_font)
listbox_fonts.pack(side='left', fill='y')

font_list_scrollbar = tk.Scrollbar(font_selection_frame)
font_list_scrollbar.pack(side='right', fill='y')
font_list_scrollbar.configure(command=listbox_fonts.yview)
listbox_fonts.configure(yscrollcommand=font_list_scrollbar.set)

# Load control icons
icon_minus_path = os.path.join(RESOURCES_DIR, 'icon_minus.png')
icon_plus_path = os.path.join(RESOURCES_DIR, 'icon_plus.png')

icon_minus = ImageTk.PhotoImage(Image.open(icon_minus_path)) if os.path.exists(icon_minus_path) else None
icon_plus = ImageTk.PhotoImage(Image.open(icon_plus_path)) if os.path.exists(icon_plus_path) else None

# **** FONT SIZE (Slider + Buttons)

font_size_label = tk.Label(controls_frame, text="Size")
font_size_label.grid(row=2, column=0, sticky='e', padx=(0, 5), pady=3)

font_size_frame = tk.Frame(controls_frame)
font_size_frame.grid(row=2, column=1, sticky='w', pady=3)

if icon_minus:
    icon_minus_label = tk.Label(font_size_frame, image=icon_minus, cursor='hand2')
    icon_minus_label.image = icon_minus
    icon_minus_label.bind('<Button-1>', icon_minus_command)
    icon_minus_label.pack(side='left')

font_size_variable = tk.StringVar(value='24')
font_size_scale = ttk.Scale(
    font_size_frame,
    from_=2,
    to=150,
    orient='horizontal',
    length=100,
    command=on_font_size_scale
)
font_size_scale.set(24)
font_size_scale.pack(side='left', padx=3)

if icon_plus:
    icon_plus_label = tk.Label(font_size_frame, image=icon_plus, cursor='hand2')
    icon_plus_label.image = icon_plus
    icon_plus_label.bind('<Button-1>', icon_plus_command)
    icon_plus_label.pack(side='left')

font_size_value_label = tk.Label(font_size_frame, textvariable=font_size_variable, width=4)
font_size_value_label.pack(side='left', padx=2)

# **** TRANSPARENCY (Slider + Buttons)

transparency_label = tk.Label(controls_frame, text="Transparency")
transparency_label.grid(row=3, column=0, sticky='e', padx=(0, 5), pady=3)

transparency_frame = tk.Frame(controls_frame)
transparency_frame.grid(row=3, column=1, sticky='w', pady=3)

if icon_minus:
    transparency_icon_minus_label = tk.Label(transparency_frame, image=icon_minus, cursor='hand2')
    transparency_icon_minus_label.image = icon_minus
    transparency_icon_minus_label.bind('<Button-1>', transparency_icon_minus_command)
    transparency_icon_minus_label.pack(side='left')

transparency_variable = tk.StringVar(value='125')
transparency_scale = ttk.Scale(
    transparency_frame,
    from_=0,
    to=255,
    orient='horizontal',
    length=100,
    command=on_transparency_scale
)
transparency_scale.set(125)
transparency_scale.pack(side='left', padx=3)

if icon_plus:
    transparency_icon_plus_label = tk.Label(transparency_frame, image=icon_plus, cursor='hand2')
    transparency_icon_plus_label.image = icon_plus
    transparency_icon_plus_label.bind('<Button-1>', transparency_icon_plus_command)
    transparency_icon_plus_label.pack(side='left')

transparency_value_label = tk.Label(transparency_frame, textvariable=transparency_variable, width=4)
transparency_value_label.pack(side='left', padx=2)

# **** ANGLE (Slider + Buttons)

angle_label = tk.Label(controls_frame, text="Angle")
angle_label.grid(row=4, column=0, sticky='e', padx=(0, 5), pady=3)

angle_frame = tk.Frame(controls_frame)
angle_frame.grid(row=4, column=1, sticky='w', pady=3)

if icon_minus:
    angle_icon_minus_label = tk.Label(angle_frame, image=icon_minus, cursor='hand2')
    angle_icon_minus_label.image = icon_minus
    angle_icon_minus_label.bind('<Button-1>', angle_icon_minus_command)
    angle_icon_minus_label.pack(side='left')

angle_variable = tk.StringVar(value='45')
angle_scale = ttk.Scale(
    angle_frame,
    from_=0,
    to=360,
    orient='horizontal',
    length=100,
    command=on_angle_scale
)
angle_scale.set(45)
angle_scale.pack(side='left', padx=3)

if icon_plus:
    angle_icon_plus_label = tk.Label(angle_frame, image=icon_plus, cursor='hand2')
    angle_icon_plus_label.image = icon_plus
    angle_icon_plus_label.bind('<Button-1>', angle_icon_plus_command)
    angle_icon_plus_label.pack(side='left')

angle_value_label = tk.Label(angle_frame, textvariable=angle_variable, width=4)
angle_value_label.pack(side='left', padx=2)

# **** COLOR (Visual Swatch + Hex Label)

color_label = tk.Label(controls_frame, text="Color")
color_label.grid(row=5, column=0, sticky='e', padx=(0, 5), pady=3)

color_frame = tk.Frame(controls_frame)
color_frame.grid(row=5, column=1, sticky='w', pady=3)

color_value_hex_variable = tk.StringVar(value='#000000')

color_swatch = tk.Label(
    color_frame,
    bg='#000000',
    width=3,
    height=1,
    relief='groove',
    borderwidth=2,
    cursor='hand2'
)
color_swatch.pack(side='left', padx=(0, 6))
color_swatch.bind('<Button-1>', dialog_select_color)

color_value_label = tk.Label(
    color_frame,
    textvariable=color_value_hex_variable,
    relief='sunken',
    padx=6,
    pady=1,
    cursor='hand2'
)
color_value_label.pack(side='left', padx=(0, 6))
color_value_label.bind('<Button-1>', dialog_select_color)

# **** IMAGE DISPLAY

initial_image = Image.open(display_image_path) if os.path.exists(display_image_path) else Image.new('RGBA', (300, 300), (200, 200, 200, 255))
image1_width, image1_height = initial_image.size
if image1_width > 600 or image1_height > 600:
    initial_image.thumbnail((600, 600))
    image1_width, image1_height = initial_image.size

image_photo = ImageTk.PhotoImage(initial_image)
image_display_label = tk.Label(image_frame, image=image_photo)
image_display_label.image = image_photo
image_display_label.pack()

# **** EXECUTION

load_preferences()
change_font()
refresh()
center_window()
win.mainloop()
