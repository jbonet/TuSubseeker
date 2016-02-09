# coding=utf-8

import time


class Printer:
    """Basic class for printing messages"""

    def __init__(self, debug):
        self.debug = debug

    def debugPrint(self, string, tipo="DEBUG"):
        tipo = tipo[:4] + '.' if len(tipo) > 5 else tipo
        if tipo not in "DEBUG" or self.debug:
            print("%s | %-5s | ->  %s" % (str(time.strftime("%H:%M:%S")),
                                          tipo, string))

    def errorPrint(self, string):
        self.debugPrint(string, "ERROR")

    def infoPrint(self, string):
        self.debugPrint(string, "INFO")

    def warningPrint(self, string):
        self.debugPrint(string, "WARNING")
