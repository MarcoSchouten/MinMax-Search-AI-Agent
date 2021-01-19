import time

class Configuration:
    def __init__(self, string):
        self.string = string

    def getCG(self):
        return self.string


class Model:
    def __init__(self, initial_data):
        self.initial_data = initial_data
        self.best_move = -2
        self.transposition_table = {}

    def addConfiguration(self, config, value):
        if not self.containsConfig(config.getCG()):
            self.transposition_table[config.getCG()] = value

    def containsConfig(self, key):
        if key in self.transposition_table.keys():
            return True
        else:
            return False

    def getValueOf(self, config):
        return self.transposition_table[config]

    def setBestMove(self, move):
        self.best_move = move


class Timer:
    def __init__(self, sec):
        self.sec = sec
        self.done = False

    def start_timer(self):
        start = time.time()
        while time.time() < start + self.sec:
            # print('still have time')
            pass
        # print('oop time ran out')
        self.done = True


