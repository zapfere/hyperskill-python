# constants
max_decimals = 3
error = "The operation cannot be performed."
no_inverse = "This matrix doesn't have an inverse."
wrong_input = "Wrong input! {} space separated numbers expected"
wrong_num = "Wrong input! One number expected"
your_choice = "Your choice: "
result_is = "The result is:"
enter_size = "Enter size of {}matrix: "
enter_matrix = "Enter {}matrix:"
enter_k = "Enter constant: "
first = "first "
second = "second "
menu_text = """
1. Add matrices
2. Multiply matrix by a constant
3. Multiply matrices
4. Transpose matrix
5. Calculate a determinant
6. Inverse matrix
0. Exit"""
transpose_text = """
1. Main diagonal
2. Side diagonal
3. Vertical line
4. Horizontal line"""


def do_action(action_code):
    """Choose action by given code and perform it"""

    if action_code == "1":
        add_matrices()

    elif action_code == "2":
        scale_matrix()

    elif action_code == "3":
        multiply_matrices()

    elif action_code == "4":
        do_transpose_matrix()

    elif action_code == "5":
        do_calc_determinant()

    elif action_code == "6":
        do_inverse_matrix()


def add_matrices():
    """Add two matrices"""

    matrix1 = build_matrix(
        enter_size.format(first),
        enter_matrix.format(first)
    )
    matrix2 = build_matrix(
        enter_size.format(second),
        enter_matrix.format(second)
    )

    print_add_matrices(matrix1, matrix2)


def scale_matrix():
    """Multiply matrix by a constant number"""

    matrix = build_matrix(
        enter_size.format(""),
        enter_matrix.format("")
    )
    k = get_num_row(1, lambda x: float(x), prompt=enter_k)[0]

    print_scale_matrix(matrix, k)


def multiply_matrices():
    """Multiply two matrices"""

    matrix1 = build_matrix(
        enter_size.format(first),
        enter_matrix.format(first)
    )
    matrix2 = build_matrix(
        enter_size.format(second),
        enter_matrix.format(second)
    )

    print_multiply_matrices(matrix1, matrix2)


def do_transpose_matrix():
    """Select kind of transposition and perform it"""

    print(transpose_text)

    t_code = input(your_choice).strip()
    if t_code not in "1234":
        print(error)
        return

    matrix = build_matrix(
        enter_size.format(""),
        enter_matrix.format("")
    )

    print_transpose(matrix, t_code)


def do_calc_determinant():
    """Calculate determinant"""

    matrix = build_matrix(
        enter_size.format(""),
        enter_matrix.format("")
    )

    if is_square_matrix(matrix):
        det = calc_determinant(matrix)
        print(result_is)
        print(det)


def do_inverse_matrix():
    """Calculate inverse matrix"""

    matrix = build_matrix(
        enter_size.format(""),
        enter_matrix.format("")
    )

    if is_square_matrix(matrix):
        det = calc_determinant(matrix)

        if det == 0:
            print(no_inverse)
            return

        print_inverse_matrix(matrix, det)


def is_square_matrix(matrix):
    """Check if matrix is square, print error text in other case"""

    is_square = len(matrix) == len(matrix[0])

    if not is_square:
        print(error)

    return is_square


def calc_determinant(matrix):
    """Recursive determinant calculation"""

    first_row = matrix[0]

    if len(matrix[0]) == 1:
        return first_row[0]

    det = 0

    for j in range(len(first_row)):
        cell = first_row[j]
        if cell != 0:
            det += cell * calc_cofactor(0, j, matrix)

    return det


def print_inverse_matrix(matrix, determinant):
    """Calculate inverse matrix with given determinant"""

    new_matrix = []
    size = len(matrix[0])

    for i in range(size):

        row = []
        for j in range(size):
            cofactor = calc_cofactor(i, j, matrix)
            row.append(cofactor)

        new_matrix.append(row)

    new_matrix = transpose_main(new_matrix)
    print_scale_matrix(new_matrix, 1 / determinant)


