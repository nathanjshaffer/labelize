import subprocess, os
from PIL import Image
from pint import UnitRegistry
import FreeSimpleGUI as sg

paths = {'img': f'{os.getcwd()}/labelize/img'}
ureg = UnitRegistry()

def key(object, k):
    return (id(object), k)


class PrintError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class printerBase:

    def saveConfig(self, configFile, instance):
        name = instance.__class__.__name__
        if name not in configFile:
            configFile[name] = {}
        for key, value in instance.__dict__.items():
            if not hasattr(value, '__dict__'):
                configFile[name][key] = str(getattr(instance, key))

    def loadConfig(self, configFile, instance):
        name = instance.__class__.__name__
        if name not in configFile:
            configFile[name] = {}
        for key, value in instance.__dict__.items():
            if not hasattr(value, '__dict__'):
                setattr(instance, key,
                        type(value)(configFile[name].get(key, value)))


class LabelPrinter(printerBase):

    def __init__(self):
        self.fontSize = 16
        self.dpi = 180
        self.chainLength = ureg('6in')
        self.chainCount = 6
        self.imagePrint = False
        self.outputImgFile = os.path.expanduser("~") + '/labelize output'


    def k(self, k):
        return key(self, k)

    def saveConfig(self, configFile):
        super().saveConfig(configFile, self)

    def loadConfig(self, configFile):
        super().loadConfig(configFile, self)

    def getTextWidth(self, label):
        cmd = ["ptouch-print", "--fontsize",
               str(self.fontSize)] + label + ["--writepng", "/tmp/labelTest"]

        output = subprocess.run(cmd, capture_output=True, text=True)
        if output.returncode > 0:
            if f'Font size {self.fontSize} too large' in output.stdout:
                sg.popup_no_titlebar(output.stdout,
                                     button_type=0,
                                     keep_on_top=True,
                                     modal=True)
                raise PrintError(output.stdout)
        try:
            image = Image.open("/tmp/labelTest")
        except FileNotFoundError:
            print("Error: Image file not found.")
            exit()

        width, height = image.size
        image.close()
        return width

    def computeCut(self, index, count, cut_all):
        if index == 0:
            return True, False
        elif cut_all:
            return False, True
        elif index == count - 1:
            return False, True
        return False, False

    def getPad(self, text: list, cut: tuple):
        lcut, rcut = cut

        textW = self.getTextWidth(["--text"] + text)

        pad = ((self.chainLength.to(ureg.inch).magnitude / self.chainCount) *
               self.dpi - textW) / 2

        lpad = pad - pad % 1
        if lcut:
            lpad -= 1
        rpad = pad + pad % 1
        if rcut:
            rpad -= 1

        lcut = ["--cutmark"] if lcut else []
        rcut = ["--cutmark"] if rcut else []

        return lcut + ["--pad", str(lpad), "--text"
                       ] + text + ["--pad", str(rpad)] + rcut

    def printLabel(self, label):
        cmd = ["ptouch-print", "--fontsize", str(self.fontSize)]
        cmd += label
        if self.imagePrint:
            cmd += ["--writepng", self.outputImgFile]
        subprocess.run(cmd, capture_output=True, text=True)
