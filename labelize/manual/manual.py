"""_summary_."""
from ..util.util import printerBase, PrintError, LabelPrinter
import FreeSimpleGUI as sg

input_size = 10


class ManualPrinter(printerBase):
  """_summary_.

  Attributes:
      labelPrinter (_type_): _description_
      useHead (_type_): _description_
      header (_type_): _description_
  """

  def __init__(self, labelPrinter: LabelPrinter):
    """_summary_.

    Args:
        labelPrinter (_type_): _description_
    """
    self.useHead: bool = True
    self.header: str = ""
    super().__init__(labelPrinter)

  def print(self, values: dict) -> None:
    """_summary_.

    Args:
        values (dict): _description_
    """
    cols = []
    col_i = 0
    while col_i < self.labelPrinter.slotCount:
      row_max = 3
      row_i = 0
      rows = []
      if self.useHead:
        rows.append(self.header)
        row_max = 2
      while row_i < row_max:
        if not values[self.k(f"VAL{col_i}.{row_i}")] == "":
            rows.append(values[self.k(f"VAL{col_i}.{row_i}")])
        row_i += 1
      cols.append(rows)
      col_i += 1

    self.labelPrinter.printLabel(cols)

  def makeLayout(self) -> list:
    """_summary_.

    Returns:
        list: _description_
    """
    customRow = []
    i = 0
    while i < 10:
      custom_layout = [
        [sg.Input(key=self.k(f'VAL{i}.0'), size=input_size, enable_events=True)],
        [sg.Input(key=self.k(f'VAL{i}.1'), size=input_size, enable_events=True)],
        [sg.Input(key=self.k(f'VAL{i}.2'), size=input_size, visible=not self.useHead, enable_events=True)]
      ]
      customRow.append(
        sg.pin(
          sg.Frame(
            f'{i}', [[sg.pin(sg.Column(custom_layout))]],
            key=self.k(f'COL{i}'),
            visible=i < self.labelPrinter.slotCount
          )
        )
      )
      i += 1
    layout = [
      [
        sg.Checkbox('Header', key=self.k("HEAD_CHK"), default=self.useHead, enable_events=True),
        sg.Input(key=self.k('VALHEAD'), size=10, default_text=self.header, enable_events=True)
      ], [sg.pin(sg.Column([customRow], key=self.k('CUSTOM_VALS')))],
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
