
class CommonCalc():
    def lcLength(self, len):
       return round(len * 100) / 10

    def checkNormalBox(self, normal):
        nx = abs(self.lcLength(normal.x))
        ny = abs(self.lcLength(normal.y))
        nz = abs(self.lcLength(normal.z))
        if nx == 0 or nx == 10:
            if ny == 0 or ny == 10:
                if nz == 0 or nz == 10:
                    return True
        return False