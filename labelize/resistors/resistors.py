from si_prefix import si_format
from ..util.util import ureg, printerBase, key, PrintError

import re

import FreeSimpleGUI as sg

COLOR_CODES = ["Sv", "Gd", "Bk", "Br", "Rd", "Or", "Yo", "Gn", "Bu", "Vi", "Gy", "Wh"]


def getColorCode(val):
    sci = "{:.1e}".format(val)
    power = int(sci.split('e')[1])
    colorCode = COLOR_CODES[int(str(sci)[0]) + 2]
    colorCode += COLOR_CODES[int(str(sci)[2]) + 2]
    colorCode += COLOR_CODES[power + 1]
    return colorCode


def getSMDCode(val):

    sci = "{:.1e}".format(val)
    power = int(sci.split('e')[1])
    SMDCode = '['
    SMDCode += str(sci)[0]
    SMDCode += str(sci)[2]
    SMDCode += str(power - 1) + ']'
    return SMDCode


class ResistorPrinter(printerBase):
    def __init__(self, labelPrinter):
        self.labelPrinter = labelPrinter
        self.baseVal = 10

    def k(self, k):
        return key(self, k)

    def saveConfig(self, configFile):
        super().saveConfig(configFile, self)

    def loadConfig(self, configFile):
        super().loadConfig(configFile, self)

    def getComponentLabel(self, dip: bool, baseVal, power, name, cut):
        val = baseVal * (10**power)
        if dip:
            numberCode = getColorCode(val)
        else:
            numberCode = getSMDCode(val)

        val = si_format(val).replace('.0', "").replace(" ", "")
        val = val + " " + numberCode

        return self.labelPrinter.getPad([name, val], cut)

    def getChainLabel(self, dip: bool, name, baseVal, count):
        index = 0
        label = []
        cut = False, False
        while index < count:
            if index == 0:
                cut = True, False
            elif index == count - 1:
                cut = False, True
            else:
                cut = False, False
            if type(baseVal).__name__ == 'list':
                label += self.getComponentLabel(dip, baseVal[index], 0, name, cut)
            else:
                label += self.getComponentLabel(dip, baseVal, index, name, cut)
            index += 1
        return label

    def printResistorLabel(self, dip: bool, name, baseVal, count):
        self.labelPrinter.printLabel(self.getChainLabel(dip, name, baseVal, count))

    def print(self, values):
        name = "Resistor DIP"
        dip = True
        if values[self.k('SMD')]:
            name = "Resistor SMD"
            dip = False
        if values[self.k('CUSTOM_CHK')]:
            customVals = []
            i = 0
            while i < self.labelPrinter.chainCount:
                customVals.append(values[self.k(f"VAL{i}")])
                i += 1
            self.printResistorLabel(dip, name, customVals, self.labelPrinter.chainCount)
        else:
            self.printResistorLabel(dip, name, self.baseVal, self.labelPrinter.chainCount)

    def makeLayout(self):
        customRow = []
        i = 0
        while i < self.labelPrinter.chainCount:
            customRow.append(sg.Input(key=self.k(f"VAL{i}"), size=5, enable_events=True))
            i += 1

        layout = [
            [sg.Checkbox('Custom Layout', key=self.k("CUSTOM_CHK"), enable_events=True)],
            [
                sg.pin(
                    sg.Column([[sg.Text("Resistor Base Value Ohms:"),
                                sg.Input(key=self.k('VAL_BASE'), default_text=str(self.baseVal), size=10, enable_events=True)]],
                              key=self.k('CALC_VALS')))
            ], [sg.pin(sg.Column([customRow], visible=False, key=self.k('CUSTOM_VALS')))],
            [sg.Radio('DIP', "RADIO1", default=True, key=self.k("DIP")),
             sg.Radio('SMD', "RADIO1", key=self.k("SMD"))], [sg.Button('Print', key=self.k('PRINT'), bind_return_key=True)]
        ]
        return layout

    def handleEvent(self, window, event, values):
        print(event)
        if event[1] == "CUSTOM_CHK":
            custom = values[event]
            window[self.k('CALC_VALS')].update(visible=not custom)
            window[self.k('CUSTOM_VALS')].update(visible=custom)
            return

        if event[1] == "PRINT":
            try:
                self.print(values)
            except PrintError as e:
                print(e)
            except ValueError as e:
                print(e)
            return

        if event[1].startswith('VAL'):
            try:
                float(values[event])
            except ValueError:
                window[event].update(re.sub(r'\D', '', values[event]))
                print("Invalid input!")
                return

        if event[1] == 'VAL_BASE':
            self.baseVal = float(values[event])
