import pymel.core as pm


class DrawingOverrideClass():

    win = None

    def __init__(self, *args):
        self.displayTypeNumber = 0
        self.levelofDetailNumber = 0
        self.displayTypeList = ['Normal', 'Template', 'Reference']
        self.levelofDetailList = ['Full', 'BoundingBox']
        self.gui()


    def gui(self, *args):
        if DrawingOverrideClass.win is not None:
            try:
                pm.deleteUI(DrawingOverrideClass.win)
            except RuntimeError:
                pass

        with pm.window(menuBar=True, menuBarVisible=True, width=200, title='Drawing Overrides') as w:
            DrawingOverrideClass.win = w
            # start the template block
            with pm.columnLayout(rowSpacing=5, width=300):
                self.displayType = pm.optionMenu(label='Display Type')
                for i in range(3):
                    pm.menuItem(label='{}'.format(self.displayTypeList[i]))
                self.levelOfDetail = pm.optionMenu(label='Level of Detail')
                for i in range(2):
                    pm.menuItem(label='{}'.format(self.levelofDetailList[i]))
                pm.button(label='Execute!', command=pm.Callback(self.execute))



    def execute(self, *args):
        lOD = self.displayTypeList.index(pm.optionMenu(self.displayType, value=True, query=True))
        dT = self.levelofDetailList.index(pm.optionMenu(self.levelOfDetail, value=True, query=True))

        allSelected = pm.ls(g=True)
        dNH = pm.ls(g=True, regex='.*_DO_NOT_HIDE')
        allSelected = [s for s in allSelected if s not in dNH]
        for obj in allSelected:
            pm.setAttr('{}.overrideEnabled'.format(obj.name()), 1)
            pm.setAttr('{}.overrideDisplayType'.format(obj.name()), lOD)
            pm.setAttr('{}.overrideLevelOfDetail'.format(obj.name()), dT)


DrawingOverrideClass()
