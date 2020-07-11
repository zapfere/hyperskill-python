your_choice = "Your choice: "
error = "The operation cannot be performed."
wrong_input = "Wrong input! {} space separated numbers expected"
wrong_num = "Wrong input! One number expected"
enter_size = "Enter size of {}matrix: "
enter_matrix = "Enter {}matrix:"
result_is = "The result is:"
max_decimals = 3


def process_matrix(row_count, column_count, operator):
    """Iterate elements row-by-row and apply given operator"""

    result = []
    for i in range(row_count):
        row = []
        for j in range(column_count):
            row.append(operator(i, j))
        result.append(row)

    return result


def print_matrix(matrix):
    """Print given matrix row-by-row"""

    print(result_is)
    max_len = max((len(str(round(n))) for row in matrix for n in row))
    cell_pattern = "{{:{pos}.{part}f}}"\
        .format(pos=max_len + max_decimals + 2, part=max_decimals)
    for row in matrix:
        row_gen = (cell_pattern.format(cell) for cell in row)
        print(*row_gen)


def build_matrix(prompt_size, prompt_matrix):
    """Ask for size and elements, return 2D array"""

    rows, cols = [int(i) for i in get_num_row(
        2,
        lambda x: int(x),
        prompt=prompt_size
    )]
    matrix = []

    print(prompt_matrix)
    for i in range(rows):
        row = get_num_row(cols, lambda x: float(x))
        matrix.append(row)

    return matrix


def get_num_row(size, element_processor, prompt=""):
    """Ask for 'count' space separated numbers, repeat until done"""

    try:
        result = [element_processor(n) for n in input(prompt).split()]
        if len(result) != size:
            raise ValueError
        return result

    except ValueError:
        print(wrong_num if size == 1 else wrong_input.format(size))
        return get_num_row(size, element_processor, prompt)
