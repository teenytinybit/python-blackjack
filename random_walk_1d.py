# Random Walk simulation in 1D
from random import randrange

def get_total_shift(steps):
    shift = 0
    for i in range(steps):
        shift += randrange(-1, 2, 2)
    abs_shift = shift if shift >= 0 else (shift * -1)
    return abs_shift

def simulate_walks():
    # get number of steps, number of simulations inputs
    steps = int(input('How many steps in a walk? '))
    sim_n = int(input('How many simulations to run? ' ))

    steps_total = 0
    for i in range(sim_n):
        steps_total += get_total_shift(steps)
    avg = steps_total / sim_n
    print("Average steps taken away from the start in any direction is", avg)

simulate_walks()