import pygame
from main.klib import panel_msgbox
from main.klib import panel_home

import wx, pdb

def main():
    info = None
    app = wx.App()

    info = panel_msgbox.Msgbox()
    # app.MainLoop()
    info._pass()
    main_win = panel_home.Welcome_win(info)
    app.MainLoop()

if __name__ == '__main__':
    main()