def calc_cofactor(i, j, matrix):
    """(I,J) cofactor calculation"""

    lesser_matrix = []
    row_len = len(matrix[0])
    right_border = j + 1
    k = (-1) ** (2 + i + j)

    for row_idx in range(0, row_len):

        if row_idx == i:
            continue

        old_row = matrix[row_idx]
        new_row = get_row_part(old_row, row_len, j, right_border)
        lesser_matrix.append(new_row)

    return k * calc_determinant(lesser_matrix)


def get_row_part(row, row_len, left_border, right_border):
    """Gets row without part between left_border and right_border"""

    new_row = []

    if left_border != -1:
        new_row.extend(row[:left_border])

    if right_border != row_len:
        new_row.extend(row[right_border:])

    return new_row


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


def process_matrix(row_count, column_count, operator):
    """Iterate elements row-by-row and apply given operator"""

    result = []
    for i in range(row_count):
        row = []
        for j in range(column_count):
            row.append(operator(i, j))
        result.append(row)

    return result


def print_add_matrices(matrix1, matrix2):
    """Print matrix addition result or error"""

    if len(matrix1) == len(matrix2) and len(matrix1[0]) == len(matrix2[0]):

        result = process_matrix(
            len(matrix1),
            len(matrix1[0]),
            lambda i, j: matrix1[i][j] + matrix2[i][j]
        )
        print_matrix(result)

    else:
        print(error)


def print_scale_matrix(matrix, scale):
    """Multiply matrix by given number"""

    result = process_matrix(
        len(matrix),
        len(matrix[0]),
        lambda i, j: matrix[i][j] * scale
    )
    print_matrix(result)


def print_multiply_matrices(matrix1, matrix2):
    """Multiply two matrices"""

    if len(matrix1[0]) == len(matrix2):

        result = process_matrix(
            len(matrix1),
            len(matrix2[0]),
            lambda i, j: compute_mult_cell(i, j, matrix1, matrix2)
        )
        print_matrix(result)

    else:
        print(error)


def compute_mult_cell(i, j, matrix1, matrix2):
    """Computes one cell for two matrices' multiplication result"""

    row = matrix1[i]
    column = [m_row[j] for m_row in matrix2]

    result = 0
    for k in range(len(row)):
        result += row[k] * column[k]

    return result


def print_transpose(matrix, t_code):
    """Perform requested transposition and print result"""

    result = []

    if t_code == "1":
        result = transpose_main(matrix)

    elif t_code == "2":
        result = transpose_side(matrix)

    elif t_code == "3":
        result = transpose_vertical(matrix)

    elif t_code == "4":
        result = transpose_horizontal(matrix)

    print_matrix(result)


def transpose_main(matrix):
    """Transposition around main diagonal"""

    return process_matrix(
        len(matrix[0]),
        len(matrix),
        lambda i, j: matrix[j][i]
    )


def transpose_side(matrix):
    """Transposition around side diagonal"""

    return process_matrix(
        len(matrix[0]),
        len(matrix),
        lambda i, j: matrix[-j - 1][-i - 1]
    )


def transpose_vertical(matrix):
    """Transposition around vertical middle line"""

    return process_matrix(
        len(matrix),
        len(matrix[0]),
        lambda i, j: matrix[i][-j - 1]
    )


def transpose_horizontal(matrix):
    """Transposition around horizontal middle line"""

    return process_matrix(
        len(matrix),
        len(matrix[0]),
        lambda i, j: matrix[-i - 1][j]
    )


def print_matrix(matrix):
    """Print given matrix row-by-row"""

    print(result_is)
    max_len = max((len(str(round(n))) for row in matrix for n in row))
    cell_pattern = "{{:{pos}.{part}f}}"\
        .format(pos=max_len + max_decimals + 2, part=max_decimals)
    for row in matrix:
        row_gen = (cell_pattern.format(cell) for cell in row)
        print(*row_gen)


# main logic
code = ""
while code != "0":
    print(menu_text)
    code = input(your_choice).strip()
    do_action(code)
