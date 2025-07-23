
class Point:
    def __new__(cls, *args, **kwargs):
        print("случился вызов new")
        return super().__new__(cls)

    def __init__(self,x=0, y=0):
        print("вызов init")
        self.x = x
        self.y = y

