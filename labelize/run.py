#!/usr/bin/env python3

import os
import configparser
import sys
import traceback
import FreeSimpleGUI as sg
from PIL import Image
import importlib.resources as resources
from .resistors.resistors import ResistorPrinter
from .capacitors.capacitors import CapacitorPrinter
from .manual.manual import ManualPrinter
from .util.util import LabelPrinter, ureg, paths
from pint import errors

sg.theme('SystemDefault1')


labelPrinter = LabelPrinter()
resistorPrinter = ResistorPrinter(labelPrinter)
capacitorPrinter = CapacitorPrinter(labelPrinter)
manualPrinter = ManualPrinter(labelPrinter)

configFile = configparser.ConfigParser()

confPath = os.path.expanduser("~") + "/.labelize.conf"


def k(k):
    return ('labelize', k)


def saveConfig():
    labelPrinter.saveConfig(configFile)
    capacitorPrinter.saveConfig(configFile)

    with open(confPath, 'w') as file:
        configFile.write(file)


def loadConfig():
    configFile.read(confPath)

    labelPrinter.loadConfig(configFile)
    capacitorPrinter.loadConfig(configFile)


def showRow(row, visible=False):
    for element in row:
        element.update(visible=visible)


def removeColumns(row):
    for element in row:
        element.update(visible=False)
        element.Widget.master.pack_forget()

def makeLayout():
    tab1 = sg.Tab('Manual', manualPrinter.makeLayout(), key=manualPrinter.k("TAB"))
    tab2 = sg.Tab('Resistors', resistorPrinter.makeLayout(), key=resistorPrinter.k("TAB"))
    tab3 = sg.Tab('Capacitors', capacitorPrinter.makeLayout(), key=capacitorPrinter.k("TAB"))

    # Create TabGroup
    tabGroup = sg.TabGroup([[tab1, tab2, tab3]], key=k('-TABGROUP-'))

    layout = [[
        sg.Column([[
            sg.Text("Label Length"),
            sg.Input(default_text=f"{labelPrinter.chainLength:#~}",
                     key=k('LABEL_LENGTH'),
                     size=10,
                     enable_events=True),
            sg.pin(
                sg.Text("Format Error",
                        text_color='red',
                        visible=False,
                        key=k('FORMAT_ERR_TXT')))
        ]]),
        sg.Column([[
            sg.Text("Columns"),
            sg.Spin([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    initial_value=labelPrinter.chainCount,
                    key=k('CHAIN_COUNT'),
                    enable_events=True)
        ]]),
        sg.Column([[
            sg.Text("Font Size"),
            sg.Spin(list(range(10, 20)),
                    initial_value=labelPrinter.fontSize,
                    key=k('FONT_SIZE'),
                    enable_events=True)
        ]])
    ],
    [
        sg.Column([[
            sg.Checkbox('Print to Image', default=labelPrinter.imagePrint,
                    key=k("IMAGE_PRINT"),
                    enable_events=True),
            sg.Text("Image output File"),
            sg.Input(default_text=labelPrinter.outputImgFile,
                    key=k('OUTPUT_IMG_FILE'),
                    size=30,
                    enable_events=True),
        ]])
    ],
    [tabGroup],
    [sg.pin(sg.Image(key=k('RENDER')))],
    [sg.HorizontalSeparator(color='grey')], [sg.Button('Close', key=k('CLOSE'))]]

    return layout


def handleEvent(window, event, values):
    print(event)
    if event[1] == 'CLOSE':
        saveConfig()
        window.close()
        sys.exit("Goodbye")

    if event[1] == 'LABEL_LENGTH':
        try:
            labelPrinter.chainLength = ureg(values[event])
            window[k('FORMAT_ERR_TXT')].update(visible=False)
        except errors.UndefinedUnitError:
            # traceback.print_exc()
            print(f"can\'t parse {values[event]}")
            window[k('FORMAT_ERR_TXT')].update(visible=True)
        return

    if event[1] == 'FONT_SIZE':
        labelPrinter.fontSize = values[event]
        print('labelier', labelPrinter.fontSize)
        return

    if event[1] == 'CHAIN_COUNT':
        labelPrinter.chainCount = values[event]
        return

    if event[1] == 'IMAGE_PRINT':
        labelPrinter.imagePrint = values[event]
        return

    if event[1] == 'OUTPUT_IMG_FILE':
        labelPrinter.outputImgFile = values[event]
        return

    if event[1] == 'PRINT':
        processEvent(window, (values[k('-TABGROUP-')][0], event[1]), values)
        return


def processEvent(window, event, values):
    if isinstance(event, tuple):
        if event[0] == 'labelize':
            handleEvent(window, event, values)
            return

        elif event[0] == id(manualPrinter):
            manualPrinter.handleEvent(window, event, values)

        elif event[0] == id(resistorPrinter):
            resistorPrinter.handleEvent(window, event, values)

        elif event[0] == id(capacitorPrinter):
            capacitorPrinter.handleEvent(window, event, values)

        if event[1] == 'PRINT':
            if labelPrinter.imagePrint:
                try:
                    image = Image.open(labelPrinter.outputImgFile)
                except FileNotFoundError:
                    print("Error: Image file not found.")
                    exit()
                print('update')
                width, height = image.size
                image.close()
                window[k('RENDER')].update(filename=labelPrinter.outputImgFile)
                window.refresh()
            else:
                window[k('RENDER')].update(filename="")
                window.refresh()
            return

    elif event == sg.WIN_CLOSED:
        handleEvent(window, ('labelize', 'CLOSE'), values)
    return


def run():
    if not os.path.exists(confPath):
        configFile['labelmaker'] = {}
        saveConfig()

    loadConfig()
    print(os.getcwd())

    window = sg.Window('Labelize', makeLayout(), finalize=True, icon=f'{paths["img"]}/labelize.png')
    window.bind("<KP_Enter>", key=k('PRINT'))
    window.bind("<Return>", key=k('PRINT'))
    window.bind("<Escape>", k('CLOSE'))

    while True:
        event, values = window.read()
        processEvent(window, event, values)

def package():
    with resources.path('labelize', 'img') as imgPath:
        print(imgPath)
        paths['img'] = imgPath
        run()
