from general import build_matrix, enter_matrix, enter_size, \
    error, print_matrix, process_matrix, your_choice


transpose_text = """
1. Main diagonal
2. Side diagonal
3. Vertical line
4. Horizontal line"""


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
