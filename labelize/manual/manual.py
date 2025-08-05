"""_summary_."""
from ..util.util import printerBase, PrintError, LabelPrinter
import FreeSimpleGUI as sg

COL_MAX = 10
ROW_MAX = 5


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
    self.rows: int = 3
    super().__init__(labelPrinter)

  def print(self, values: dict) -> None:
    """_summary_.

    Args:
        values (dict): _description_
    """
    cols = []
    col = 0
    while col < self.labelPrinter.slotCount:
      row = 0
      rows = []
      row_max = self.rows
      if self.useHead:
        if not self.header == '':
          rows.append(self.header)
        row_max -= 1
      while row < row_max:
        if not values[self.k(f"VAL{col}.{row}")] == '':
            rows.append(values[self.k(f"VAL{col}.{row}")])
        row += 1
      cols.append(rows)
      col += 1

    self.labelPrinter.printLabel(cols)

  def makeLayout(self) -> list:
    """_summary_.

    Returns:
        list: _description_
    """
    customRow = []
    i = 0
    while i < 10:
      row = 0
      custom_layout = []
      while row < ROW_MAX:
        vis = (row < self.rows - 1 or not self.useHead) and row < self.rows
        custom_layout.append([sg.Input(key=self.k(f'VAL{i}.{row}'), size=COL_MAX, enable_events=True, visible=vis)])
        row += 1

      customRow.append(
        sg.pin(
          sg.Frame(
            f'{i+1}', [[sg.pin(sg.Column(custom_layout))]],
            key=self.k(f'COL{i}'),
            visible=i < self.labelPrinter.slotCount
          )
        )
      )
      i += 1
    layout = [
      [
        sg.Text("Rows:"),
        sg.Spin(list(range(1, ROW_MAX + 1)), key=self.k('ROWS'), size=10, initial_value=self.rows, enable_events=True),
        sg.Checkbox('Header', key=self.k("HEAD_CHK"), default=self.useHead, enable_events=True),
        sg.Input(key=self.k('VALHEAD'), size=10, default_text=self.header, enable_events=True)
      ], [sg.pin(sg.Column([customRow], key=self.k('CUSTOM_VALS')))],
      [sg.Button('Print', key=self.k('PRINT'), bind_return_key=True)]
    ]

    return layout

  def updateInputFields(self, window: sg.Window) -> None:
    """_summary_.

    Args:
        window (sg.Window): _description_
    """
    col = 0
    while col < COL_MAX:
      window[self.k(f'COL{col}')].update(visible=col < self.labelPrinter.slotCount)
      row = 0
      while row < ROW_MAX:
        vis = (row < self.rows - 1 or not self.useHead) and row < self.rows
        window[self.k(f'VAL{col}.{row}')].update(visible=vis)
        row += 1
      col += 1

  def handleEvent(self, window: sg.Window, event: tuple, values: dict) -> None:
    """_summary_.

    Args:
        window (sg.Window): _description_
        event (tuple): _description_
        values (dict): _description_
    """
    if event[1] == "HEAD_CHK":
      self.useHead = values[event]
      self.updateInputFields(window)
      return

    if event[1] == "ROWS":
      self.rows = values[event]
      self.updateInputFields(window)
      return

    if event == ('labelize', 'SLOT_COUNT'):
      self.updateInputFields(window)

    if event[1] == "VALHEAD":
      self.header = values[event]

    if event[1] == "PRINT":
      try:
        self.print(values)
      except PrintError as e:
        print(e)
      return
