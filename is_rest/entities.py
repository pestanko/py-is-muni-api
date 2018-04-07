class Resource(object):

    def __init__(self, entity: dict):
        self._entity = entity

    @property
    def entity(self):
        return self._entity

    def __getitem__(self, item):
        return self._entity[item]

    def __setitem__(self, key, value):
        self._entity[key] = value

