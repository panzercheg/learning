import sys
import os


class FileReader:
    def __init__(self, read_file):
        self.read_file = read_file

    def read(self):
        file = os.path.join(sys.argv[1], self.read_file)
        while True:
            try:
                with open(file, "r") as file_read:
                    lines = ''.join(file_read.readlines())
                    return lines
            except IOError:
                err_txt = ""
                return err_txt


def main():
    reader = FileReader("test.txt")
    print(reader.read())


if __name__ == "__main__":
    main()
