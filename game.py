import random
import time
from board import Board, Coordinate
from enum import Enum
import abc


class PlayerType(Enum):
    USER = 1
    ALPHA_BETA = 2
    GREEDY = 3
    RANDOM = 4
    MCTS = 5


class Agent(abc.ABC):
    def __init__(self, color):
        self.color = color

    @abc.abstractmethod
    def move(self, board):
        pass


class User(Agent):
    def move(self, board):
        if not board.get_valid_moves(self.color):
            return None
        print(board)
        print("Your move")
        move = input()
        print("\n")
        return Coordinate.from_string(move)


class AlphaBeta(Agent):
    def __init__(self, color, depth):
        super().__init__(color)
        self.depth = depth

    def move(self, board):
        # get the best move using alpha-beta pruning
        possible_moves = board.get_valid_moves(self.color)
        possible_moves = self.__reorder_moves(possible_moves, board, self.color)
        best_move = None
        best_score = -float("inf") if self.color == Board.WHITE else float("inf")
        for move in possible_moves:
            new_board = Board.from_board(board)
            new_board.move(move, self.color)
            score = self.__alphabeta(
                board, self.depth, -float("inf"), float("inf"), False
            )
            if (
                (score > best_score and self.color == Board.WHITE)
                or (score < best_score and self.color == Board.BLACK)
                or (
                    score >= best_score
                    and self.color == Board.WHITE
                    and best_move is None
                )
                or (
                    score <= best_score
                    and self.color == Board.BLACK
                    and best_move is None
                )
            ):
                best_score = score
                best_move = move
        return best_move

    def __reorder_moves(self, moves, board, color):
        return sorted(
            moves,
            key=lambda move: self.__move_priority(move, board, color),
            reverse=True,
        )

    def __move_priority(self, move, board, color):
        new_board = Board.from_board(board)
        new_board.move(move, color)
        return self.__evaluate(new_board)

    def __alphabeta(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.game_over():
            return self.__evaluate(board)

        current_color = self.color if maximizing_player else self.__get_opponent_color()

        if maximizing_player:
            max_eval = -float("inf")
            possible_moves = board.get_valid_moves(current_color)
            possible_moves = self.__reorder_moves(possible_moves, board, current_color)
            for move in possible_moves:
                new_board = Board.from_board(board)
                new_board.move(move, current_color)
                eval = self.__alphabeta(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            possible_moves = board.get_valid_moves(current_color)
            possible_moves = self.__reorder_moves(possible_moves, board, current_color)
            for move in possible_moves:
                new_board = Board.from_board(board)
                new_board.move(move, current_color)
                eval = self.__alphabeta(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def __evaluate(self, board):
        # if game is over, return the score
        if board.game_over():
            if board.get_winner() == self.color:
                return float("inf")
            elif board.get_winner() == self.__get_opponent_color():
                return -float("inf")
            else:
                return 0

        # assign each space to a positional value
        positional_weights = [
            [100, -20, 10, 5, 5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10, 5, 5, 10, -20, 100],
        ]

        # compute piece difference
        piece_difference = sum(
            (1 if board[Coordinate(x, y)] == self.color else -1)
            for x in range(8)
            for y in range(8)
            if board[Coordinate(x, y)] is not None
        )

        # compute mobility difference
        my_moves = len(board.get_valid_moves(self.color))
        opponent_moves = len(board.get_valid_moves(self.__get_opponent_color()))
        mobility_difference = my_moves - opponent_moves

        # compute positional score
        positional_score = sum(
            positional_weights[x][y]
            * (1 if board[Coordinate(x, y)] == self.color else -1)
            for x in range(8)
            for y in range(8)
            if board[Coordinate(x, y)] is not None
        )

        total_pieces = sum(board.get_player_counts())
        if total_pieces < 12:
            mobility_weight = 1
        if total_pieces < 56:
            mobility_weight = 2
        else:
            mobility_weight = 4

        return (
            10 * piece_difference
            + mobility_weight * mobility_difference
            + positional_score
        )

    def __get_opponent_color(self):
        return Board.WHITE if self.color == Board.BLACK else Board.BLACK


class Greedy(Agent):
    def move(self, board):
        possible_moves = board.get_valid_moves(self.color)

        best_move = None
        best_score = -float("inf")

        for move in possible_moves:
            new_board = Board.from_board(board)
            new_board.move(move, self.color)

            white, black = new_board.get_player_counts()
            score = white if self.color == Board.WHITE else black

            if score > best_score:
                best_score = score
                best_move = move

        return best_move


class Random(Agent):
    def move(self, board):
        possible_moves = board.get_valid_moves(self.color)
        if not possible_moves:
            return None
        return random.choice(possible_moves)


class Game:
    def __init__(self, player1_type, player2_type):
        self.board = Board()
        self.turn = Board.WHITE
        self.player1, self.player2 = self.__init_players(player1_type, player2_type)

    def __init_players(self, player1_type, player2_type):
        player1 = self.__create_player(player1_type, Board.WHITE)
        player2 = self.__create_player(player2_type, Board.BLACK)

        return player1, player2

    def __create_player(self, player_type, color):
        match player_type:
            case PlayerType.USER:
                return User(color)
            case PlayerType.ALPHA_BETA:
                return AlphaBeta(color, depth=3)
            case PlayerType.GREEDY:
                return Greedy(color)
            case PlayerType.RANDOM:
                return Random(color)
            case _:
                raise NotImplementedError

    def play(self, delay_seconds=0):
        while not self.board.game_over():
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            if self.turn == Board.WHITE:
                move = self.player1.move(self.board)
            else:
                move = self.player2.move(self.board)

            # if move is none, the other player may be able to move
            if move is None:
                self.turn = Board.WHITE if self.turn == Board.BLACK else Board.BLACK
                continue

            try:
                self.board.move(move, self.turn)
            except ValueError as e:
                print(e)
                continue

            self.turn = Board.WHITE if self.turn == Board.BLACK else Board.BLACK

    def print_end_game_message(self):
        winning_color = self.board.get_winner()
        winner = (
            "Player 1"
            if winning_color == Board.WHITE
            else "Player 2" if winning_color == Board.BLACK else "Tie"
        )
        print(self.board)
        print("Game over")
        print(
            f"Winner: {winner}{'' if winner == 'Tie' else ' (' + self.__get_winning_player_type(winning_color) + ')'}"
        )

    def get_winning_player_type(self, winning_color):
        if winning_color == Board.WHITE:
            return self.player1.__class__.__name__
        return self.player2.__class__.__name__


if __name__ == "__main__":
    greedy_wins = 0
    for _ in range(100):
        game = Game(PlayerType.ALPHA_BETA, PlayerType.USER)
        game.play()
        game.print_end_game_message()
        if game.get_winning_player_type(game.board.get_winner()) == "Greedy":
            greedy_wins += 1

    # print percentage of games won by greedy player (to 4 significant figures)
    print(f"Greedy player wins: {greedy_wins}%")
