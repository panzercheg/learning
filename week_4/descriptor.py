class ImportantValue:
    def __get__(self, obj, obj_type):
        pass

    def __set__(self, obj, value):
        pass


class Class:
    attr = Descriptor()

new_obj = Class()
print(new_obj.attr)