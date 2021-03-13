from graphics import *

def main():
    # ask for number of dies to depict
    number = input("how many dice to draw? 1-6... ")
    try:
        number = int(number)
        if (number < 1 or number > 6):
            raise ValueError()
    except:
        print("Input must be a number between 1 and 6")
        return

    draw_dice(number)

def draw_dice(num):

    # parent rectangle
    side = 58
    half_side = side/2
    dot_thickness = 6
    offset = 10

    width = 500 + (num - 5) * 70 if num > 5 else 500
    height = 500
    center = Point(width/2, height/2)
    win = GraphWin(width=width, height=height)

    die_set = [i+1 for i in range(num)]
    die = Rectangle(Point(center.getX()-half_side, center.getY()+half_side), 
                    Point(center.getX()+half_side, center.getY()-half_side))
    die.setOutline("black")
    die.setFill("white")
    die.setWidth(2)

    for i in range(num):
        further_dies = num-(i+1)
        new_die = die.clone()
        #new_die.move(-(side + offset)*further_dies + ((side*num + offset*(num-1))/2) - half_side, 0)
        new_die.move((side + offset) * (-further_dies + 0.5 * (num-1)), 0) # same as above but reduced
        new_die.draw(win)
        print(new_die.getCenter())
        dot = Circle(new_die.getCenter(), dot_thickness/2)
        dot.setFill("black")
        if die_set[i]%2 == 1:
            dot.draw(win)
        if die_set[i] == 6:
            for y in range(6):
                side_dot = get_dot(dot.clone(), y+1, side)
                side_dot.draw(win)
        elif die_set[i] > 1:
            left_upper = get_dot(dot.clone(), 1, side)
            right_lower = get_dot(dot.clone(), 6, side)
            left_upper.draw(win)
            right_lower.draw(win)
            if die_set[i] > 3:
                left_lower = get_dot(dot.clone(), 4, side)
                right_upper = get_dot(dot.clone(), 3, side)
                left_lower.draw(win)
                right_upper.draw(win)

    Text(Point(250,450), "Click again to quit").draw(win)
    win.getMouse()
    win.close()    # Close window when done

def get_dot(dot, num, side_len):
    dot_offset = side_len/4
    if (num < 1 or num > 6):
        return Exception("Invalid dot position number")

    dx = dot_offset
    dy = dot_offset if num < 4 else -dot_offset
    if (num == 2 or num == 5):
        dx = 0
    elif (num == 1 or num == 4):
        dx = -dot_offset

    dot.move(dx, dy)
    return dot

main()