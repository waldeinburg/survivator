import displayio


class Enemy:

    def __init__(self):
        self.group = displayio.Group()

    def update(self, machine):
        pass

    def is_active(self, machine):
        return True

    def has_hit(self, machine):
        return False
