class Chunk:
    def __init__(self, raw_chunk, x, z):
        self.raw_chunk = raw_chunk
        self.x, self.z = x, z

    def __str__(self):
        return "Chunk %d %d - %d bytes" % (self.x, self.z, len(self.raw_chunk))