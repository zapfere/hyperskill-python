from general import your_choice
from determinant import do_calc_determinant, do_inverse_matrix
from simple import do_add_matrices, do_multiply_matrices, do_scale_matrix
from transpose import do_transpose_matrix


menu_text = """
1. Add matrices
2. Multiply matrix by a constant
3. Multiply matrices
4. Transpose matrix
5. Calculate a determinant
6. Inverse matrix
0. Exit"""


def do_action(action_code):
    """Choose action by given code and perform it"""

    if action_code == "1":
        do_add_matrices()

    elif action_code == "2":
        do_scale_matrix()

    elif action_code == "3":
        do_multiply_matrices()

    elif action_code == "4":
        do_transpose_matrix()

    elif action_code == "5":
        do_calc_determinant()

    elif action_code == "6":
        do_inverse_matrix()


def main():
    code = ""
    while code != "0":
        print(menu_text)
        code = input(your_choice).strip()
        do_action(code)


if __name__ == '__main__':
    main()
