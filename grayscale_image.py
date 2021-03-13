import re
from pathvalidate import ValidationError, validate_filename
from graphics import *
from tkinter.filedialog import askopenfilename

def click_button(win: GraphWin, target):
    click = win.getMouse()
    while (click.getX() < target.getP1().getX() 
        or click.getX() > target.getP2().getX() 
        or click.getY() < target.getP1().getY() 
        or click.getY() > target.getP2().getY()):
        click = win.getMouse()
    return True

def is_valid_filename(filename: str):
    try:
        validate_filename(filename, platform="Windows")
        return True
    except ValidationError as e:
        print(e)
        return False

def main():
    # Create a graphics window with labels on left edge
    win = GraphWin("Grayscale Image Converter", 500, 500)
    win.setBackground("white")

    # Get principal and interest rate
    instruction = Text(Point(250, 250), "Choose image (.GIF or .PPM) file to convert")
    button = Rectangle(Point(210, 275), Point(290, 315))
    button_text = Text(Point(250, 295), "Select")
    button.setOutline("grey")
    button.setWidth(2)
    button.setFill("light grey")
    button.draw(win)
    instruction.draw(win)
    button_text.draw(win)

    exit_btn_label = Text(Point(250, 355), "Close window")
    exit_btn = Rectangle(Point(150, 330), Point(350, 380))
    exit_btn.setOutline("grey")
    exit_btn.setWidth(2)
    exit_btn.setFill("light grey")

    filename = ""
    no_file_text = Text(Point(250, 225), "No file selected")
    no_file_text.setTextColor("red")
    no_file_text.setStyle('bold')
    wrong_file_text = Text(Point(250, 225), "Invalid file format")
    wrong_file_text.setTextColor("red")
    wrong_file_text.setStyle('bold')
    while True:
        click_button(win, button)
        filename = askopenfilename()
        wrong_file_text.undraw()
        no_file_text.undraw()
        if not filename.strip():
            no_file_text.draw(win)
        elif not filename.endswith(('.gif', '.ppm')):
            wrong_file_text.draw(win)
        else:
            break

    print(filename)
    try:
        gr_file = Image(Point(0,0), filename)
    except Exception as e:
        print(e)
        warning_text = Text(Point(250, 225), "File not readable")
        warning_text.setTextColor("red")
        warning_text.setStyle('bold')
        warning_text.draw(win)
        exit_btn.draw(win)
        exit_btn_label.draw(win)
        click_button(win, exit_btn)
        win.close()
        return

    # open new window with the image
    img_height =  gr_file.getHeight()
    img_width = gr_file.getWidth()
    win_width = 500 if img_width < 450 else img_width+50
    win_height = 500 if img_height < 380 else img_height+120
    win_cx, win_cy = win_width/2, win_height/2
    win.close()
    win = GraphWin("Grayscale Image Converter", win_width, win_height)
    # win.setBackground("black")
    gr_file.move(win_cx, win_cy-35)
    gr_file.draw(win)

    convert_btn_label = Text(Point(win_cx, win_height-50), "Convert to grey")
    convert_btn = Rectangle(Point(win_cx-75, win_height-75), Point(win_cx+75, win_height-25))
    convert_btn.setOutline("grey")
    convert_btn.setWidth(2)
    convert_btn.setFill("light grey")
    convert_btn.draw(win)
    convert_btn_label.draw(win)
    click_button(win, convert_btn)

    convert_btn_label.undraw()
    convert_btn.undraw()
    loading_message = Text(Point(win_cx, win_height-50), "Please, wait. The image is converting...")
    loading_message.setStyle('bold italic')
    loading_message.draw(win)
    for y in range(img_height):
        for x in range(img_width):
            r, g, b = gr_file.getPixel(x, y)
            br = int(round(0.299*r + 0.578*g + 0.114*b))
            gr_file.setPixel(x, y, color_rgb(br, br, br))
        gr_file.undraw()
        gr_file.draw(win)
    loading_message.undraw()

    save_modal = GraphWin("", 500, 200)
    new_fn_field = Entry(Point(310, 25), 23)
    new_fn_field.setFill("white")
    new_fn_field.setFace("courier")
    new_fn_label = Text(Point(90, 25), "New file name")
    new_fn_label.draw(save_modal)
    new_fn_field.draw(save_modal)
    
    save_btn_label = Text(Point(250, 160), "Save File")
    save_btn = Rectangle(Point(200, 135), Point(300,185))
    save_btn.setOutline("grey")
    save_btn.setWidth(2)
    save_btn.setFill("light grey")
    save_btn.draw(save_modal)
    save_btn_label.draw(save_modal)
    
    click_button(save_modal, save_btn)
    while not is_valid_filename(new_fn_field.getText()):
        fn_warning = Text(Point(250, 75), "Invalid input. Try again.")
        fn_warning.setStyle('bold')
        fn_warning.setTextColor('red')
        fn_warning.draw(save_modal)
        click_button(save_modal, save_btn)
        fn_warning.undraw()

    dir = "/".join(filename.split("/")[:-1])
    new_fn = new_fn_field.getText().strip() + filename[-4:]
    save_fn = dir + "/" + new_fn
    gr_file.save(save_fn)
    save_modal.close()
    saved_msg = Text(Point(win_cx, win_height-50), "File saved. Click to QUIT")
    saved_msg.setTextColor('green')
    saved_msg.setStyle('bold')
    saved_msg.draw(win)

    win.getMouse()
    win.close()

main()