import unittest
from board import Board, Coordinate


class TestBoard(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.board = Board()

    def test_init(self):
        self.assertEqual(self.board["d4"], Board.BLACK)
        self.assertEqual(self.board["d5"], Board.WHITE)
        self.assertEqual(self.board["e4"], Board.WHITE)
        self.assertEqual(self.board["e5"], Board.BLACK)

    def test_get_valid_moves(self):
        print("\n" + str(self.board))
        white_moves = self.board.get_valid_moves(Board.WHITE)
        black_moves = self.board.get_valid_moves(Board.BLACK)
        self.assertEqual(
            white_moves,
            {
                Coordinate.from_string("d3"),
                Coordinate.from_string("e6"),
                Coordinate.from_string("f5"),
                Coordinate.from_string("c4"),
            },
        )
        self.assertEqual(
            black_moves,
            {
                Coordinate.from_string("d6"),
                Coordinate.from_string("e3"),
                Coordinate.from_string("f4"),
                Coordinate.from_string("c5"),
            },
        )

    def test_no_valid_moves(self):
        # Fill the board with the same color
        for x in range(8):
            for y in range(8):
                self.board[x][y] = Board.WHITE
        self.assertEqual(self.board.get_valid_moves(Board.BLACK), set())

    def test_game_over_when_no_valid_moves(self):
        # Empty the board
        for x in range(8):
            for y in range(8):
                self.board[x][y] = None
        self.assertTrue(self.board.game_over())

    def test_game_not_over(self):
        self.assertFalse(self.board.game_over())

    def test_game_over(self):
        # Fill the board with the same color
        for x in range(8):
            for y in range(8):
                self.board[x][y] = Board.WHITE
        self.assertTrue(self.board.game_over())
        self.assertEqual(self.board.get_winnner(), Board.WHITE)

    def test_reverses(self):
        move_set = [
            [(("e3", Board.BLACK), "e4")],  # capture down
            [(("d6", Board.BLACK), "d5")],  # capture up
            [(("f4", Board.BLACK), "e4")],  # capture left
            [(("c5", Board.BLACK), "d5")],  # capture right
            [
                (("e3", Board.BLACK), "e4"),
                (("f3", Board.WHITE), "e4"),
            ],  # capture south-west
            [
                (("d6", Board.BLACK), "d5"),
                (("c6", Board.WHITE), "d5"),
            ],  # capture north-east
        ]

        for game in move_set:
            board = Board()
            for move, capture in game:
                board.move(*move)
                self.assertEqual(board[capture], move[1])


if __name__ == "__main__":
    unittest.main()
