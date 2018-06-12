import wx
import cv2
import numpy as np
import pandas as pd
import wx.media
import matplotlib
from matplotlib.figure import Figure
from collections import defaultdict
import wx.lib.mixins.inspection as WIT

import sys, math

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from ..klib import bodygame3
from ..klib import trainingmode
from .historylog import Historylog

# class Info():
#     def __init__(self):
#         self.name   = 'jane doe'
#         self.age    = '19'
#         self.gender = 'female'

class Welcome_win(wx.Frame):
    def __init__(self, info, parent, title):
        self.info = info
        self.game = None

        self.font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.font_field = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.font_title = wx.Font(36, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Lucida Handwriting')

        super(Welcome_win, self).__init__(parent, title=title, size=(410, 500))
        panel = wx.Panel(self)

        # sizers
        topSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.GridBagSizer(5, 5)
        sizer = wx.GridBagSizer(5, 5)

        # title
        text = wx.StaticText(panel, label="LymphCoach")
        text.SetFont(self.font_title)
        topSizer.Add(text, 0, wx.CENTER)


        # Basic information
        text11 = wx.StaticText(panel, label="Name:")
        text11.SetFont(self.font_field)
        titleSizer.Add(text11, pos=(1, 0))

        text1 = wx.StaticText(panel, label=self.info.fname + " " + self.info.lname)
        text1.SetFont(self.font)
        titleSizer.Add(text1, pos=(1, 1))

        text21 = wx.StaticText(panel, label="Gender:")
        text21.SetFont(self.font_field)
        titleSizer.Add(text21, pos=(2, 0))
        text2 = wx.StaticText(panel, label=self.info.gender)
        text2.SetFont(self.font)
        titleSizer.Add(text2, pos=(2, 1))

        text31 = wx.StaticText(panel, label="Age:")
        text31.SetFont(self.font_field)
        titleSizer.Add(text31, pos=(3, 0))
        text3 = wx.StaticText(panel, label=self.info.age)
        text3.SetFont(self.font)
        titleSizer.Add(text3, pos=(3, 1))

        button_size = (300, 50)

        button1 = wx.Button(panel, size=button_size, label="Training")
        button1.SetFont(self.font)
        button1.Bind(wx.EVT_BUTTON, self.open_trainingmode)
        sizer.Add(button1, pos=(1, 1), span=(1, 0))

        button2 = wx.Button(panel, size=button_size, label="Instructions")
        button2.SetFont(self.font)
        button2.Bind(wx.EVT_BUTTON, self.open_instruction)
        sizer.Add(button2, pos=(2, 1), span=(1, 0))

        button3 = wx.Button(panel, size=button_size, label="Live Evaluation")
        button3.SetFont(self.font)
        button3.Bind(wx.EVT_BUTTON, self.open_bodygame)
        sizer.Add(button3, pos=(3, 1), span=(1, 0))

        button3 = wx.Button(panel, size=button_size, label="History Review")
        button3.SetFont(self.font)
        button3.Bind(wx.EVT_BUTTON, self.open_history)
        sizer.Add(button3, pos=(4, 1), span=(1, 0))

        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(sizer, 0, wx.CENTER)
        panel.SetSizer(topSizer)

        # panel.SetSizer(sizer)
        # panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Show(True)

    def open_bodygame(self, event):
        # myobject = event.GetEventObject()
        # myobject.Disable()
        self.game = bodygame3.BodyGameRuntime(self.info)
        self.game.run()
        if self.game.kp._done:
            self.Destroy()

    def open_instruction(self, event):
        instruct = Instrcution_win(None, 'Instruction')

    def open_history(self, event):
        history  = History_view(None, self.info)

    def open_trainingmode(self, event):
        self.train = trainingmode.BodyGameRuntime()
        self.train.run()
        # if self.train.kp._done:
        #     self.Destroy()

    def OnEraseBackground(self, evt):
        """
        Add a picture to the background
        """
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("./data/bkimgs/BUMfk9.jpg")
        dc.DrawBitmap(bmp, 0, 0)


class Instrcution_win(wx.Frame):

    def __init__(self, parent, title):
        self.init_text()
        super(Instrcution_win, self).__init__(parent, title=title, size=(950, 700))

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        # self.text = wx.TextCtrl(panel, size = (900,300), style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.player = MoviePanel(panel, -1)
        self.text = wx.TextCtrl(panel, size=self.player.mc.GetBestSize(), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text.SetFont(self.font)
        # self.text.SetBackgroundColour((255, 255, 255))
        self.text.SetBackgroundColour((179, 236, 255))
        languages = [self.str['exe'][1], self.str['exe'][2], self.str['exe'][3], self.str['exe'][4],\
                     self.str['exe'][5], self.str['exe'][6], self.str['exe'][7]]

        box2 = wx.BoxSizer(wx.VERTICAL)
        box3 = wx.BoxSizer(wx.VERTICAL)
        lst = wx.ListBox(panel, size = (250, self.player.mc.GetBestSize()[1] * 2), choices=languages, style=wx.LB_SINGLE)
        lst.SetBackgroundColour((255, 255, 255))
        button1 = wx.Button(panel, label="Close")
        button1.Bind(wx.EVT_BUTTON, self.close)

        button_print = wx.Button(panel, id=wx.ID_PRINT, label="")
        button_print.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.OnBtnPrint, button_print)

        box2.Add(lst, 0, wx.EXPAND)
        box2.Add(button1, 1, wx.EXPAND)
        box3.Add(self.player, 0, wx.EXPAND)

        text_sizer = wx.GridBagSizer(5, 5)
        text_sizer.Add(button_print, (4, 4))
        text_sizer.Add(self.text, (0, 0), span=(5, 0))  # for .avi .mpg video files

        # box3.Add(self.text, 0, wx.LEFT)
        box3.Add(text_sizer, 0, wx.LEFT)

        box.Add(box2, 0,wx.EXPAND)
        box.Add(box3, 1, wx.EXPAND)
        # box.Add(button_print, 2, wx.RIGHT)
        panel.SetSizer(box)
        panel.Fit()

        self.Centre()
        self.Bind(wx.EVT_LISTBOX, self.onListBox, lst)
        self.Show(True)


    def init_text(self):
        self.str = defaultdict(dict)
        self.str['exe'][1] = 'Exercise 1 : Muscle Tighting Deep Breathing'
        self.str['exe'][2] = 'Exercise 2 : Over The Head Pumping'
        self.str['exe'][3] = 'Exercise 3 : Push Down Pumping'
        self.str['exe'][4] = 'Exercise 4 : Horizontal Pumping'
        self.str['exe'][5] = 'Exercise 5 : Reach to the Sky'
        self.str['exe'][6] = 'Exercise 6 : Shoulder Rolls'
        self.str['exe'][7] = 'Exercise 7 : Clasp and Spread'

        self.str['ins'][1] = '\n  '\
                             '\n1. Put your hands on the belly position.'\
                             '\n2. Wait until the sign shows "start breath in/out."'\
                             '\n3. Do deep breathing 4 times.'\
                             '\n4. Put down your hands.'

        self.str['ins'][2] = '\n  '\
                             '\n1. Raise your harms up and hold there.'\
                             '\n2. Wait until the sign shows "start breath in/out."'\
                             '\n3. Do deep breathing 4 times.' \
                             '\n4. Put down your arms.'

        self.str['ins'][3] = '\n  '\
                             '\n1. Raise your arms up.'\
                             '\n2. Lower your elbows, let shoulder-elbow-hand be a V-shape.'\
                             '\n3. Raise your arms up again.'\
                             '\n4. Repeat this repetition 4 times.'\
                             '\n5. Put down your arms.'

        self.str['ins'][4] = '\n  '\
                             '\n1. Raise your arms up till "T-pose."'\
                             '\n2. Move arms slowly to the chest.'\
                             '\n3. Back to "T-pose".'\
                             '\n4. Repeat this repetition 4 times.'\
                             '\n5. Put down your arms.'

        self.str['ins'][5] = '\n  '\
                             '\n1. Raise your arms up  as high as possible and clasp.'\
                             '\n2. Bend your body to the left.'\
                             '\n3. Bend your body to the right.'\
                             '\n4. Repeat 4 times.'\
                             '\n5. Put down your arms.'

        self.str['ins'][6] = '\n  '\
                             '\n1. Put your hands on the belly position.'\
                             '\n2. Rotate you shoulder.'\
                             '\n3. Repeat 4 times.'\
                             '\n4. Put down your hands.'

        self.str['ins'][7] = '\n  '\
                             '\n1. Raise and clasp your arms till the belly position.'\
                             '\n2. Raise clasped hands toward to your forehead and keep elbows together.'\
                             '\n3. Slide your heands to the back of your head and spread the elbows open wide.'\
                             '\n4. Back to the belly position.'\
                             '\n5. Repeat 4 times.'\
                             '\n6. Put down your arms.'

        self.str['note'][1] = 'Tips :'\
                                '\n1. Tighten your muscle as much as you can.'\
                                '\n2. Breathe as deep as you can.'
        self.str['note'][2] = 'Tips :'\
                                '\n1. When you breathe in, you also need to close your hands.'\
                                '\n2. When you breathe out, you also need to open your hands.'\
                                '\n3. Breathe as deep as you can.'
        self.str['note'][3] = 'Tips :'\
                                '\n1. When you raise up your arms, make sure that your hand, elbow and shoulder are straight.'\
                                '\n2. When bending the elbow, hand-elbow-shoulder should be "V-shape" not "L-shape"'\

        self.str['note'][4] = 'Tips :'\
                                '\n1. When doing "T-pose", make sure that your hand, elbow and shoulder are straight'\
                                '\n2. When closing hands, make sure that your hand, and shoulder are in the same height.'\

        self.str['note'][5] = 'Tips :'\
                                '\n1. When bending the body, make sure that your hand, elbow and shoulder are straight.'\
                                '\n2. Keep your body staight'

        self.str['note'][6] = 'Tips :'\
                                '\n1. Let your shoulders rotation movement as large as possible.'

        self.str['note'][7] = 'Tips :'\
                                '\n1. When raising the arms to the forehead, keeping two elbows as close as possible.'\
                                '\n2. When the hands is in the back of your head, spread the elnows open as wide as possible.'\
                                '\n3. Keep your body staight.'

    def onListBox(self, event):
        self.text.Clear()
        ex = event.GetEventObject().GetSelection()+1
        self.text.AppendText(self.str['exe'][ex]+self.str['ins'][ex]+'\n\n')
        self.text.AppendText(self.str['note'][ex])
        self.player.doLoadFile('./video/ex'+str(ex)+'.mpg')


    def OnBtnPrint(self, event):
        """
        Print the document.
        """

        text = self.text.GetValue()

        #------------

        pd = wx.PrintData()

        pd.SetPrinterName("")
        pd.SetOrientation(wx.PORTRAIT)
        pd.SetPaperId(wx.PAPER_A4)
        pd.SetQuality(wx.PRINT_QUALITY_DRAFT)
        # Black and white printing if False.
        pd.SetColour(True)
        pd.SetNoCopies(1)
        pd.SetCollate(True)

        #------------

        pdd = wx.PrintDialogData()

        pdd.SetPrintData(pd)
        pdd.SetMinPage(1)
        pdd.SetMaxPage(1)
        pdd.SetFromPage(1)
        pdd.SetToPage(1)
        pdd.SetPrintToFile(False)
        # pdd.SetSetupDialog(False)
        # pdd.EnableSelection(True)
        # pdd.EnablePrintToFile(True)
        # pdd.EnablePageNumbers(True)
        # pdd.SetAllPages(True)

        #------------

        dlg = wx.PrintDialog(self, pdd)

        if dlg.ShowModal() == wx.ID_OK:
            dc = dlg.GetPrintDC()

            dc.StartDoc("My document title")
            dc.StartPage()

            # (wx.MM_METRIC) ---> Each logical unit is 1 mm.
            # (wx.MM_POINTS) ---> Each logical unit is a "printer point" i.e.
            dc.SetMapMode(wx.MM_POINTS)

            dc.SetTextForeground("red")
            dc.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD))
            dc.DrawText(text, 50, 100)

            dc.EndPage()
            dc.EndDoc()
            del dc

        else :
            dlg.Destroy()


    def close(self, event):
        self.Destroy()


