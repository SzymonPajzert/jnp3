import random


def random_bool(size):
    """Generate random list of bools with given size."""

    result = []

    for i in range(size):
        result.append(random.choice([True, False]))

    return result
