import pygame
from main.klib import msgbox
from main.klib import welcome

import wx, pdb

def main():
    info = None
    app = wx.App()

    info = msgbox.Msgbox(None, title="Welcome")
    # app.MainLoop()
    info._pass()

    main_win = welcome.Welcome_win(info, parent=None, title='Menu')
    app.MainLoop()

    return main_win.game

if __name__ == '__main__':
    result = main()
