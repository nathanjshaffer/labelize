"""_summary_."""
from si_prefix import si_format
from ..util.util import printerBase, PrintError, LabelPrinter
import re

import FreeSimpleGUI as sg

COLOR_CODES = ["Sv", "Gd", "Bk", "Br", "Rd", "Or", "Yo", "Gn", "Bu", "Vi", "Gy", "Wh"]


def getColorCode(val):
  """_summary_.

  Args:
      val (_type_): _description_

  Returns:
      _type_: _description_
  """
  sci = "{:.1e}".format(val)
  power = int(sci.split('e')[1])
  colorCode = COLOR_CODES[int(str(sci)[0]) + 2]
  colorCode += COLOR_CODES[int(str(sci)[2]) + 2]
  colorCode += COLOR_CODES[power + 1]
  return colorCode


def getNumCode(val):
  """_summary_.

  Args:
      val (_type_): _description_

  Returns:
      _type_: _description_
  """
  sci = "{:.1e}".format(val)
  power = int(sci.split('e')[1])
  NumCode = '['
  NumCode += str(sci)[0]
  NumCode += str(sci)[2]
  NumCode += str(power - 1) + ']'
  return NumCode


class ResistorPrinter(printerBase):
  """_summary_.

  Attributes:
      valBase (_type_): _description_
  """

  def __init__(self, labelPrinter: LabelPrinter):
    """_summary_.

    Args:
        labelPrinter (LabelPrinter): _description_
    """
    self.valBase: float = 10.0
    super().__init__(labelPrinter)

  def getSlotLabel(self, dip: bool, valBase: float, power: int, name: str) -> list:
    """_summary_.

    Args:
        dip (bool): _description_
        valBase (float): _description_
        power (int): _description_
        name (str): _description_

    Returns:
        list: _description_
    """
    val = valBase * (10**power)
    if dip:
      numberCode = getColorCode(val)
    else:
      numberCode = getNumCode(val)

    val = si_format(val).replace('.0', "").replace(" ", "")
    val = val + " " + numberCode

    return [name, val]

  def print(self, values: dict) -> None:
    """_summary_.

    Args:
        values (dict): _description_
    """
    chain = []
    name = "Resistor DIP"
    dip = True
    if values[self.k('SMD')]:
      name = "Resistor SMD"
      dip = False

    i = 0
    while i < self.labelPrinter.slotCount:
      if values[self.k('CUSTOM_CHK')]:
        chain.append(self.getSlotLabel(dip, values[self.k(f"VAL{i}")], 0, name))
      else:
        chain.append(self.getSlotLabel(dip, self.valBase, i, name))
      i += 1

    self.labelPrinter.printLabel(chain)

  def makeLayout(self) -> list:
    """_summary_.

    Returns:
        list: _description_
    """
    customRow = []
    i = 0
    while i < self.labelPrinter.slotCount:
      customRow.append(sg.Input(key=self.k(f"VAL{i}"), size=5, enable_events=True))
      i += 1

    layout = [
      [sg.Checkbox('Custom Layout', key=self.k("CUSTOM_CHK"), enable_events=True)],
      [
        sg.pin(
          sg.Column(
            [
              [
                sg.Text("Resistor Base Value Ohms:"),
                sg.Input(key=self.k('VAL_BASE'), default_text=str(self.valBase), size=10, enable_events=True)
              ]
            ],
            key=self.k('CALC_VALS')
          )
        )
      ], [sg.pin(sg.Column([customRow], visible=False, key=self.k('CUSTOM_VALS')))],
      [sg.Radio('DIP', "RADIO1", default=True, key=self.k("DIP")),
        sg.Radio('SMD', "RADIO1", key=self.k("SMD"))], [sg.Button('Print', key=self.k('PRINT'), bind_return_key=True)]
    ]
    return layout

  def handleEvent(self, window: sg.Window, event: tuple, values: dict) -> None:
    """_summary_.

    Args:
        window (sg.Window): _description_
        event (tuple): _description_
        values (dict): _description_
    """
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
      self.valBase = float(values[event])
