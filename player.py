#!/usr/bin/env python3
import random
import sys
import math
import time

from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR
from my_model import Model, Configuration
TIME_LIMIT = 0.030

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        # print('first smth', file=sys.stderr)
        # print(first_msg, file=sys.stderr)
        # Initialize your minimax model
        model = self.initialize_model(initial_data=first_msg)

        while True:
            msg = self.receiver()

            # Create the root node of the game tree
            node = Node(message=msg, player=0)

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(
                model=model, initial_tree_node=node)

            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def initialize_model(self, initial_data):
        """
        Initialize your minimax model 
        :param initial_data: Game data for initializing minimax model
        :type initial_data: dict
        :return: Minimax model
        :rtype: object

        Sample initial data:
        { 'fish0': {'score': 11, 'type': 3}, 
          'fish1': {'score': 2, 'type': 1}, 
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }

        Please note that the number of fishes and their types is not fixed between test cases.
        """
        # EDIT THIS METHOD TO RETURN A MINIMAX MODEL ###
        model = Model(initial_data)
        return model

    def search_best_next_move(self, model, initial_tree_node):
        """
        Use your minimax model to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node 
        :type initial_tree_node: game_tree.Node 
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###

        # NOTE: Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!

        # TODO: have 75 milliseconds per turn, use time module

        max_depth = 8
        depth = 2


        start = time.time()
        best_depths = {}
        while (depth <= max_depth) and (time.time() < start + TIME_LIMIT):
            # print("calling with DEPTHS {}".format(depth), file=sys.stderr)
            value = self.alpha_beta(model, initial_tree_node, depth, -math.inf, math.inf, 0, start)
            best_depths[depth] = (value, model.best_move)
            depth += 1

        optimal_depth = max(best_depths, key=best_depths.get)  # gets the best move, considering all the inspected depths
        action = best_depths[optimal_depth][1]

        config = self.computeConfig(initial_tree_node.state)
        model.addConfiguration(config, best_depths[optimal_depth][0])

        return ACTION_TO_STR[action]

    def alpha_beta(self, model, node, depth, alpha, beta, player, start):
        # print("PLAYER {}, DEPTHS {}".format(player, depth), file=sys.stderr)
        
        best_move = None
        if len(node.children) == 0:
            node.compute_and_get_children()
        

        
        if (depth == 0) or not len(node.children):
            #print("COMPUTING HEURISTIC", file=sys.stderr)
            v = self.computeHeuristic(node.state, player)

            # print("test7", file=sys.stderr)

        elif ((player == 0) and (depth > 0)):
            #print("INSIDE A", file=sys.stderr)
            new_kiddos = self.reorder_children(node.children, player)
            v = -math.inf
            for child in new_kiddos:
                if (time.time() < start + TIME_LIMIT):
                    #print("test1-newchild", file=sys.stderr)
                    config = self.computeConfig(child.state)
                    if model.containsConfig(config.getCG()):
                        # print("test2", file=sys.stderr)
                        v = model.getValueOf(config.getCG())
                    else:
                        v = max(v, self.alpha_beta(model, child, depth - 1, alpha, beta, 1, start))
                        # print("test3-", file=sys.stderr)

                    if v > alpha:
                        # print("test4", file=sys.stderr)
                        best_move = child.move
                    alpha = max(alpha, v)
                    if beta <= alpha:
                        # print("test5", file=sys.stderr)
                        break
                else:
                    break

        else: #if ((player == 1) and (depth > 0)):
            #("ENTER IN B", file=sys.stderr)
            new_kiddos = self.reorder_children(node.children, player)
            v = math.inf
            for child in new_kiddos:
                if (time.time() < start + TIME_LIMIT):
                    # print("there is a child A", file=sys.stderr)
                    config = self.computeConfig(child.state)
                    if model.containsConfig(config.getCG()):
                        v = model.getValueOf(config.getCG())
                    else:
                        v = min(v, self.alpha_beta(model, child, depth - 1, alpha, beta, 0, start))
                    if v < beta:
                        best_move = child.move
                    beta = min(beta, v)
                    if beta <= alpha:
                        break
                else:
                    break

        # print("test6", file=sys.stderr)
        model.best_move = best_move
        return v

    def computeHeuristic(self, state, player):
        hooks_position = state.get_hook_positions()
        fishes_position = state.get_fish_positions()
        fishes_scores = state.get_fish_scores()

        # algorithm: moves towards its best fish --------------- FOR A
        best_value = -math.inf
        best_id = -1
        negative_value = 0
        for fish_id, fish_position in fishes_position.items():
            dist = self.computeDistance(hooks_position[0], hooks_position[1], fish_position)
            w = self.distanceFactor(dist)
            score = fishes_scores[fish_id]
            value = score * w
            if value < 0:
                negative_value += value

            if best_value < value:
                best_value = value
                best_id = fish_id

        if best_id != -1:
            return best_value + (negative_value/2) + state.player_scores[0] - state.player_scores[1]
        else:
            return state.player_scores[0] -state.player_scores[1]

    def distanceFactor(self, distance):
        # given a distance, return a number from 0.1 and 1
        N = 19
        return ((0.01 - 1) / (math.sqrt((N/2)**2 + N**2))) * (distance) + 1

    def computeDistance(self, player_position, opp_position, fish_position):
        N = 19
        a_X = player_position[0]
        a_Y = player_position[1]

        b_X = opp_position[0]
        #b_Y = opp_position[1]

        f_X = fish_position[0]
        f_Y = fish_position[1]


        if a_X < b_X and b_X < f_X:
            distance_X= N - f_X + a_X     # c'é B in mezzo , devo fare il giro del mondo
        else:
            distance_X = f_X - a_X        # non c'é B in mezzo

        distance_Y = f_Y - a_Y

        return math.sqrt(distance_X ** 2 + distance_Y ** 2)

    def reorder_children(self, children, player):
        kids = {}
        evals = []
        # compute the shallow evaluation of each child of a node
        for child in children:
            eval = self.computeHeuristic(child.state, player)
            evals.append(eval)
            if eval not in kids:
                kids[eval] = [child]
            else:
                kids[eval].append(child)

        # sort the kids based on their evaluation
        if player == 0:
            evals = sorted(list(set(evals)), reverse=True)
        else:
            evals = sorted(list(set(evals)), reverse=False)

        # create the list with reordered children
        new_kiddos = []
        for eval in evals:
            new_kiddos.extend(kids[eval])
        return new_kiddos


    def computeConfig(self, state):
        fp = str(state.fish_positions)
        hp = str(state.hook_positions[0]) + str(state.hook_positions[1])
        sc = str(state.player_scores[0]) + str(state.player_scores[1])
        s = fp + hp + sc
        config = Configuration(s)
        return config
