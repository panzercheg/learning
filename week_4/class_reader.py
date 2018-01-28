import os
import tempfile


class File:
    def __init__(self, path_to_file):
        self.path = path_to_file
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
        # from https://stackoverflow.com/questions/19151/build-a-basic-python-iterator
        if self.current_line >= self.file_len:
            raise StopIteration
        else:
            self.current_line += 1
            return self.__content[self.current_line - 1]

    def __iter__(self):
        self.current_line = 0
        return self

    def __str__(self):
        return os.path.abspath(self.path)  # не уверен что вот тут правильно, хотят полный путь при инициализации...

    def read(self):
        try:
            with open(self.path, 'r') as file:
                return [_.strip() for _ in file.readlines()]
        except IOError:
            return ["Файла по даному пути не существует"]

    def write(self, line_to_add=None):
        try:
            with open(self.path, 'w') as file:
                if line_to_add:
                    self.__content.append(line_to_add)
                file.write('\n'.join(self.__content))
                return file
        except IOError:
            return ["Файла по даному пути не существует"]


def main():
    first = File("N:\\test.txt")
    second = File("N:\\test2.txt")
    # first.write('3\n')
    # for line in first:
    #     print(line)
    '''
    если раскоментировать цикл внизу, то увидим, что моя реализация - кривая:
    ну т.е. будут идти пропуски с якобы пустой строкой, а я так не хочу, но тоже затык
    как сделать по-другому, не понимаю
    '''
    # for idx, line in enumerate(first + second):
    #     print('#{}: "{}"'.format(idx, line))


if __name__ == "__main__":
    main()