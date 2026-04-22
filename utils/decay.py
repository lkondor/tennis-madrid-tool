import math
def time_decay(months, lamb=0.08):
    return math.exp(-lamb * months)
