import pygame
from main.klib import msgbox
from main.klib import home

import wx, pdb

def main():
    info = None
    app = wx.App()

    info = msgbox.Msgbox()
    app.MainLoop()
    # info._pass()

    # main_win = home.Welcome_win(info)
    # app.MainLoop()

    # return main_win.game

if __name__ == '__main__':
    result = main()
