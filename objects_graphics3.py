# futval_graph2.py

from graphics import *

def main():
    # Introduction
    print("This program plots the growth of a 10-year investment.")

    # Create a graphics window with labels on left edge
    win = GraphWin("Investment Growth Chart", 900, 600)
    win.setBackground("white")

    # Get principal and interest rate
    entry_text = Text(Point(450, 250), "Enter the initial principal: ")
    principal_e = Entry(Point(450, 280), 20)
    principal_e.setFill("light grey")

    entry_text2 = Text(Point(450, 330), "Enter the annualized interest rate: ")
    apr_e = Entry(Point(450, 360), 20)
    apr_e.setFill("light grey")

    button = Rectangle(Point(400, 400), Point(500, 450))
    button_text = Text(Point(450, 425), "OK")
    button.setOutline("grey")
    button.setWidth(2)
    button.setFill("light grey")
    
    button.draw(win)
    button_text.draw(win)
    entry_text.draw(win)
    entry_text2.draw(win)
    principal_e.draw(win)
    apr_e.draw(win)

    button_click = win.getMouse()
    while (button_click.getX() < button.getP1().getX() 
        or button_click.getX() > button.getP2().getX() 
        or button_click.getY() < button.getP1().getY() 
        or button_click.getY() > button.getP2().getY()):
        button_click = win.getMouse()

    principal = float(principal_e.getText())
    apr = float(apr_e.getText())
    
    win.setCoords(-1.75,-200, 11.5, 10400)
    Text(Point(-1, 0), ' 0.0K').draw(win)
    Text(Point(-1, 2500), ' 2.5K').draw(win)
    Text(Point(-1, 5000), ' 5.0K').draw(win)
    Text(Point(-1, 7500), ' 7.5k').draw(win)
    Text(Point(-1, 10000), '10.0K').draw(win)

    # Draw bar for initial principal
    bar = Rectangle(Point(0, 0), Point(1, principal))
    bar.setFill("green")
    bar.setWidth(2)
    bar.draw(win)
    
    # Draw a bar for each subsequent year
    for year in range(1, 11):
        principal = principal * (1 + apr)
        bar = Rectangle(Point(year, 0), Point(year+1, principal))
        bar.setFill("green")
        bar.setWidth(2)
        bar.draw(win)

    win.getMouse()
    win.close()

main()