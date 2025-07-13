import re
import traceback
from pprint import pprint
from ..util.util import ureg, printerBase, key, PrintError
import FreeSimpleGUI as sg


input_size = 10


class ManualPrinter(printerBase):

    def __init__(self, labelPrinter):
        self.labelPrinter = labelPrinter
        self.useHead = True
        self.header = ""

    def k(self, k):
        return key(self, k)


    def saveConfig(self, configFile):
        super().saveConfig(configFile, self)

    def loadConfig(self, configFile):
        super().loadConfig(configFile, self)

    def getChainLabel(self, cols, count):
        index = 0
        label = []
        while index < count:
            cut = self.labelPrinter.computeCut(index, count, False)

            label += self.labelPrinter.getPad(cols[index], cut)

            index += 1
        return label

    def printManualLabel(self, cols, count):
        self.labelPrinter.printLabel(self.getChainLabel(cols, count))

    def print(self, values):
        print('manual', self.labelPrinter.fontSize)
        cols = []
        col_i = 0
        while col_i < self.labelPrinter.chainCount:
            row_max = 3
            row_i = 0
            rows = []
            if self.useHead:
                rows.append(self.header)
                row_max = 2
            while row_i < row_max:
                rows.append(values[self.k(f"VAL{col_i}.{row_i}")])
                row_i += 1
            cols.append(rows)
            col_i += 1
        self.printManualLabel(cols, self.labelPrinter.chainCount)

    def makeLayout(self):
        customRow = []
        i = 0
        while i < 10:
            custom_layout = [[
                sg.Input(key=self.k(f'VAL{i}.0'), size=input_size, enable_events=True)
            ], [
                sg.Input(key=self.k(f'VAL{i}.1'), size=input_size, enable_events=True)
            ],
                             [
                                 sg.Input(key=self.k(f'VAL{i}.2'),
                                          size=input_size,
                                          visible=not self.useHead,
                                          enable_events=True)
                             ]]
            customRow.append(
                sg.pin(sg.Frame(f'{i}', [[sg.pin(sg.Column(custom_layout))]],
                                key=self.k(f'COL{i}'),
                                visible=i < self.labelPrinter.chainCount)))
            i += 1
        layout = [[
            sg.Checkbox('Header',
                        key=self.k("HEAD_CHK"),
                        default=self.useHead,
                        enable_events=True),
            sg.Input(key=self.k('VALHEAD'),
                     size=10,
                     default_text=self.header,
                     enable_events=True)
        ], [sg.pin(sg.Column([customRow], key=self.k('CUSTOM_VALS')))
        ], [sg.Button('Print',key=self.k('PRINT'), bind_return_key=True)
        ]]

        return layout

    def handleEvent(self, window, event, values):
        if event[1] == "HEAD_CHK":
            self.useHead = values[event]
            window[self.k('VALHEAD')].update(disabled=not self.useHead)
            i = 0
            while i < 10:
                window[self.k(f"VAL{i}.2")].update(visible=not self.useHead)
                i += 1
            return

        if event[1] == "VALHEAD":
            self.header = values[event]

        if event[1] == "PRINT":
            try:
                self.print(values)
            except PrintError as e:
                print(e)
            return
