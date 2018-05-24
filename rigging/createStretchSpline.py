import sys
import pymel.core as pm


class CreateStretchSplineClass():
    win = None

    def __init__(self, *args):
        self.tFBG = None
        self.myCurve = None
        self.mainController = None
        self.globalControlLayout = None
        self.gui()

    def gui(self, *args):

        if CreateStretchSplineClass.win is not None:
            try:
                pm.deleteUI(CreateStretchSplineClass.win)
            except RuntimeError:
                pass

        with pm.window(
            menuBar=True, menuBarVisible=True,
            width=200, title='Create Stretch Spline'
        ) as w:

            CreateStretchSplineClass.win = w
            # start the template block
            with pm.columnLayout(rowSpacing=5, width=500):
                self.tFBG = pm.textFieldButtonGrp(
                    label='Load Spine Curve: ', buttonLabel='Load Curve',
                    buttonCommand=pm.Callback(self.loadSelectionToTextField)
                )
                pm.button(label='Execute', command=pm.Callback(self.execute))
                self.myCheckbox = pm.checkBox(
                    label='Maintain Scale', changeCommand=pm.Callback(self.toggleMainScale)
                )

            with pm.columnLayout(rowSpacing=5, width=500, enable=False) as self.globalControlLayout:
                self.sTFBG = pm.textFieldButtonGrp(
                    label='Load Main Controller: ', buttonLabel='Load Controller',
                    buttonCommand=pm.Callback(self.loadMainController)
                )

    def toggleMainScale(self, *args):
        enabled = pm.columnLayout(self.globalControlLayout, query=True, enable=True)
        pm.columnLayout(self.globalControlLayout, edit=True, enable=not enabled)

    def loadMainController(self, *args):
        try:
            self.mainController = pm.selected()[0]
            pm.textFieldButtonGrp(self.sTFBG, edit=True, tx=self.mainController.name())
        except:
            pm.textFieldButtonGrp(self.sTFBG, edit=True, placeholderText='Select your main Controller!')   

    def loadSelectionToTextField(self, *args):

        try:
            self.myCurve = pm.selected()[0]
            pm.textFieldButtonGrp(self.tFBG, edit=True, tx=self.myCurve.name())
        except:
            pm.textFieldButtonGrp(self.tFBG, edit=True, placeholderText='Select your Spine Curve!')

    def execute(self, *args):

        try:
            pm.select(self.myCurve)
            handSelection = pm.listRelatives(s=True)
            curveShape = pm.ls(handSelection[0])[0]

            # ik Handle selektieren -> daraus eine Liste aller "Bind Joints" erstellen
            ikHandle = pm.listConnections(curveShape, s=True, d=True)
            ikHandle = pm.ls(ikHandle, type='ikHandle')[0]
            jointList = pm.ikHandle(ikHandle, q=True, jl=True)

            curveInfoNode = pm.createNode('curveInfo', n='CurveInfoNode')
            pm.addAttr(longName='normalizedScale', attributeType='float')
            curveShape.worldSpace.worldSpace[0] >> curveInfoNode.inputCurve

            multiplyDivide = pm.createNode('multiplyDivide', n='{}normalizedScale'.format(self.myCurve.name()))
            multiplyDivide.setAttr('operation', 2)

            # Wenn Maintain Scale angehakt ist, sollten hier die entsprechenden Operationen stattfinden

            if pm.checkBox(self.myCheckbox, query=True, value=True)==True:

                maintainScaleMD = pm.createNode('multiplyDivide', n='maintainScaleMD')
                maintainScaleMD.setAttr('operation', 2)
                self.mainController.scale.scaleY >> maintainScaleMD.input2.input2X
                curveInfoNode.arcLength >> maintainScaleMD.input1.input1X
                maintainScaleMD.output.outputX >> multiplyDivide.input1.input1X

            else:
                curveInfoNode.arcLength >> multiplyDivide.input1.input1X


            multiplyDivide.setAttr('input2.input2X', multiplyDivide.getAttr('input1.input1X'))
            multiplyDivide.outputX >> curveInfoNode.normalizedScale

            expString = '$scale = {}.normalizedScale;\n'.format(curveInfoNode.name())
            expString += '$sqrt = 1/sqrt($scale);\n'

            # Es gilt herauszufinden, mit welcher Achse die Bind Joints auf ihr Child zeigen.
            # Dazu ermittelt man, ob tx, ty oder tz des zweiten Joints am groessten ist.
            # In axisActionList wird eingetragen, fuer welchen Translate Wert nachher
            # die Variable sqrt oder scale verrechnet wird.
            actionList = ["$sqrt", "$scale"]
            axisActionList = [
                actionList[abs(jointList[1].getAttr(axis)) > 0.00001] for axis in ['tx', 'ty', 'tz']
            ]
            scaleAxis = ['sx', 'sy', 'sz']

            for joint in jointList:
                for i in range(3):
                    expString = "{}{}.{}={};\n".format(
                        expString, joint.name(), scaleAxis[i], axisActionList[i]
                    )

            pm.expression(n='{}Exp'.format(self.myCurve.name()), s=expString)

            # Schliessen des Fensters
            if CreateStretchSplineClass.win is not None:
                try:
                    pm.deleteUI(CreateStretchSplineClass.win)
                except RuntimeError:
                    pass

        except IndexError:
            pm.textFieldButtonGrp(self.tFBG, edit=True, placeholderText='Load your Spine Curve first!')

        except:
            print(sys.exc_info()[0])


CreateStretchSplineClass()
