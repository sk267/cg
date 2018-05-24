import pymel.core as pm
from cg.system.renamer import hash_to_number


class HashToNumberClass():
    win = None

    def __init__(self):
        self.hashToNumberGui()

    def hashToNumberCall(self):
        name = hash_to_number(pm.textField(self.nameField, q=True, text=True))
        hand_selection = pm.selected()
        for i in hand_selection:
            i.rename(next(name))

    def hashToNumberGui(self, *args):

        if HashToNumberClass.win is not None:
            try:
                pm.deleteUI(HashToNumberClass.win)
            except RuntimeError:
                pass

        with pm.window(menuBar=True, menuBarVisible=True, width=200) as w:

            HashToNumberClass.win = w
            # start the template block
            with pm.columnLayout(rowSpacing=5, width=100):
                pm.text(label='Type in the name pattern:')
                self.nameField = pm.textField(width=150)
                pm.button(label="Enter", command=pm.Callback(self.hashToNumberCall))
