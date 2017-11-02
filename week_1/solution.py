import sys

summ = str()
digit_string = sys.argv[1]

if not digit_string.isdigit():
    print("Введите числовое значение")
elif digit_string.isdigit():
    for i in digit_string:
        i = "#"
        summ += str(i) * int(digit_string)
        print(summ)
        # print(summ[::-1])