from general import enter_size, enter_matrix, error, build_matrix, result_is
from simple import print_scale_matrix
from transpose import transpose_main


no_inverse = "This matrix doesn't have an inverse."


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


def is_square_matrix(matrix):
    """Check if matrix is square, print error text in other case"""

    is_square = len(matrix) == len(matrix[0])

    if not is_square:
        print(error)

    return is_square


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
