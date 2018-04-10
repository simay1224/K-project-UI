from .klib import bodygame3
from .klib import msgbox
import wx, pdb
# __main__ = "Kinect v2 Body Analysis"
def main():
    info = None
    app = wx.App()
    while not (hasattr(info, 'name') and hasattr(info, 'age') and hasattr(info, 'gender')):
        info = msgbox.Msgbox(None, title="Welcome")
        app.MainLoop()
    game = bodygame3.BodyGameRuntime(info)
    game.run()
    return game