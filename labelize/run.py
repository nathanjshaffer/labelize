#!/usr/bin/env python3
"""_summary_."""

import os
import configparser
import sys
from typing import Union
import FreeSimpleGUI as sg
from PIL import Image
import importlib.resources as resources
from .resistors.resistors import ResistorPrinter
from .capacitors.capacitors import CapacitorPrinter
from .manual.manual import ManualPrinter
from .util.util import LabelPrinter, ureg, paths, printerBase
from pint import errors

sg.theme('SystemDefault1')

configFile = configparser.ConfigParser()
confPath = os.path.expanduser("~") + "/.labelize.conf"

labelPrinter = LabelPrinter()


def k(k: str) -> tuple:
  """_summary_.

  Args:
      k (str): _description_

  Returns:
      tuple: _description_
  """
  return ('labelize', k)


def saveConfig():
  """_summary_."""
  for printer in printerBase.modules['confItems']:
    printer.saveConfig(configFile)

  with open(confPath, 'w') as file:
    configFile.write(file)


def loadConfig():
  """_summary_."""
  configFile.read(confPath)

  for printer in printerBase.modules['confItems']:
    printer.loadConfig(configFile)


def makeLayout() -> list:
  """_summary_.

  Returns:
      list: _description_
  """
  tabs = []
  for tab in printerBase.modules['tabs']:
    tabs.append(sg.Tab(tab.__class__.__name__, tab.makeLayout(), key=tab.k("TAB")))

  # Create TabGroup
  tabGroup = sg.TabGroup([tabs], key=k('-TABGROUP-'))

  layout = [
    [
      sg.Frame(
        'Settings', [
          [
            sg.Column(
              [
                [
                  sg.Text("Columns:"),
                  sg.Spin(
                    list(range(1, 10)), initial_value=labelPrinter.slotCount, key=k('SLOT_COUNT'), enable_events=True
                  )
                ]
              ]
            ),
            sg.Column(
              [
                [
                  sg.Text("Font Size:"),
                  sg.Spin(
                    list(range(10, 31)), initial_value=labelPrinter.fontSize, key=k('FONT_SIZE'), enable_events=True
                  )
                ]
              ]
            ),
          ],
          [
            sg.Column(
              [
                [
                  sg.Frame(
                    "Label Length:", [
                      [
                        sg.Radio(
                          'Use Label Length',
                          "LENGTH_RAD",
                          key=k("CHAIN_LENGTH_RAD"),
                          default=labelPrinter.useChainLength,
                          enable_events=True
                        ),
                        sg.Input(
                          default_text=f"{labelPrinter.chainLength:#~}",
                          key=k('CHAIN_LENGTH'),
                          size=10,
                          enable_events=True,
                          disabled=not labelPrinter.useChainLength
                        )
                      ],
                      [
                        sg.Radio(
                          'Use Column Length',
                          "LENGTH_RAD",
                          key=k("SLOT_LENGTH_RAD"),
                          default=not labelPrinter.useChainLength,
                          enable_events=True
                        ),
                        sg.Input(
                          default_text=f"{labelPrinter.slotLength:#~}",
                          key=k('SLOT_LENGTH'),
                          size=10,
                          enable_events=True,
                          disabled=labelPrinter.useChainLength
                        )
                      ], [sg.pin(sg.Text("Format Error", text_color='red', visible=False, key=k('FORMAT_ERR_TXT')))]
                    ]
                  ),
                ],
              ]
            )
          ],
          [
            sg.Frame(
              "Cut Marks:", [
                [
                  sg.
                  Radio('None', "CUT", key=k("CUT_NONE"), default=labelPrinter.cut == "CUT_NONE", enable_events=True),
                  sg.
                  Radio('Ends', "CUT", key=k("CUT_ENDS"), default=labelPrinter.cut == "CUT_ENDS", enable_events=True),
                  sg.Radio('All', "CUT", key=k("CUT_ALL"), default=labelPrinter.cut == "CUT_ALL", enable_events=True)
                ]
              ]
            )
          ],
          [
            sg.Frame(
              'Output', [
                [
                  sg.
                  Checkbox('Print to Image', default=labelPrinter.imagePrint, key=k("IMAGE_PRINT"), enable_events=True),
                  sg.Text("Image output File"),
                  sg.
                  Input(default_text=labelPrinter.outputImgFile, key=k('OUTPUT_IMG_FILE'), size=30, enable_events=True),
                ]
              ]
            )
          ],
        ],
        expand_x=True,
        title_location='n'
      )
    ],
    [sg.HorizontalSeparator(color='grey')],
    [tabGroup],
    [sg.pin(sg.Image(key=k('RENDER')))],
    [sg.HorizontalSeparator(color='grey')],
    [sg.Button('Close', key=k('CLOSE'))],
  ]

  return layout


