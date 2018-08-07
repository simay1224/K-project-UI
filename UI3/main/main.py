from .klib import panel_msgbox
from .klib import panel_home
from .klib import bodygame3
from .klib import trainingmode
import wx, pdb
# __main__ = "Kinect v2 Body Analysis"
def main():
    info = None
    app = wx.App()
    info = panel_msgbox.Msgbox()
    app.MainLoop()

    main_win = panel_home.Welcome_win(info)
    app.MainLoop()
    return main_win.game
