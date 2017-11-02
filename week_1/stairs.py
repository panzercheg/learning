import sys

summ = str()
digit_string = sys.argv[1]
if not digit_string.isdigit():
    print("Введите числовое значение")
if digit_string.isdigit():
    for i in range(int(digit_string),0,-1):
        print(' '*(i-1) + "#"*(int(digit_string)-i+1))