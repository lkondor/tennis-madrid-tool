def safe_div(a, b):
    return a / b if b else 0.0

def clip(value, low, high):
    return max(low, min(value, high))
