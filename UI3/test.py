import pygame
from main.klib import msgbox
import wx, pdb
# from .klib import bodygame3
# from .klib import trainingmode
# from .klib import welcome

def main():
    info = None
    app = wx.App()
    while not (hasattr(info, 'name') and hasattr(info, 'age') and hasattr(info, 'gender')):
        info = msgbox.Msgbox(None, title="Welcome")
        app.MainLoop()


if __name__ == '__main__':
    result = main()
