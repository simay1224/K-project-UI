from .klib import panel_msgbox
from .klib import panel_home
from .klib import bodygame3
from .klib import trainingmode
import wx, pdb
# __main__ = "Kinect v2 Body Analysis"
def main():
    info = None
    app = wx.App()
    print 'Creating message box...'
    info = panel_msgbox.Msgbox()
    app.MainLoop()
    print 'Creating the welcome window...'
    main_win = panel_home.Welcome_win(info)
    print 'Finish welcome windows'
    app.MainLoop()
    return main_win.game
