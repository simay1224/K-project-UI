from .klib import home
from .klib import bodygame3
from .klib import trainingmode
from .klib import msgbox
import wx, pdb
# __main__ = "Kinect v2 Body Analysis"
def main():
    info = None
    app = wx.App()
    info = msgbox.Msgbox()
    app.MainLoop()

    main_win = home.Welcome_win(info)
    app.MainLoop()
    return main_win.game
