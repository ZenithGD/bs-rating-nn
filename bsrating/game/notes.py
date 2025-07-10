class ColorNote:

    def __init__(self, time : float, x, y, color, cut_dir, angle_offset):

        self.time = time
        self.x = x
        self.y = y
        self.color = color
        self.cut_dir = cut_dir
        self.angle_offset = angle_offset

class BombNote:

    def __init__(self, time : float, x, y):

        self.time = time
        self.x = x
        self.y = y

class Obstacle:

    def __init__(self, time : float, x, y, duration, width, height):

        self.time = time
        self.x = x
        self.y = y
        self.duration = duration
        self.width = width
        self.height = height
