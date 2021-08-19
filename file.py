class File:
    def __init__(self, path: str, filename: str, version: str):
        self._path = path
        self._filename = filename
        self._version = version
        self._class_name = None

    @property
    def full_file_path(self):
        return self._path + self._filename

    @property
    def filename(self):
        return self._filename

    @property
    def version(self):
        return self._version

    @property
    def class_name(self):
        return self._class_name

    @class_name.setter
    def class_name(self, value):
        self._class_name = value

    def __str__(self):
        return f'{self._path}{self._filename}'
