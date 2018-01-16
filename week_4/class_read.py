import os
import tempfile


class File:
    def __init__(self, path_to_file):
        self.path = path_to_file
        self.__content = []
        self.__content = self.read()
        self.file_len = len(self.__content)
        self.current_line = None

    def __add__(self, obj):
        storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')
        tmpobj = File(storage_path)
        tmpobj.__content = self.__content + obj.__content
        tmpobj.write()
        return tmpobj

    def __next__(self):
        if self.current_line >= self.file_len:
            raise StopIteration
        else:
            self.current_line += 1
            return self.__content[self.current_line - 1]

    def __iter__(self):
        self.current_line = 0
        return self

    def __str__(self):
        return self.path

    def read(self):
        try:
            with open(self.path, 'r+') as file:
                return [_.strip() for _ in file.readlines()]
        except IOError:
            self.write()
            return self.read()
            # return ["Файла по даному пути не существует"]

    def write(self, line_to_add=None):
            with open(self.path, 'w') as file:
                if line_to_add:
                    self.__content.append(line_to_add)
                file.write('\n'.join(self.__content))
                return self
            raise IOError ("Файла по даному пути не существует")


def main():
    first = File("test1.txt").write("2\n4")
    second = File("text2.txt").write("3\n5")
    third = first + second
    # for line in third:
    #     print(line)
    for idx, line in enumerate(third):
        print('#{}: "{}"'.format(idx, line))
    print(third)


if __name__ == "__main__":
    main()