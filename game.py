import argparse
import random
import time
from board import Board, Coordinate
from enum import Enum
import abc


class PlayerType(Enum):
    """Player types"""

    USER = 1
    ALPHA_BETA = 2
    GREEDY = 3
    RANDOM = 4


class Agent(abc.ABC):
    """Base class for agents"""

    def __init__(self, color):
        self.color = color

    @abc.abstractmethod
    def move(self, board):
        """Get the next move"""


class User(Agent):
    """User agent"""

    def move(self, board):
        """Get the next move from the user (if valid moves exist)"""
        if not board.get_valid_moves(self.color):
            return None
        print(board)
        print("Your move")
        move = input()
        print("\n")
        return Coordinate.from_string(move)


class AlphaBeta(Agent):
    """Agent that uses alpha-beta pruning to find the best move"""

    def __init__(self, color, depth):
        super().__init__(color)
        self.depth = depth

    def move(self, board):
        """Get the next move using alpha-beta pruning"""
        possible_moves = board.get_valid_moves(self.color)

        # Reorder moves to prioritize valuable moves that will prune the tree faster
        possible_moves = self.__reorder_moves(possible_moves, board, self.color)

        best_move = None
        best_score = -float("inf") if self.color == Board.WHITE else float("inf")
        for move in possible_moves:
            new_board = Board.from_board(board)
            new_board.move(move, self.color)
            score = self.__alphabeta(
                board, self.depth, -float("inf"), float("inf"), False
            )
            # If the score is an end-game score, the alpha-beta pruning went all the way down the tree (in spite of depth limit)
            # In this case, if best_move is None, we should still return the move
            # This particularly happens in the late game when there are few moves left
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
        """Reorder moves to prioritize valuable moves that will prune the tree"""
        return sorted(
            moves,
            key=lambda move: self.__move_priority(move, board, color),
            reverse=True,
        )

    def __move_priority(self, move, board, color):
        """Get the priority of a move"""
        new_board = Board.from_board(board)
        new_board.move(move, color)
        return self.__evaluate(new_board)

    def __alphabeta(self, board, depth, alpha, beta, maximizing_player):
        """Alpha-beta pruning algorithm"""
        if depth == 0 or board.game_over():
            return self.__evaluate(board)

        current_color = self.color if maximizing_player else self.__get_opponent_color()

        if maximizing_player:
            max_eval = -float("inf")

            possible_moves = board.get_valid_moves(current_color)
            # Reorder moves to prioritize valuable moves that will prune the tree faster
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
            # Reorder moves to prioritize valuable moves that will prune the tree
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
        """Evaluate the board"""
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

        # adjust mobility weight based on game stage (number of pieces)
        # If the game is in the end stages, mobility is important to avoid getting blocked
        # In earlier stages, it is more important to have more pieces and mobility encourages
        # less pruning of the search tree (because the next recursion level will have more moves)
        total_pieces = sum(board.get_player_counts())
        if total_pieces < 12:
            mobility_weight = 1
        if total_pieces < 56:
            mobility_weight = 2
        else:
            mobility_weight = 4

        # return weighted sum of piece difference, mobility difference, and positional score
        return (
            10 * piece_difference
            + mobility_weight * mobility_difference
            + positional_score
        )

    def __get_opponent_color(self):
        return Board.WHITE if self.color == Board.BLACK else Board.BLACK


class Greedy(Agent):
    """Agent that makes the move that maximizes the number of pieces it has on the board"""

    def move(self, board):
        """Get the next move that maximizes the number of pieces on the board"""
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
    """Agent that makes a random move"""

    def move(self, board):
        possible_moves = board.get_valid_moves(self.color)
        if not possible_moves:
            return None
        return random.choice(possible_moves)


class Game:
    """Defines a game loop between two players"""

    def __init__(self, player1_type, player2_type):
        self.board = Board()
        self.turn = Board.BLACK  # Black always goes first
        self.player1, self.player2 = self.__init_players(player1_type, player2_type)

    def __init_players(self, player1_type, player2_type):
        """Initialize the players based on the player types"""
        player1 = self.__create_player(player1_type, Board.BLACK)
        player2 = self.__create_player(player2_type, Board.WHITE)

        return player1, player2

    def __create_player(self, player_type, color):
        """Create a player based on the player type and color"""
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
        """Play the game"""
        while not self.board.game_over():
            if delay_seconds > 0:
                time.sleep(delay_seconds)  # Used to observe an AI vs AI game
            if self.turn == Board.BLACK:
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
        """Print the end game message that includes the final board state and the winner"""
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
        """Get the winning player type"""
        if winning_color == Board.WHITE:
            return self.player1.__class__.__name__
        return self.player2.__class__.__name__


def get_args():
    """Get the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "player1_type",
        type=str,
        help="Player 1 type",
        choices=[player_type.name.lower() for player_type in PlayerType],
    )
    parser.add_argument(
        "player2_type",
        type=str,
        help="Player 2 type",
        choices=[player_type.name.lower() for player_type in PlayerType],
    )
    parser.add_argument(
        "-e",
        "--expected_winner",
        type=str,
        choices=["player1", "player2", "tie", "all"],
    )
    parser.add_argument("-n", "--num_trials", type=int, required=False, default=1)
    parser.add_argument("-d", "--delay_seconds", type=float, required=False, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    player1_type = PlayerType[args.player1_type.upper()]
    player2_type = PlayerType[args.player2_type.upper()]
    n = args.num_trials

    # If a user is involved, or a delay is set, only run one trial
    if (
        player1_type == PlayerType.USER
        or player2_type == PlayerType.USER
        or args.delay_seconds > 0
    ):
        n = 1

    # Run the game n times
    p1_win = 0
    p2_win = 0
    tie = 0
    for _ in range(n):
        game = Game(player1_type, player2_type)
        game.play(args.delay_seconds)
        if game.board.get_winner() == Board.BLACK:
            p1_win += 1
        elif game.board.get_winner() == Board.WHITE:
            p2_win += 1
        else:
            tie += 1

    # Print the results (win rate or tie rate, depending on the expected winner as set by the user)
    if args.expected_winner == "tie":
        print(
            f"A tie occurred between {player1_type.name.capitalize()} and {player2_type.name.capitalize()} {tie} out of {args.num_trials} games ({tie / args.num_trials:.4%})"
        )
    elif args.expected_winner == "player1":
        print(
            f"Player 1 ({player1_type.name.capitalize()}) won {p1_win} out of {args.num_trials} games ({p1_win / args.num_trials:.4%})"
        )
    elif args.expected_winner == "player2":
        print(
            f"Player 2 ({player2_type.name.capitalize()}) won {p2_win} out of {args.num_trials} games ({p2_win / args.num_trials:.4%})"
        )
    elif args.expected_winner == "all":
        print(
            f"{player1_type.name.capitalize()}: {p1_win / args.num_trials:.4%} win rate\n{player2_type.name.capitalize()}: {p2_win / args.num_trials:.4%} win rate\nTie: {tie / args.num_trials:.4%}"
        )
