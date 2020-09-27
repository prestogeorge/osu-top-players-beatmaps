class Beatmap(object):
    def __init__(self, count, title, length, url):
        self.count = count
        self.title = title
        self.length = length
        self.url = url

    def __str__(self):
        buffer = str(self.count) + " " * (4 - len(str(self.count)))
        buffer += self.title + " " * (60 - len(self.title))
        buffer += self.length + " " * (6 - len(self.length))
        buffer += self.url
        return buffer