def handleEvent(window: sg.Window, event: tuple, values: dict) -> None:
  """_summary_.

  Args:
      window (sg.Window): _description_
      event (tuple): _description_
      values (dict): _description_
  """
  if event[1] == 'CLOSE':
    saveConfig()
    window.close()
    sys.exit("Goodbye")

  if event[1].endswith('_LENGTH'):
    try:
      if event[1].startswith('CHAIN_'):
        labelPrinter.chainLength = ureg(values[event])
      else:
        labelPrinter.slotLength = ureg(values[event])
      window[k('FORMAT_ERR_TXT')].update(visible=False)
      window[event].update(text_color='black')
    except errors.UndefinedUnitError:
      print(f"can\'t parse {values[event]}")
      window[k('FORMAT_ERR_TXT')].update(visible=True, value=f'Format Error:can\'t parse {values[event]}')
      window[event].update(text_color='red')
    return

  if event[1] == 'FONT_SIZE':
    labelPrinter.fontSize = values[event]
    return

  if event[1] == 'SLOT_COUNT':
    labelPrinter.slotCount = values[event]
    for tab in printerBase.modules['tabs']:
      tab.handleEvent(window, event, values)
    return

  if event[1] == 'IMAGE_PRINT':
    print('IMAGE_PRINT')
    labelPrinter.imagePrint = values[event]
    print(labelPrinter.imagePrint)
    return

  if event[1] == 'OUTPUT_IMG_FILE':
    labelPrinter.outputImgFile = values[event]
    return

  if 'CUT_' in event[1]:
    labelPrinter.cut = event[1]
    return

  if '_LENGTH_RAD' in event[1]:
    labelPrinter.useChainLength = event[1] == 'CHAIN_LENGTH_RAD'

    window[k('CHAIN_LENGTH')].update(disabled=not labelPrinter.useChainLength)
    window[k('SLOT_LENGTH')].update(disabled=labelPrinter.useChainLength)

  if event[1] == 'PRINT':
    processEvent(window, (values[k('-TABGROUP-')][0], event[1]), values)
    return


def processEvent(window: sg.Window, event: Union[tuple, str], values: dict) -> None:
  """_summary_.

  Args:
      window (sg.Window): _description_
      event (Union[tuple, str]): _description_
      values (dict): _description_
  """
  if isinstance(event, tuple):
    if event[0] == 'labelize':
      handleEvent(window, event, values)
      return

    for tab in printerBase.modules['tabs']:
      if event[0] == id(tab):
        tab.handleEvent(window, event, values)
        break

    if event[1] == 'PRINT':
      if labelPrinter.imagePrint:
        try:
          image = Image.open(labelPrinter.outputImgFile)
        except FileNotFoundError:
          print("Error: Image file not found.")
          exit()
        width, height = image.size
        image.close()
        window[k('RENDER')].update(filename=labelPrinter.outputImgFile)
        window.refresh()
      else:
        window[k('RENDER')].update(filename="")
        window.refresh()
      return

  else:
    if event == sg.WIN_CLOSED:
      handleEvent(window, ('labelize', 'CLOSE'), values)
    return


def run():
  """_summary_."""
  ResistorPrinter(labelPrinter)
  CapacitorPrinter(labelPrinter)
  ManualPrinter(labelPrinter)

  if not os.path.exists(confPath):
    configFile['labelmaker'] = {}
    saveConfig()

  loadConfig()
  window = sg.Window('Labelize', makeLayout(), finalize=True, icon=f'{paths["img"]}/labelize.png')
  window.bind("<KP_Enter>", key=k('PRINT'))
  window.bind("<Return>", key=k('PRINT'))
  window.bind("<Escape>", k('CLOSE'))

  while True:
    event, values = window.read()
    processEvent(window, event, values)


def package():
  """_summary_."""
  with resources.path('labelize', 'img') as imgPath:
    paths['img'] = str(imgPath)
    run()
