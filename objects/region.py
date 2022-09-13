class Region:
    def __init__(self, chunks, region_x, region_z, mtime, timestamps):
        self.chunks = chunks
        self.region_x, self.region_z = region_x, region_z
        self.mtime = mtime
        self.timestamps = timestamps

    def chunk_count(self):
        count = 0
        for i in self.chunks:
            count += 1
        return count