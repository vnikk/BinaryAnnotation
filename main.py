#!/usr/bin/env python3
import sys, os, io, time
from PIL import Image, ImageTk
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

import _pickle as pickle

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = '~/cmp/test/'

extensions = ('jpg', 'jpeg', 'png')

images = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path))
                              for f in fn if f.split('.')[-1] in extensions]

current = 0
imgDict = {}
# with open('file', 'w') as file:

try:
    files = [f for f in os.listdir('.') if 'annotations' in f]
    files.sort()
    f = open(files[-1], 'rb')
    imgDict = pickle.load(f)
    f.close()
    f = open('annotations'+str(int(time.time())), 'wb')
    print('loaded', imgDict)

except (FileNotFoundError, IndexError):
    f = open('annotations'+str(int(time.time())), 'wb')


def get_image_data(maxsize = (800, 600), first = True):
    """Generate image data using PIL
    """
    print(current)
    img = Image.open( images[current % len(images)])
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format = "PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def getname():
    return os.path.split(images[current % len(images)])[1]

def next(event):
    global current
    symbol = SYMBOL_MAP[event]

    name = getname()
    if name not in imgDict or imgDict[name] == '?' or\
        (symbol != '?' and imgDict[name] != symbol):
        imgDict[name] = symbol

    # f.write(images[current % len(images)] + '\t' + symbol + '\n')
    # TODO find next non-marked
    current += ACTION_MAP[event]


def update_label():
    try:
        # print(images[current % len(images)])
        # print(getname() in imgDict)
        if imgDict[getname()] == '+':
            text, color = 'Mushroom', 'green'
        elif imgDict[getname()] == '-':
            text, color = 'NOT a mushroom', 'red'
        else:
            text, color = 'Unknown', 'grey'
    except:
        print('except')
        text, color = 'Unknown', 'grey'
    return ( (text), {'background_color':color})

text, color = update_label()
layout = [[ sg.Image(data=get_image_data(first=True), key='_IMG_') ],
          [ sg.Text(text, **color, key='_LB_') ],
          [ sg.Button('Yes (y)', key='_yes_', button_color=('white', 'green')),
            sg.Button('No (n)', key='_no_', button_color=('white', 'red')),
            sg.Button('Skip (j)', key='_next_', button_color=('black', 'grey')),
            sg.Button('Back (k)', key='_prev_', button_color=('black', 'grey')),
            sg.Button('Skip 5 (l)', key='_next_5_', button_color=('black', 'grey')),
            sg.Button('5 back (h)', key='_prev_5_', button_color=('black', 'grey'))]]

window = sg.Window('Mushroom annotation', return_keyboard_events = True).Layout(layout)

SYMBOL_MAP = {
        '_yes_':    '+', 'y': '+',
        '_no_':     '-', 'n': '-',
        '_next_':   '?', 'j': '?',
        '_prev_':   '?', 'k': '?',
        '_next_5_': '?', 'l': '?',
        '_prev_5_': '?', 'h': '?'
        }
ACTION_MAP = {
        '_yes_': 1,     'y': 1,
        '_no_': 1,     'n': 1,
        '_next_': 1,    'j': 1,
        '_prev_': -1,   'k': -1,
        '_next_5_': 5,  'l': 5,
        '_prev_5_': -5, 'h': -5
        }

while True:
  event, values = window.Read()
  print(event, values)
  # TODO escape
  if event is None or event == 'Exit' or event == '\x1b':
      break
  else:
      next(event)
      text, color = update_label()
      window.FindElement('_IMG_').Update(data=get_image_data())
      window.FindElement('_LB_').Update(value=text, **color)


print(imgDict)
pickle.dump(imgDict, f)
window.Close()
f.close()
