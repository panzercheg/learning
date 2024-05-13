class Solution:
    def isPalindrome(self, x: int) -> bool:
        if ((-2 ** 31) <= x) and (x <= (2 ** 31 - 1)):
            if str(x)[::-1] == str(x):
                print("palindrome is {}".format(x))
                return True
            else:
                return False
        else:
            print("Число вне диапазона")


class Solution2:
    def isPalindrome(self, x: int) -> bool:
        if -2**31 <= x <= 2**31 - 1:
            return str(x) == str(x)[::-1]
        else:
            print("Число вне диапазона")

def main():
    x = -121
    solution = Solution().isPalindrome(x)
    print(solution)


if __name__ == "__main__":
    main()

