import nuke
import os
import nukescripts as ns
from subprocess import Popen, PIPE
import threading
# SIMPLE MESSAGE WINDOW


class AlertBox():

    def __init__(self, msg="Warning"):
        self.msg = msg

    def pop(self):
        nuke.message(self.msg)

# SIMPLE LIST ORDER CHOOSER WINDOW


class ChooseBox(ns.PythonPanel):

    def __init__(self, msg="Warning", layerList=[], oldList=[]):
        ns.PythonPanel.__init__(self, "Warning/Attention")
        self.msg = nuke.Text_Knob("Info: ")
        self.msg.setValue(msg)
        self.addKnob(self.msg)
        self.order = {}
        self.layerKnobs = []
        for i, lay in enumerate(layerList):
            self.layerKnobs.append(nuke.Enumeration_Knob(
                'layer_%d' % (i + 1), 'layer %d' % (i + 1), layerList))
            self.layerKnobs[i].setValue(i)
            if oldList != [] and layerList[i] not in oldList:
                self.toggleState(i)
            self.order[i] = i
        for i, knob in enumerate(self.layerKnobs):
            self.addKnob(knob)
            self.addKnob(nuke.PyScript_Knob("layer_%d_toggle" % (i), 'toggle'))

    def toggleState(self, i):
        state = self.layerKnobs[i].enabled()
        strState = ""
        if not state is True:
            strState = "On"
        else:
            strState = "Off"
        print "Toggled %d to %s" % (i, strState)
        self.layerKnobs[i].setEnabled(not state)

    def printOrder(self):
        print self.order

    def getKnobIndexForVal(self, val):
        # self.printOrder()
        for listVal in self.order.values():
            if int(listVal) == val:
                return self.order.values().index(listVal)
                self.order.values()

    def knobChanged(self, knob):
        if knob in self.layerKnobs:
            # self.printOrder()
            indexChanged = self.layerKnobs.index(knob)
            valBeforeChanged = self.order[indexChanged]
            valAfterChanged = int(knob.getValue())
            indexToChange = self.getKnobIndexForVal(valAfterChanged)

            # print indexChanged,valAfterChanged
            # print indexToChange,valBeforeChanged

            self.order[indexToChange] = valBeforeChanged
            self.order[indexChanged] = valAfterChanged

            for i, knob in enumerate(self.layerKnobs):
                knob.setValue(self.order[i])
            # self.printOrder()
        if knob.Class() == "PyScript_Knob":
            name = knob.name()
            indexBtn = int(name.split('_')[1])
            self.toggleState(indexBtn)

    def showModalDialog(self):
        result = ns.PythonPanel.showModalDialog(self)
        return result

    def pop(self):
        return ChooseBox.showModalDialog(self)


class ChooseFromList(ns.PythonPanel):

    def __init__(self, msg="Warning", objList=[]):
        ns.PythonPanel.__init__(self, "ChooseBox")
        self.msg = nuke.Text_Knob("Info: ")
        self.msg.setValue(msg)
        self.addKnob(self.msg)
        self.objList = []
        self.objList = objList
        self.objs = []
        self.objs = nuke.Enumeration_Knob(
            'objs', 'Choose an item :', self.objList)
        self.addKnob(self.objs)
        self.selected = objList[0]

    def knobChanged(self, knob):
        if knob == self.objs:
            self.selected = self.objList[int(knob.getValue())]

    def showModalDialog(self):
        result = ns.PythonPanel.showModalDialog(self)
        return result

    def pop(self):
        return ChooseFromList.showModalDialog(self)


class EnterValue(ns.PythonPanel):

    def __init__(self, msg="Warning", type="", value=""):
        ns.PythonPanel.__init__(self, "ChooseBox")
        self.msg = nuke.Text_Knob("Info: ")
        self.msg.setValue(msg)
        self.addKnob(self.msg)
        self.obj = nuke.String_Knob('obj', 'Enter a %s:' % type)
        self.addKnob(self.obj)
        if value != "":
            self.obj.setValue(value)

    def showModalDialog(self):
        result = ns.PythonPanel.showModalDialog(self)
        return result

    def pop(self):
        return EnterValue.showModalDialog(self)

