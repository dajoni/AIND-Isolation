"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
from isolation import Board


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    return free_spaces_around_player_minus_length(game, player)


def simple_score(game, player):
    return random.random()


def free_spaces_around_player(game, player):
    if game.is_loser(player):
        return 10000.0

    if game.is_winner(player):
        return 10000.0
    (x, y) = game.get_player_location(player)
    # print ("coordinates: {},{}".format(x,y))
    # topleft, bottomright
    corners = [(max(0, min(6, x + x1)), max(0, min(6, y + y1))) for (x1, y1) in [(-2, -2), (2, 2)]]
    # print("Corners: {}".format(corners))
    area_to_check = [(row, col) for row in range(corners[0][0], corners[1][0] + 1)
                     for col in range(corners[0][1], corners[1][1] + 1)]
    # print("area_to_check: {}".format(area_to_check))
    val = float(len([(row, col) for (row, col) in area_to_check if game.__board_state__[row][col] == Board.BLANK]))
    # print(val)
    return val


def free_spaces_around_player_improved(game, player):
    score_p1 = free_spaces_around_player(game, player)
    p2 = game.get_opponent(player)
    score_p2 = free_spaces_around_player(game, p2)
    return score_p1 - score_p2


def free_spaces_around_player_minus_length(game, player):
    score_p1 = free_spaces_around_player(game, player)
    # print("p1 score: {}".format(score_p1))
    p2 = game.get_opponent(player)
    # print("p1: {}, p2: {}".format(player, p2))
    score_p2 = len(game.get_legal_moves(p2))
    # print("score p2: {}".format(score_p2))
    if not score_p2:
        score_p2 = 1
    return score_p1 / score_p2


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        if method == 'minimax':
            self.search_method = self.minimax
        elif method == 'alphabeta':
            self.search_method = self.alphabeta
            # print("CustomPlayer[iterative: {}, method: {}, timeout: {}, search_depth: {}, score_fn: {}]".format(
            #     iterative, method, timeout, search_depth, score_fn
            # ))

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves
        if not legal_moves or not game.get_legal_moves():
            return -1, -1

        move = -1, -1
        i = 1

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.iterative:
                while True:
                    score, move = self.search_method(game, i)
                    i += 1
            else:
                score, move = self.search_method(game, self.search_depth)

        except Timeout:
            # print("Got depth {}".format(i))
            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search iteration
        return move

    indent = ""

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        moves = game.get_legal_moves()
        if not moves:
            return game.utility(self), (-1, -1)

        if maximizing_player:
            if depth <= 1:
                scores = [(self.score(game.forecast_move(move), self), move) for move in moves]
                # print("{}Scoring move {}".format(self.indent, move))
                # print(successor.to_string(indent=self.indent))
            else:
                # print("{}Evaluating move {}".format(self.indent, move))
                # print(successor.to_string(indent=self.indent))
                # self.indent += "__"
                scores = [(self.minimax(game.forecast_move(move), depth - 1, not maximizing_player)[0], move)
                          for move in moves]
                # self.indent = self.indent[:-2]
                # print("{}Score {}".format(self.indent, nv))
            best_score = max(scores)
        # print("{}Returning: score: {} move: {}".format(self.indent, v, smove))
        if not maximizing_player:
            if depth <= 1:
                scores = [(self.score(game.forecast_move(move), self), move) for move in moves]
                # print("{}Scoring move {}".format(self.indent, move))
                # print(successor.to_string(indent=self.indent))
            else:
                # print("{}Evaluating move {}".format(self.indent, move))
                # print(successor.to_string(indent=self.indent))
                # self.indent += "__"
                scores = [(self.minimax(game.forecast_move(move), depth - 1, not maximizing_player)[0], move)
                          for move in moves]
                # self.indent = self.indent[:-2]
                # print("{}Score {}".format(self.indent, nv))
            best_score = min(scores)
        # print("{}Returning: score: {} move: {}".format(self.indent, v, smove))
        return best_score

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):

        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # print("{}Possible moves for input board is {}".format(self.indent, game.get_legal_moves()))

        moves = game.get_legal_moves()

        if not moves:
            return game.utility(self), (-1, -1)

        if maximizing_player:
            scores = []
            for move in moves:
                successor = game.forecast_move(move)

                if depth <= 1:
                    score = self.score(successor, self)
                    # print("{}Scoring move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                else:
                    # print("{}Evaluating move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                    # self.indent += "__"
                    (score, _) = self.alphabeta(successor, depth - 1, alpha, beta, not maximizing_player)
                    # self.indent = self.indent[:-2]
                scores.append((score, move))
                # print("{}Score {}".format(self.indent, score))
                if score >= beta:
                    return score, move
                if score > alpha:
                    alpha = score
            # print("{}Returning: score: {} move: {}".format(self.indent, max(scores)[0], max(scores)[1]))
            best_move = max(scores)

        if not maximizing_player:
            scores = []
            for move in moves:
                successor = game.forecast_move(move)
                if depth <= 1:
                    score = self.score(successor, self)
                    # print("{}Scoring move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                else:
                    # print("{}Evaluating move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                    # self.indent += "__"
                    (score, _) = self.alphabeta(successor, depth - 1, alpha, beta, not maximizing_player)
                    # self.indent = self.indent[:-2]
                scores.append((score, move))
                # print("{}Score {}".format(self.indent, score))
                if score <= alpha:
                    return score, move
                if score < beta:
                    beta = score
            best_move = min(scores)
            # print("{}Returning: Score: {} move: {}".format(self.indent, v, smove))

        return best_move
