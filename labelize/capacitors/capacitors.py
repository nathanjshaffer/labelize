"""_summary_."""
import FreeSimpleGUI as sg
import traceback
# import Pint
from pint import errors, Quantity

from ..util.util import ureg, printerBase, PrintError, paths, LabelPrinter


def getNumCode(VAL: Quantity, code: int) -> str:
  """_summary_.

  Args:
      VAL (quantity): _description_
      code (int): _description_

  Returns:
      str: _description_
  """
  sci = "{:.1e}".format(VAL.to('pF').magnitude)
  power = int(sci.split('e')[1])
  NumCode = '['
  NumCode += str(sci)[0]
  NumCode += str(sci)[2]
  NumCode += str(power - 1) + ']'
  return NumCode


class CapacitorPrinter(printerBase):
  """_summary_.

  Attributes:
      labelPrinter (_type_): _description_
      valBase (_type_): _description_
      capType (_type_): _description_
      useVolt (_type_): _description_
      volt (_type_): _description_
  """

  def __init__(self, labelPrinter: LabelPrinter):
    """_summary_.

    Args:
        labelPrinter (LabelPrinter): _description_
    """
    self.valBase: Quantity = ureg('10pF')
    self.capType: str = 'TYPE_ELYTIC'
    self.useVolt: bool = False
    self.volt: int = 10
    super().__init__(labelPrinter)

  def getSlotLabel(self, code: int, baseVal: Quantity, power: int, name: str) -> list:
    """_summary_.

    Args:
        code (int): _description_
        baseVal (str): _description_
        power (int): _description_
        name (str): _description_

    Returns:
        str: _description_
    """
    val = baseVal * (10**power)
    numberCode = ""
    if code > 0:
      numberCode = ' ' + getNumCode(val, code)

    val = f"{val:.1f~#D}".replace('.0', "").replace(" ", "")
    val = val + numberCode

    return [name, val]

  def print(self, values: dict) -> None:
    """_summary_.

    Args:
        values (dict): _description_
    """
    chain = []
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
    i = 0
    while i < self.labelPrinter.slotCount:
      if values[self.k('CUSTOM_CHK')]:
        chain.append(self.getSlotLabel(code, values[self.k(f"VAL{i}")], 0, name))
      else:
        chain.append(self.getSlotLabel(code, self.valBase, i, name))
      i += 1

    self.labelPrinter.printLabel(chain)

  def makeLayout(self) -> list:
    """_summary_.

    Returns:
        list: _description_
    """
    customRow = []
    i = 0
    while i < 10:
      customRow.append(
        sg.Input(key=self.k(f"VAL{i}"), size=5, visible=i < self.labelPrinter.slotCount, enable_events=True)
      )
      i += 1

    layout = [
      [sg.Checkbox('Custom Layout', key=self.k("CUSTOM_CHK"), enable_events=True)],
      [
        sg.pin(
          sg.Column(
            [
              [
                sg.Text("Capacitor Base Value"),
                sg.Input(
                  key=self.k('VAL_BASE'),
                  size=10,
                  default_text=f"{self.valBase:.1f~#D}".replace('.0', ""),
                  enable_events=True
                ),
                sg.Column(
                  [
                    [
                      sg.Text("Format Error", text_color='red', visible=True, k=self.k('FORMAT_ERR_TXT')),
                      # https://fonts.google.com/icons?icon.set=Material+Icons&icon.query=help+outline&icon.size=24&icon.color=%231f1f1f&icon.platform=web
                      sg.Button(
                        image_filename=f'{paths["img"]}/help_outline_16dp_1F1F1F.png',
                        mouseover_colors=('black', 'white'),
                        key=self.k('ERROR_HELP_BTN')
                      )
                    ]
                  ],
                  key=self.k('FORMAT_ERR'),
                  visible=False
                )
              ]
            ],
            key=self.k('CALC_VALS')
          ),
        )
      ],
      [sg.pin(sg.Column([customRow], visible=False, key=self.k('CUSTOM_VALS')))],
      [
        sg.Radio(
          'Electrolytic', "TYPE", key=self.k("TYPE_ELYTIC"), default=self.capType == "TYPE_ELYTIC", enable_events=True
        ),
        sg.Radio('SMD', "TYPE", key=self.k("TYPE_SMD"), default=self.capType == "TYPE_SMD", enable_events=True),
        sg.Radio('Ceramic', "TYPE", key=self.k("TYPE_CERAM"), default=self.capType == "TYPE_CERAM", enable_events=True),
        sg.Radio('Tantalum', "TYPE", key=self.k("TYPE_TANT"), default=self.capType == "TYPE_TANT", enable_events=True)
      ],
      [
        sg.Checkbox('Voltage', key=self.k("VOLT_CHK"), default=self.useVolt, enable_events=True),
        sg.Input(key=self.k('VOLT'), size=10, default_text=self.volt, enable_events=True)
      ],
      [sg.Button('Print', key=self.k('PRINT'), bind_return_key=True)]
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
      except errors.UndefinedUnitError as e:
        print(e)
      return

    if event[1].startswith('VAL'):
      try:
        value = ureg(values[event])
        if 'farad' not in str(value.units):
          window[self.k('FORMAT_ERR')].update(visible=True)
        else:
          window[self.k('FORMAT_ERR')].update(visible=False)
          self.valBase = value
      except errors.UndefinedUnitError:
        traceback.print_exc()
        window[self.k('FORMAT_ERR')].update(visible=True)

      return

    if event[1] == "ERROR_HELP_BTN":
      sg.popup_no_titlebar(
        'Capacitance formatting ex: 22F, 10uF, 100 picofarad',
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
        modal=True
      )

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
