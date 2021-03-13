from graphics import *

def main():
    win = GraphWin(width=500, height=500)
    shape = Rectangle(Point(50,50), Point(100,100))
    shape.setOutline("red")
    shape.setFill("red")
    shape.draw(win)

    for i in range(10):
        p = win.getMouse() # Pause to view result
        c = shape.getCenter()
        dx = p.getX() - c.getX()
        dy = p.getY() - c.getY()
        next_shape = shape.clone()
        next_shape.draw(win)
        next_shape.move(dx, dy)
    Text(Point(250,450), "Click again to quit").draw(win)
    win.getMouse()
    win.close()    # Close window when done

main()