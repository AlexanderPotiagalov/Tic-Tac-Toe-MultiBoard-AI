
import copy
import random
import time
import sys
import math
from collections import namedtuple
#import numpy as np

GameState = namedtuple('GameState', 'to_move, move, utility, board, moves')

def random_player(game, state):
    """A random player that chooses a legal move at random."""
    return random.choice(game.actions(state)) if game.actions(state) else None

# MonteCarlo Tree Search support

class MCTS: #Monte Carlo Tree Search implementation
    class Node:
        def __init__(self, state, par=None):
            self.state = copy.deepcopy(state)

            self.parent = par
            self.children = []
            self.visitCount = 0
            self.winScore = 0

        def getChildWithMaxScore(self):
            maxScoreChild = max(self.children, key=lambda x: x.visitCount)
            return maxScoreChild



    def __init__(self, game, state):
        self.root = self.Node(state)
        self.state = state
        self.game = game
        self.exploreFactor = math.sqrt(2)

    def isTerminalState(self, utility, moves):
        return utility != 0 or len(moves) == 0
    def monteCarloPlayer(self, timelimit = 4):
        """Entry point for Monte Carlo search"""
        start = time.perf_counter()
        end = start + timelimit

        while time.perf_counter() < end:
            promisingNode = self.selectNode(self.root)
            if not self.isTerminalState(promisingNode.state.utility, promisingNode.state.moves):
                self.expandNode(promisingNode)
            node_explore = promisingNode if not promisingNode.children else random.choice(promisingNode.children)
            playout_result = self.simulateRandomPlay(node_explore)
            self.backPropagation(node_explore, playout_result)

        if not self.root.children:
            return random.choice(self.game.actions(self.state)) if self.game.actions(self.state) else None

        winnerNode = self.root.getChildWithMaxScore()
        return winnerNode.state.move

    """selection stage function. walks down the tree using findBestNodeWithUCT()"""
    def selectNode(self, nd):
        node = nd
        while node.children:
            node = self.findBestNodeWithUCT(node)
        return node

    def findBestNodeWithUCT(self, nd):
        """finds the child node with the highest UCT. Parse nd's children and use uctValue() to collect uct's for the
        children....."""
        childUCT = [(child, self.uctValue(nd.visitCount, child.winScore, child.visitCount)) for child in nd.children]
        return max(childUCT, key=lambda item: item[1])[0]


    def uctValue(self, parentVisit, nodeScore, nodeVisit):
        """compute Upper Confidence Value for a node"""
        if nodeVisit == 0:
            return float('inf') 
        winRate = nodeScore / nodeVisit 
        exploration = self.exploreFactor * math.sqrt(math.log(parentVisit) / nodeVisit)
        return winRate + exploration

    def expandNode(self, nd):
        """generate the child nodes and append them to nd's children"""
        for action in self.game.actions(nd.state):
            next_state = self.game.result(nd.state, action)
            next_state = next_state._replace(to_move=('X' if nd.state.to_move == 'O' else 'O')) 
            childNode = self.Node(next_state, nd)
            nd.children.append(childNode)


    def simulateRandomPlay(self, nd):
        winStatus = self.game.compute_utility(nd.state.board, nd.state.move, nd.state.board[nd.state.move])
        if winStatus == self.game.k: 
            assert(nd.state.board[nd.state.move] == 'X')
            if nd.parent is not None:
                nd.parent.winScore = -sys.maxsize
            return ('X' if winStatus > 0 else 'O')

        """now roll out a random play down to a terminating state. """

        tempState = copy.deepcopy(nd.state) 
        while not self.isTerminalState(tempState.utility, tempState.moves):
            action = random.choice(tempState.moves)
            tempState = self.game.result(tempState, action)
        
        final_result = self.game.compute_utility(tempState.board, tempState.move, tempState.to_move)
        return ('X' if final_result > 0 else 'O' if final_result < 0 else 'N') 


    def backPropagation(self, nd, winningPlayer):
        """propagate upword to update score and visit count from
        the current leaf node to the root node."""
        tempNode = nd
        while tempNode is not None:
            tempNode.visitCount += 1
            if (winningPlayer == 'X' and tempNode.state.to_move == 'O') or \
            (winningPlayer == 'O' and tempNode.state.to_move == 'X'):
                tempNode.winScore += 1 
            elif winningPlayer == 'N': 
                tempNode.winScore += 0.5 
            tempNode = tempNode.parent


