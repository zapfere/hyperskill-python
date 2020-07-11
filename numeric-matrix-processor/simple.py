from general import build_matrix, enter_size, enter_matrix, \
    error, get_num_row, print_matrix, process_matrix


enter_k = "Enter constant: "
first = "first "
second = "second "


def do_add_matrices():
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


def do_scale_matrix():
    """Multiply matrix by a constant number"""

    matrix = build_matrix(
        enter_size.format(""),
        enter_matrix.format("")
    )
    k = get_num_row(1, lambda x: float(x), prompt=enter_k)[0]

    print_scale_matrix(matrix, k)


def do_multiply_matrices():
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
