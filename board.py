class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_string(cls, s):
        x = ord(s[0]) - ord("a")
        y = int(s[1]) - 1
        return cls(x, y)

    @classmethod
    def to_string(cls, coord):
        return f"{chr(ord('a') + coord.x)}{coord.y + 1}"

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return Coordinate.to_string(self)

    def __repr__(self):
        return Coordinate.to_string(self)


class Board:
    WHITE = "W"
    BLACK = "B"

    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self["d4"] = self.BLACK
        self["d5"] = self.WHITE
        self["e4"] = self.WHITE
        self["e5"] = self.BLACK

    @classmethod
    def from_board(self, board):
        self.board = [[None] * 8 for _ in range(8)]
        for x in range(8):
            for y in range(8):
                self[x][y] = board[x][y]

    def __str__(self):
        s = "  "
        for x in range(8):
            s += chr(ord("a") + x)
            s += " "
        s += "\n"

        for y in range(8):
            s += str(y + 1)
            for x in range(8):
                if self[x][y] is None:
                    s += "  "
                else:
                    s += " "
                    s += self[x][y]
            s += "\n"
        return s

    def __getitem__(self, key):
        if isinstance(key, Coordinate):
            return self.board[key.x][key.y]
        if isinstance(key, str):
            return self[Coordinate.from_string(key)]
        return self.board[key]

    def __setitem__(self, key, value):
        if isinstance(key, Coordinate):
            self.board[key.x][key.y] = value
        elif isinstance(key, str):
            self[Coordinate.from_string(key)] = value
        else:
            self.board[key] = value

    def move(self, coordinate, color):
        if isinstance(coordinate, str):
            coordinate = Coordinate.from_string(coordinate)
        if not self.__is_valid_move(coordinate, color):
            raise ValueError(f"Invalid move: {Coordinate.to_string(coordinate)}")
        self[coordinate] = color
        self.__reversi(coordinate, color)

    def get_winnner(self):
        if not self.game_over():
            return None

        count_white, count_black = self.__get_player_counts()

        if count_white > count_black:
            return self.WHITE
        elif count_white < count_black:
            return self.BLACK
        return None

    def game_over(self):
        count_white, count_black = self.__get_player_counts()
        if count_white + count_black == 64:
            return True

        if self.get_valid_moves(self.WHITE) or self.get_valid_moves(self.BLACK):
            return False
        return True

    def get_valid_moves(self, color):
        valid_moves = set()
        for x in range(8):
            for y in range(8):
                if self.__is_valid_move(Coordinate(x, y), color):
                    valid_moves.add(Coordinate(x, y))
        return valid_moves

    def __is_valid_move(self, i_coord, color):
        if self[i_coord] is not None or not self.__is_in_bounds(i_coord):
            return False

        directions = [
            Coordinate(1, 0),
            Coordinate(0, 1),
            Coordinate(-1, 0),
            Coordinate(0, -1),
            Coordinate(1, 1),
            Coordinate(-1, 1),
            Coordinate(1, -1),
            Coordinate(-1, -1),
        ]
        for d_coord in directions:
            if self.__is_valid_direction(i_coord, d_coord, color):
                return True
        return False

    def __is_valid_direction(self, i_coord, d_coord, color):
        i_coord += d_coord
        if not self.__is_in_bounds(i_coord) or self[i_coord] != self.__opponent(color):
            return False

        i_coord += d_coord
        while self.__is_in_bounds(i_coord):
            if self[i_coord] == color:
                return True
            if self[i_coord] is None:
                return False
            i_coord.x += d_coord.x
            i_coord.y += d_coord.y
        return False

    def __is_in_bounds(self, coord):
        return 0 <= coord.x < 8 and 0 <= coord.y < 8

    def __opponent(self, color):
        return self.WHITE if color == self.BLACK else self.BLACK

    def __get_player_counts(self):
        count_white = 0
        count_black = 0
        for x in range(8):
            for y in range(8):
                if self[x][y] == self.WHITE:
                    count_white += 1
                elif self[x][y] == self.BLACK:
                    count_black += 1
        return count_white, count_black

    def __reversi(self, i_coord, color):
        directions = [
            Coordinate(1, 0),
            Coordinate(0, 1),
            Coordinate(-1, 0),
            Coordinate(0, -1),
            Coordinate(1, 1),
            Coordinate(-1, 1),
            Coordinate(1, -1),
            Coordinate(-1, -1),
        ]
        for d_coord in directions:
            if self.__is_valid_direction(i_coord, d_coord, color):
                self.__flip_direction(i_coord, d_coord, color)

    def __flip_direction(self, i_coord, d_coord, color):
        i_coord += d_coord
        while self[i_coord] != color:
            self[i_coord] = color
            i_coord += d_coord
