from graphics import *
from tkinter.filedialog import askopenfilename

def click_button(win, target):
    click = win.getMouse()
    while (click.getX() < target.getP1().getX() 
        or click.getX() > target.getP2().getX() 
        or click.getY() < target.getP1().getY() 
        or click.getY() > target.getP2().getY()):
        click = win.getMouse()
    return True

def main():
    # Create a graphics window with labels on left edge
    win = GraphWin("Word Counter", 500, 500)
    win.setBackground("white")

    # Get principal and interest rate
    instruction = Text(Point(250, 250), "Choose text file to analyse")
    button = Rectangle(Point(210, 275), Point(290, 315))
    button_text = Text(Point(250, 295), "Select")
    button.setOutline("grey")
    button.setWidth(2)
    button.setFill("light grey")
    button.draw(win)
    instruction.draw(win)
    button_text.draw(win)

    filename = ""
    warning_text = Text(Point(250, 225), "File not selected or is invalid!")
    while True:
        click_button(win, button)
        filename = askopenfilename()
        warning_text.undraw()
        if filename.endswith(".txt"):
            break
        else:
            warning_text.setTextColor("red")
            warning_text.setStyle('bold')
            warning_text.draw(win)

    infile = open(filename, 'r', encoding='utf-8')
    chars_all = chars = words = lines = 0
    for line in infile:
        lines += 1
        chars_all += len(line)
        no_nl_line = line.rstrip("\n")
        chars += len(no_nl_line)
        for l in no_nl_line.split(" "):
            l = l.strip()
            words += 1 if l else 0
    infile.close()

    button.undraw()
    instruction.undraw()
    button_text.undraw()

    label = Text(Point(250, 100), "Count")
    label_word = Text(Point(200-50, 150), "Words")
    label_chars = Text(Point(217-50, 200), "Characters")
    label_lines = Text(Point(195-50, 250), "Lines")
    label.getAnchor()
    label_chars.setStyle("italic")
    label_lines.setStyle("italic")
    label_word.setStyle("italic")
    label.setStyle("bold")

    word_res = Rectangle(Point(250, 130), Point(380, 170))
    char_res = Rectangle(Point(250, 180), Point(380, 220))
    line_res = Rectangle(Point(250, 230), Point(380, 270))
    word_res.setFill("light blue")
    char_res.setFill("light blue")
    line_res.setFill("light blue")
    word_res_txt = Text(Point((250+380)/2, 150), str(words))
    char_res_txt = Text(Point((250+380)/2, 200), str(chars) + " (%s)" % str(chars_all))
    line_res_txt = Text(Point((250+380)/2, 250), str(lines))
    word_res.draw(win)
    char_res.draw(win)
    line_res.draw(win)
    word_res_txt.draw(win)
    char_res_txt.draw(win)
    line_res_txt.draw(win)

    exit_btn_label = Text(Point(250, 355), "Close window")
    exit_btn = Rectangle(Point(150, 330), Point(350, 380))
    exit_btn.setOutline("grey")
    exit_btn.setWidth(2)
    exit_btn.setFill("light grey")

    exit_btn.draw(win)
    exit_btn_label.draw(win)
    label.draw(win)
    label_word.draw(win)
    label_chars.draw(win)
    label_lines.draw(win)

    click_button(win, exit_btn)
    win.close()

main()
