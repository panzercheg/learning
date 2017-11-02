import sys

a = int(sys.argv[1])
b = int(sys.argv[2])
c = int(sys.argv[3])

disc = ( b * b ) - 4 * a * c
if disc > 0:
    root_1 = (-b + disc ** 0.5) / 2 * a
    root_2 = (-b - disc ** 0.5) / 2 * a
    print(int(root_1))
    print(int(root_2))
elif disc == 0:
    root_1 = (-b + disc ** 0.5) / 2 * a
    print(int(root_1))
elif disc < 0:
    print("Уравнение не имеет действительных корней")