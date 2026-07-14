class Position:
    def __init__(self, col, row):
        self.col = col
        self.row = row
    
    def __eq__(self, other):
        return isinstance(other, Position) and self.col == other.col and self.row == other.row
    
    def __hash__(self):
        return hash((self.col, self.row))
    
    def __repr__(self):
        return f"Postion({self.col}, {self.row})"
    
    def as_tuple(self):
        return (self.col, self.row)
    
    def neighbors(self, cols, rows):
        result = []
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                if dc == 0 and dr == 0:
                    continue
                nc, nr = self.col + dc, self.row + dr
                if 0 <= nc < cols and 0 <= nr < rows:
                    result.append(Position(nc, nr))
        return result