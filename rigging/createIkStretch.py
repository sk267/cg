import pymel.core as pm


class CreateIkStretch():
    win = None

    def __init__(self, *args):
        self.globalControlLayout = None
        self.tFBG = None
        self.mainCtrl = None
        self.myCheckbox = None
        self.gui()

    def gui(self, *args):

        if CreateIkStretch.win is not None:
            try:
                pm.deleteUI(CreateIkStretch.win)
            except RuntimeError:
                pass

        with pm.window(
            menuBar=True, menuBarVisible=True,
            width=200, title='Create Ik Stretch'
        ) as w:
            CreateIkStretch.win = w

            with pm.columnLayout(rowSpacing=5, width=500):
                pm.text('select two joints')
                pm.button(label='Excecute', command=pm.Callback(self.excecute))
                self.myCheckbox = pm.checkBox(
                    enable=True, label='Maintain Scale',
                    changeCommand=pm.Callback(self.toggleCheckbox)
                )
            with pm.columnLayout(rowSpacing=5, width=500, enable=False) as self.globalControlLayout:
                self.sTFBG = pm.textFieldButtonGrp(
                    label='Load Main Controller: ', buttonLabel='Load Controller',
                    buttonCommand=pm.Callback(self.loadMainCtrl)
                )

    def toggleCheckbox(self, *args):
        enabled = pm.columnLayout(self.globalControlLayout, query=True, enable=True)
        pm.columnLayout(self.globalControlLayout, edit=True, enable=not enabled)

    def loadMainCtrl(self, *args):
        try:
            self.mainCtrl = pm.selected()[0]
            pm.textFieldButtonGrp(self.sTFBG, edit=True, tx=self.mainCtrl.name())
        except IndexError:
            pm.textFieldButtonGrp(
                self.sTFBG, edit=True, placeholderText='Select your main Controller!'
            )

    def excecute(self, *args):

        startJoint = None
        endJoint = None
        joints = pm.ls(os=True)

        if joints[0] in joints[1].listRelatives(allDescendents=True, children=True, type='joint'):
            startJoint, endJoint = joints[1], joints[0]
        else:
            startJoint, endJoint = joints[0], joints[1]
        jointList = startJoint.listRelatives(allDescendents=True, children=True, type='joint')
        jointList.reverse()
        jointList = jointList[0:jointList.index(endJoint) + 1]
        jointList.insert(0, startJoint)

        startLoc = pm.spaceLocator(name='startLoc')
        endLoc = pm.spaceLocator(name='endLoc')

        startLoc.setTranslation(startJoint.getTranslation(worldSpace=True), worldSpace=True)
        endLoc.setTranslation(endJoint.getTranslation(worldSpace=True), worldSpace=True)

        pm.select(startJoint.name())
        pm.select(endJoint.name(), add=True)

        ikHandle = pm.ikHandle()[0]

        pm.select(ikHandle.name())
        pm.select(endLoc.name(), add=True)
        pm.parent()

        distanceBetween = pm.createNode('distanceBetween')

        pm.listRelatives(startLoc, shapes=True)[0].worldMatrix[0] >> distanceBetween.inMatrix1
        pm.listRelatives(endLoc, shapes=True)[0].worldMatrix[0] >> distanceBetween.inMatrix2

        if pm.checkBox(self.myCheckbox, query=True, value=True) is True:
            scaleCompensateMultDiv = pm.createNode('multiplyDivide', name='scaleCompensateMultDiv')
            scaleCompensateMultDiv.setAttr('operation', 2)
            distanceBetween.distance >> scaleCompensateMultDiv.input1.input1X
            self.mainCtrl.scale.scaleX >> scaleCompensateMultDiv.input2.input2X
            multiplyDivide = pm.createNode('multiplyDivide')
            multiplyDivide.setAttr('operation', 2)
            scaleCompensateMultDiv.output.outputX >> multiplyDivide.input1.input1X

        else:
            multiplyDivide = pm.createNode('multiplyDivide')
            multiplyDivide.setAttr('operation', 2)
            distanceBetween.distance >> multiplyDivide.input1.input1X

        translateAxis = ['tx', 'ty', 'tz']
        scaleAxis = ['scaleX', 'scaleY', 'scaleZ']

        relevantAxis = None
        relevantScale = None

        for i in range(3):
            if abs(endJoint.getAttr(translateAxis[i])) > 0.00001:
                relevantAxis = translateAxis[i]
                relevantScale = scaleAxis[i]

        # initiale Distanz ausrechnen, durch die dann dividiert werden kann
        initialDistance = 0

        for obj in jointList[1:]:
            initialDistance += abs(obj.getAttr(relevantAxis))

        multiplyDivide.setAttr('input2.input2X', initialDistance)
        clamp = pm.createNode('clamp')
        multiplyDivide.output.outputX >> clamp.input.inputR

        clamp.setAttr('min.minR', 1)
        clamp.setAttr('max.maxR', 5)

        # skalierungswert auf die Joints geben
        for obj in jointList[:-1]:
            clamp.output.outputR >> '{}.{}'.format(obj, relevantScale)


CreateIkStretch()
