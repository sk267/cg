from cg.system.helloPrinter import HelloPrinter as hP

class Test():
    def __init__(self, *args):
        myHelloPrinter = hP()
        myHelloPrinter.german()
        myHelloPrinter.france()
        myHelloPrinter.english()


Test()