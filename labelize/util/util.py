"""_summary_."""
import subprocess, os
from typing import Any
from PIL import Image
from pint import UnitRegistry
import FreeSimpleGUI as sg

paths = {'img': f'{os.getcwd()}/labelize/img'}
ureg = UnitRegistry()


class PrintError(Exception):
  """_summary_."""

  def __init__(self, message):
    """_summary_.

    Args:
        message (_type_): _description_
    """
    super().__init__(message)


class printerBase:
  """_summary_."""

  modules: dict = {'confItems': [], 'tabs': []}

  def __init__(self, labelPrinter: Any):
    """_summary_."""
    printerBase.modules['confItems'].append(self)
    if labelPrinter:
      printerBase.modules['tabs'].append(self)
    self.labelPrinter = labelPrinter

  def k(self, k: str) -> tuple:
    """_summary_.

    Args:
        k (object): _description_

    Returns:
        tuple: _description_
    """
    return (id(self), k)

  def saveConfig(self, configFile):
    """_summary_.

    Args:
        configFile (_type_): _description_
    """
    name = self.__class__.__name__
    if name not in configFile:
      configFile[name] = {}
    for key, value in self.__dict__.items():
      if not hasattr(value, '__dict__') and value is not None:
        configFile[name][key] = str(getattr(self, key))

  def loadConfig(self, configFile):
    """_summary_.

    Args:
        configFile (_type_): _description_
    """
    name = self.__class__.__name__
    if name not in configFile:
      configFile[name] = {}
    for key, value in self.__dict__.items():
      if not hasattr(value, '__dict__') and value is not None:
        setattr(self, key, type(value)(configFile[name].get(key, value)))


class LabelPrinter(printerBase):
  """_summary_.

  Attributes:
      fontSize (_type_): _description_
      dpi (_type_): _description_
      chainLength (_type_): _description_
      slotCount (_type_): _description_
      imagePrint (_type_): _description_
      outputImgFile (_type_): _description_
      cutAll (_type_): _description_
  """

  def __init__(self):
    """_summary_."""
    self.fontSize = 16
    self.dpi = 180
    self.chainLength = ureg('6in')
    self.slotCount = 6
    self.imagePrint = False
    self.outputImgFile = os.path.expanduser("~") + '/labelize output'
    self.cutAll = False
    super().__init__(None)

  def getTextWidth(self, label: list) -> int:
    """_summary_.

    Args:
        label (list): _description_

    Returns:
        int: _description_

    Raises:
        PrintError: _description_
    """
    cmd = ["ptouch-print", "--fontsize", str(self.fontSize)] + label + ["--writepng", "/tmp/labelTest"]

    output = subprocess.run(cmd, capture_output=True, text=True)
    if output.returncode > 0:
      if f'Font size {self.fontSize} too large' in output.stdout:
        sg.popup_no_titlebar(output.stdout, button_type=0, keep_on_top=True, modal=True)
        raise PrintError(output.stdout)
    try:
      image = Image.open("/tmp/labelTest")
    except FileNotFoundError:
      print("Error: Image file not found.")
      exit()

    width, height = image.size
    image.close()
    return width

  def computeCut(self, index: int) -> tuple:
    """_summary_.

    Args:
        index (int): _description_

    Returns:
        tuple: _description_
    """
    if index == 0:
      return (True, False)
    elif self.cutAll:
      return (False, True)
    elif index == self.slotCount - 1:
      return (False, True)
    return (False, False)

  def getPad(self, text: list, cut: tuple) -> list:
    """_summary_.

    Args:
        text (list): _description_
        cut (tuple): _description_

    Returns:
        list: _description_
    """
    lcut, rcut = cut

    textW = self.getTextWidth(["--text"] + text)

    pad = ((self.chainLength.to(ureg.inch).magnitude / self.slotCount) * self.dpi - textW) / 2

    lpad = pad - pad % 1
    if lcut:
      lpad -= 1
    rpad = pad + pad % 1
    if rcut:
      rpad -= 1

    lcut = ["--cutmark"] if lcut else []
    rcut = ["--cutmark"] if rcut else []

    return lcut + ["--pad", str(lpad), "--text"] + text + ["--pad", str(rpad)] + rcut

  def printLabel(self, chain: list) -> None:
    """_summary_.

    Args:
        chain (list): _description_
        cutAll (bool): _description_
    """
    cmd = ["ptouch-print", "--fontsize", str(self.fontSize)]
    index = 0
    for label in chain:
      cut = self.computeCut(index)
      cmd += self.getPad(label, cut)
      index += 1

    if self.imagePrint:
      cmd += ["--writepng", self.outputImgFile]
    subprocess.run(cmd, capture_output=True, text=True)
