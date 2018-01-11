import json


class Pet:
    def __init__(self, name):
        self.name = name


class Dog(Pet):
    def __init__(self, name, breed=None):
        super().__init__(name)
        self.breed = breed


class ExDog(Dog):
    def __init__(self, name, breed=None, exporter=None):
        self._exporter = exporter or ExportJSON()
        if not isinstance(self._exporter, PetExport):
            raise ValueError("bad exporter", exporter)
        self.breed = breed
        super().__init__(name, breed=None)


    def export(self):
        return self._exporter.export(self)


class PetExport:
    def export(self, dog):
        raise NotImplementedError


class ExportJSON(PetExport):
    def export(self, dog):
        return json.dumps({
            "name": dog.name,
            "breed": dog.breed
        })


class ExportXML(PetExport):
    def export(self, dog):
        return """<?xml version="1.0" encoding="utf-8"?>
<dog>
    <name>{0}</name>
    <breed>{1}</breed>
</dog>        
""".format(dog.name, dog.breed)


dog = ExDog("Шарик", "Дворняга", exporter=ExportXML())
dog.export()

print(dog.export())