class MoviePanel(wx.Panel):
    def __init__(self, parent, id):
        #self.log = log
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

        # Create some controls
        self.mc = wx.media.MediaCtrl(self, size=(500,300), style=wx.SIMPLE_BORDER)
        playButton = wx.Button(self, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.onPlay, playButton)

        pauseButton = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.onPause, pauseButton)

        stopButton = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self.onStop, stopButton)
        # self.st_file = wx.StaticText(self, -1, ".mid .mp3 .wav .au .avi .mpg", size=(200,-1))
        self.st_size = wx.StaticText(self, -1, size=(100, -1))
        self.st_len  = wx.StaticText(self, -1, size=(100, -1))
        self.st_pos  = wx.StaticText(self, -1, size=(100, -1))

        # setup the button/label layout using a sizer
        sizer = wx.GridBagSizer(5, 5)
        # sizer.Add(loadButton, (1,1))
        sizer.Add(playButton, (2, 4))
        sizer.Add(pauseButton, (3, 4))
        sizer.Add(stopButton, (4, 4))
        sizer.Add(self.mc, (0, 0), span=(5, 0))  # for .avi .mpg video files
        self.SetSizer(sizer)


    def doLoadFile(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
        else:
            filename = './video/ex'+str(1)+'.mpg'
            self.st_file.SetLabel('%s' % filename)
            self.GetSizer().Layout()
            self.mc.Play()#ITS TO PROBLEM, WHY IT DOESNT PLAY HERE?#

    def onPlay(self, evt):
        self.mc.Play()

    def onPause(self, evt):
        self.mc.Pause()

    def onStop(self, evt):
        self.mc.Stop()



class History_view(wx.Frame):
    def __init__(self, parent, info, title='welcome'):
        super(History_view, self).__init__(parent, title=title, size=(850, 520))
        self.info = info
        self.no_hist_img = cv2.imread('./data/no_hist.jpg')
        self.InitUI()
        self.Show()

    def InitUI(self, path='./output/log.xlsx'):
        self.font = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.path = path
        try:
            log_xl = pd.ExcelFile(path)
        except:
            print('log file do not exist, creating a new one')
            hist = Historylog()
            hist.newlog()
            log_xl = pd.ExcelFile(path)

        self.panel = wx.Panel(self)

        box1 = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.VERTICAL)
        box3 = wx.BoxSizer(wx.HORIZONTAL)

        info_text = 'Name: ' + self.info.name.title() + \
                    '\nGender: ' + self.info.gender.title() + \
                    '\nAge: ' + str(self.info.age)

        info = wx.StaticText(self.panel, wx.ID_ANY, label=info_text)
        info.SetFont(self.font)
        box1.Add(info, 0, wx.EXPAND)

        ex_choices = log_xl.sheet_names
        self.choice = wx.Choice(self.panel, choices=ex_choices)
        self.choice.SetFont(self.font)
        self.choice.Bind(wx.EVT_CHOICE, self.update_choice)
        box1.Add(self.choice, 1, wx.EXPAND)
        box2.Add(box1, 0)

        self.lst = wx.ListBox(self.panel, size=(330, 300), choices=[], style=wx.LB_SINGLE)
        self.lst.SetFont(self.font)
        self.Bind(wx.EVT_LISTBOX, self.update_figure, self.lst)
        box2.Add(self.lst, 1, wx.EXPAND)
        box3.Add(box2, 0, wx.EXPAND)


        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.panel, -1, self.figure)
        box3.Add(self.canvas, 1, wx.EXPAND)

        self.panel.SetSizer(box3)
        self.panel.Fit()

    def update_choice (self, event):
        cur_choice = self.choice.GetSelection()
        self.df = pd.read_excel(self.path, sheetname=cur_choice)
        self.lst.Clear()
        lst_choice = self.df.columns.values.tolist()
        idx_1 = [i for i, elem in enumerate(lst_choice) if 'time' in elem][0] + 1
        idx_2 = [i for i, elem in enumerate(lst_choice) if 'errmsg' in elem][0]
        self.lst.InsertItems(lst_choice[idx_1:idx_2], 0)

    def update_figure(self, event):
        df_name  = self.df[self.df['name'] == self.info.name]
        df_ideal = self.df[self.df['name'] == '$IDEAL VALUE$']
        item = self.lst.GetStringSelection()
        y = np.array(df_name[item])
        x = np.arange(0, len(y), 1)
        x_name = df_name['time'].tolist()
        self.axes.clear()
        try:
            self.axes.plot(x, y, color='#0000FF')
            # self.axes.bar(x, y, color='g')
            if df_ideal[item].dtype == float:
                cri = df_ideal[item][0]
                self.axes.axhline(cri, color='r', linestyle='-', linewidth=4)
            else:
                cri = -1
            self.axes.set_title(item)
            self.axes.set_xticks(x)
            # self.axes.set_ylim(0,max(np.max(y),cri)+10)

            # not sure why np.min() / np.max() not working
            y_min = sys.float_info.max
            y_max = -sys.float_info.max
            for i in range(0, y.shape[0]):
                if (math.isnan(y[i])):
                    continue
                if (y[i] < y_min):
                    y_min = y[i]
                elif (y[i] > y_max):
                    y_max = y[i]

            # print(y_min, y_max, np.amin(y), np.amax(y))
            # 4.43289792333271 62.82625302045408 31.89259259259258 31.89259259259258

            if cri == -1:
                self.axes.set_ylim(y_min - 10, y_max + 10)
            else:
                self.axes.set_ylim(min(y_min, cri) - 10, max(y_max, cri) + 10)



            self.axes.set_xticklabels(x_name, rotation=25, fontsize=10)
            self.canvas.draw()
        except:
            self.axes.imshow(self.no_hist_img)
            self.canvas.draw()
