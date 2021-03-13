# Random Walk simulation in 1D
from random import randrange

UP, DOWN, LEFT, RIGHT = 1, 2, 3, 4

def get_total_shift(steps):
    if steps < 25:
        vis = draw_empty_vis(steps)
    shift_x, shift_y = 0, 0
    for i in range(steps):
        move = randrange(1, 5)
        if move > 2:
            shift_x += 1 if move == RIGHT else -1
        else:
            shift_y += 1 if move == UP else -1

        if steps < 25:
            vis = edit_visual(steps, shift_x, shift_y, vis=vis)
    if steps < 25:
        s = ''
        for row in vis:
            s += row + '\n'
        print(s)

    return shift_x, shift_y
    
def draw_empty_vis(steps):
    row_list = []
    row_length = steps * 2 + 1
    chars = {
        'row_char': '__', 
        'center': '++', 
        'padding': '**'
    }
    row_list.append(((row_length + 2) * chars['padding']).center(39))
    for i in range(steps * 2 + 1):
        row_str = chars['padding']
        if i == steps:
            row_str += chars['row_char'] * steps + chars['center'] + chars['row_char'] * steps
        else:
            row_str += chars['row_char'] * steps + chars['row_char'] + chars['row_char'] * steps
        row_str += chars['padding']
        row_list.append(row_str.center(40))
    row_list.append(((row_length + 2) * chars['padding']).center(39))
    return row_list

def edit_visual(steps, posx, posy, vis=[]):
    chars = {
        'row_char': '__', 
        'center': '++', 
        'padding': '**',
        'mark': 'X.'
    }
    i_target = steps + 1 - posy
    str_row = vis[i_target]
    i_center = (len(str_row) / 2) - 1
    if posx != 0:
        i_change = int(i_center + posx * len(chars['row_char']))
    elif posy != 0:
        i_change = int(i_center)
    else:
        return vis
    
    str_row = "".join([
        str_row[:i_change], 
        chars['mark'], 
        str_row[i_change+len(chars['mark']):]
        ])

    vis[i_target] = str_row
    return vis

def simulate_walks():
    # get number of steps, number of simulations inputs
    steps = int(input('How many steps in a walk? '))
    sim_n = int(input('How many simulations to run? ' ))

    steps_total = 0
    for i in range(sim_n):
        steps_x, steps_y = get_total_shift(steps)
        steps_total += abs(steps_x) + abs(steps_y)
    avg = steps_total / sim_n
    print("Average steps taken away from the start in any direction is", round(avg, 1))

simulate_walks()