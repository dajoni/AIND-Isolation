"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
from evaluation_fkt import *


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
        if not legal_moves:
            return -1, -1

        move = legal_moves[0]

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            _, move = self.search_method(game, self.search_depth)

        except Timeout:
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
        # inspirational code:
        # http://aima.cs.berkeley.edu/python/games.html
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # print("{}Possible moves for input board is {}".format(self.indent, game.get_legal_moves()))

        if maximizing_player:
            v = float("-inf")
            smove = -1, -1
            for move in game.get_legal_moves():
                successor = game.forecast_move(move)
                if successor.is_loser(game.active_player):
                    return float("-inf"), move
                elif successor.is_winner(game.active_player):
                    return float("inf"), move

                if depth == 1:
                    nv = self.score(successor, game.active_player)
                    # print("{}Scoring move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                else:
                    # print("{}Evaluating move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                    # self.indent += "__"
                    (nv, _) = self.minimax(successor, depth - 1, False)
                    # self.indent = self.indent[:-2]
                # print("{}Score {}".format(self.indent, nv))
                if nv > v:
                    v = nv
                    smove = move
            # print("{}Returning: score: {} move: {}".format(self.indent, v, smove))
            return v, smove

        if not maximizing_player:
            v = float("inf")
            smove = -1, -1
            for move in game.get_legal_moves():
                successor = game.forecast_move(move)
                if successor.is_loser(game.inactive_player):
                    return float("inf"), move
                elif successor.is_winner(game.inactive_player):
                    return float("-inf"), move

                if depth == 1:
                    nv = self.score(successor, game.inactive_player)
                    # print("{}Scoring move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                else:
                    # print("{}Evaluating move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                    # self.indent += "__"
                    (nv, _) = self.minimax(successor, depth - 1, True)
                    # self.indent = self.indent[:-2]
                # print("{}Score {}".format(self.indent, nv))
                if nv < v:
                    v = nv
                    smove = move
            # print("{}Returning: Score: {} move: {}".format(self.indent, v, smove))
            return v, smove

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
        # inspirational code:
        # http://aima.cs.berkeley.edu/python/games.html

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()
        # print("{}Possible moves for input board is {}".format(self.indent, game.get_legal_moves()))

        if maximizing_player:
            v = float("-inf")
            smove = -1, -1
            for move in game.get_legal_moves():
                successor = game.forecast_move(move)
                if successor.is_loser(game.active_player):
                    return float("-inf"), move
                elif successor.is_winner(game.active_player):
                    return float("inf"), move

                if depth == 1:
                    nv = self.score(successor, game.active_player)
                    # print("{}Scoring move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                else:
                    # print("{}Evaluating move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                    # self.indent += "__"
                    (nv, _) = self.alphabeta(successor, depth - 1, alpha, beta, False)
                    # self.indent = self.indent[:-2]
                # print("{}Score {}".format(self.indent, nv))
                if nv >= beta:
                    return nv, move
                if nv > v:
                    v = nv
                    smove = move
                alpha = max(alpha, v)
            # print("{}Returning: score: {} move: {}".format(self.indent, v, smove))
            return v, smove

        if not maximizing_player:
            v = float("inf")
            smove = -1, -1
            for move in game.get_legal_moves():
                successor = game.forecast_move(move)
                if successor.is_loser(game.inactive_player):
                    return float("inf"), move
                elif successor.is_winner(game.inactive_player):
                    return float("-inf"), move

                if depth == 1:
                    nv = self.score(successor, game.inactive_player)
                    # print("{}Scoring move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                else:
                    # print("{}Evaluating move {}".format(self.indent, move))
                    # print(successor.to_string(indent=self.indent))
                    # self.indent += "__"
                    (nv, _) = self.alphabeta(successor, depth - 1, alpha, beta, True)
                    # self.indent = self.indent[:-2]
                # print("{}Score {}".format(self.indent, nv))
                if nv <= alpha:
                    return nv, move
                if nv < v:
                    v = nv
                    smove = move
                beta = min(beta, v)
            # print("{}Returning: Score: {} move: {}".format(self.indent, v, smove))
            return v, smove


