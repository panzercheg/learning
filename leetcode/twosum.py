from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        num_to_index = {}

        # Создаем словарь, где ключами являются числа из nums, а значениями - их индексы
        for i, num in enumerate(nums):
            num_to_index[num] = i

        # Проверяем, есть ли комплемент текущего числа в словаре
        for i, num in enumerate(nums):
            complement = target - num
            # Если комплемент есть в словаре и его индекс не совпадает с индексом текущего числа
            if complement in num_to_index and num_to_index[complement] != i:
                # Возвращаем индексы текущего числа и его комплемента
                return [i, num_to_index[complement]]

        # Если не найдено решение, возвращаем пустой список
        print("решение не найдено")
        return []

def main():
    nums = [140, 24, 11, 15, 2, 97, 43, 11, 35, 140, 24, 11, 15, 2, 97, 43, 11, 35140, 24, 11, 15, 2, 97, 43, 11, 35140,
            24, 11, 15, 2, 97, 43, 11, 35140, 24, 11, 15, 2, 97, 43, 11, 35140, 24, 11, 15, 2, 97, 43, 11, 35140, 24, 11,
            15, 2, 97, 43, 11, 35140, 24, 11, 15, 2, 97, 43, 11, 35, 7]
    target = 9
    solution = Solution()
    result = solution.twosum(nums, target)
    print("Наш target: {}\n"
          "Индексы двух чисел, сумма которых равна target: {}".format(target, result))

if __name__ == "__main__":
    main()