import re
import FreeSimpleGUI as sg
import traceback
import os

from ..util.util import ureg, printerBase, key, PrintError, paths

def getNumCode(VAL, code):
    sci = "{:.1e}".format(VAL.to('pF').magnitude)
    # sci = f"{sci:.1e}"
    power = int(sci.split('e')[1])
    print(sci)
    SMDCode = '['
    SMDCode += str(sci)[0]
    SMDCode += str(sci)[2]
    SMDCode += str(power - 1 ) + ']'
    return SMDCode


class CapacitorPrinter(printerBase):

    def __init__(self, labelPrinter):
        self.labelPrinter = labelPrinter
        self.capVal = ureg('10pF')
        self.capType = 'TYPE_ELYTIC'
        self.useVolt = False
        self.volt = 10

    def k(self, k):
        return key(self, k)

    def saveConfig(self, configFile):
        super().saveConfig(configFile, self)

    def loadConfig(self, configFile):
        super().loadConfig(configFile, self)

    def getComponentLabel(self, code: int, baseVal, power, name, cut):
        try:
            val = ureg(baseVal) * (10**power)
            print(type(val.magnitude).__name__)
            numberCode = ""
            if code > 0:
                numberCode = ' ' + getNumCode(val, code)

            val = f"{val:.1f~#D}".replace('.0', "").replace(" ", "")
            val = val + numberCode

            return self.labelPrinter.getPad([name, val], cut)
        except:
            traceback.print_exc()
            return ""

    def getChainLabel(self, code: int, name, baseVal, count):
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
                label += self.getComponentLabel(code, baseVal[index], 0, name,
                                                cut)
            else:
                label += self.getComponentLabel(code, baseVal, index, name,
                                                cut)
            index += 1
        return label

    def printResistorLabel(self, code: int, name, baseVal, count):
        self.labelPrinter.printLabel(
            self.getChainLabel(code, name, baseVal, count))


    def print(self, values):
        name = "Cap Elec"
        code = 0
        if values[self.k('TYPE_SMD')]:
            name = "Cap SMD"
            code = 3
        if values[self.k('TYPE_TANT')]:
            name = "Cap Tant"
            code = 0
        if values[self.k('TYPE_CERAM')]:
            name = "Cap Ceram"
            code = 3
        if values[self.k('VOLT_CHK')]:
            name = name + " " + values[self.k('VOLT')] + 'V'

        if values[self.k('CUSTOM_CHK')]:
            customVals = []
            i = 0
            while i < self.labelPrinter.chainCount:
                customVals.append(values[self.k(f"VAL{i}")])
                i += 1
            self.printResistorLabel(code, name, customVals,
                                    self.labelPrinter.chainCount)
        else:
            self.printResistorLabel(code, name, values[self.k('VAL_BASE')],
                                    self.labelPrinter.chainCount)

    def makeLayout(self):
        customRow = []
        i = 0
        while i < 10:
            customRow.append(
                sg.Input(key=self.k(f"VAL{i}"),
                         size=5,
                         visible=i < self.labelPrinter.chainCount,
                         enable_events=True))
            i += 1

        layout = [
            [
                sg.Checkbox('Custom Layout',
                            key=self.k("CUSTOM_CHK"),
                            enable_events=True)
            ],
            [
                sg.pin(
                    sg.Column(
                        [[
                            sg.Text("Capacitor Base Value"),
                            sg.Input(
                                key=self.k('VAL_BASE'), size=10, default_text=f"{self.capVal:.1f~#D}".replace('.0', ""), enable_events=True),
                            sg.Column(
                                [[
                                    sg.Text("Format Error",
                                            text_color='red',
                                            visible=True,
                                            k=self.k('FORMAT_ERR_TXT')),
                                    # https://fonts.google.com/icons?icon.set=Material+Icons&icon.query=help+outline&icon.size=24&icon.color=%231f1f1f&icon.platform=web
                                    sg.Button(image_filename=
                                              f'{paths["img"]}/help_outline_16dp_1F1F1F.png',
                                              mouseover_colors=('black', 'white'),
                                              key=self.k('ERROR_HELP_BTN'))
                                ]],
                                key=self.k('FORMAT_ERR'),
                                visible=False)
                        ]],
                        key=self.k('CALC_VALS')), )
            ],
            [sg.pin(sg.Column([customRow], visible=False, key=self.k('CUSTOM_VALS')))],
            [
                sg.Radio('Electrolytic', "TYPE", key=self.k("TYPE_ELYTIC"), default=self.capType=="TYPE_ELYTIC", enable_events=True),
                sg.Radio('SMD', "TYPE", key=self.k("TYPE_SMD"), default=self.capType=="TYPE_SMD", enable_events=True),
                sg.Radio('Ceramic', "TYPE", key=self.k("TYPE_CERAM"), default=self.capType=="TYPE_CERAM", enable_events=True),
                sg.Radio('Tantalum', "TYPE", key=self.k("TYPE_TANT"), default=self.capType=="TYPE_TANT", enable_events=True)
            ],
            [
                sg.Checkbox('Voltage', key=self.k("VOLT_CHK"), default=self.useVolt, enable_events=True),
                sg.Input(key=self.k('VOLT'), size=10, default_text=self.volt, enable_events=True)
            ],
            [sg.Button('Print', key=self.k('PRINT'), bind_return_key=True)]
        ]
        return layout

    def handleEvent(self, window, event, values):
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
                value = ureg(values[event])
                if isinstance(value, int) or 'farad' not in str(value.units):
                    window[self.k('FORMAT_ERR')].update(visible=True)
                else:
                    window[self.k('FORMAT_ERR')].update(visible=False)
                    self.capVal=ureg(values[event])
            except:
                traceback.print_exc()
                window[self.k('FORMAT_ERR')].update(visible=True)

            return

        if event[1] == "ERROR_HELP_BTN":
            sg.popup_no_titlebar('Capacitance formatting ex: 22F, 10uF, 100 picofarad',
                                 button_type=0,
                                 button_color=None,
                                 background_color=None,
                                 text_color=None,
                                 icon=None,
                                 line_width=None,
                                 font=None,
                                 grab_anywhere=True,
                                 keep_on_top=True,
                                 location=window.mouse_location(),
                                 modal=True)

            return

        if event[1] == "VOLT":
            self.volt = values[event]
            return

        if event[1] == "VOLT_CHK":
            self.useVolt = values[event]
            return

        if 'TYPE_' in event[1]:
            self.capType = event[1]
            return
