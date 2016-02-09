# coding=utf-8

import time


class Printer:
    """Class for printing messages"""

    def __init__(self, debug):
        self.debug = debug

    def debugPrint(self, string, tipo="DEBUG"):
        if tipo not in "DEBUG" or self.debug:
            print("%s: %-5s ->  %s" % (str(time.strftime("%H:%M:%S")),
                                       tipo, string))

    def errorPrint(self, string):
        self.debugPrint(string, "ERROR")

    def infoPrint(self, string):
        self.debugPrint(string, "INFO")
