 # coding: utf-8
import wx
import cv2
import numpy as np
import pandas as pd
import wx.media
import matplotlib
from matplotlib.figure import Figure
from collections import defaultdict
import wx.lib.mixins.inspection as WIT

import sys, math, os
import random
from datetime import datetime

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from ..klib import bodygame3
from ..klib import trainingmode
from .historylog import Historylog

class Welcome_win(wx.Frame):
    def __init__(self, info, parent=None, title="Home"):
        self.font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.font_field = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.font_title = wx.Font(36, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Lucida Handwriting')
        self.font_text = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.font_text_title = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial')
        self.info = info
        self.game = None

        self.width, self.height = wx.GetDisplaySize()
        self.height -= 100
        self.sizer_w = 10
        self.sizer_h = 10

        super(Welcome_win, self).__init__(parent, title=title, size=(self.width, self.height),  style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        isz = (16, 16)
        ico = wx.Icon('./data/imgs/others/logo.png', wx.BITMAP_TYPE_PNG, isz[0], isz[1])
        self.SetIcon(ico)

        self.init_ui()
        self.Show()

    def init_ui(self):
        self.panel = wx.Panel(self)

        # sizers
        combine = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        topSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        lineSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        buttonSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        menuSizer = wx.BoxSizer(wx.VERTICAL)
        dailySizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        infoSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)

        # title
        text = wx.StaticText(self.panel, label="LymphCoach")
        text.SetFont(self.font_title)
        topSizer.Add(text, 0, wx.CENTER)

        line = wx.StaticLine(self.panel)
        lineSizer.Add(line, pos=(0, 0), span=(2, int(self.width/self.sizer_w/2)), flag=wx.EXPAND|wx.BOTTOM)

        if self.info.isPat:
            text1 = wx.StaticText(self.panel, label='Hi ' + self.info.fname + '! How\'s your day!')
        elif self.info.isCli:
            text1 = wx.StaticText(self.panel, label='Hi ' + self.info.fcname + '! How\'s your day!')
        text1.SetFont(self.font)
        titleSizer.Add(text1, pos=(1, 0))

        button_size = (300, 50)

        menu_title = wx.StaticText(self.panel, label="Menu")
        menu_title.SetFont(self.font_text_title)

        button1 = wx.Button(self.panel, size=button_size, label="Instruction with Video")
        button1.SetFont(self.font)
        button1.Bind(wx.EVT_BUTTON, self.open_instruction)

        # button2 = wx.Button(self.panel, size=button_size, label="Training Mode")
        # button2.SetFont(self.font)
        # button2.Bind(wx.EVT_BUTTON, self.open_trainingmode)

        button3 = wx.Button(self.panel, size=button_size, label="Evaluation Mode")
        button3.SetFont(self.font)
        button3.Bind(wx.EVT_BUTTON, self.open_bodygame)

        button4 = wx.Button(self.panel, size=button_size, label="History Review")
        button4.SetFont(self.font)
        button4.Bind(wx.EVT_BUTTON, self.open_history)

        buttonSizer.Add(button1, pos=(1, 0))
        # buttonSizer.Add(button2, pos=(2, 0))
        buttonSizer.Add(button3, pos=(2, 0))
        buttonSizer.Add(button4, pos=(3, 0))
        menuSizer.Add(menu_title, 0, wx.CENTER)
        menuSizer.Add(buttonSizer, 0, wx.CENTER)


        # http://optimallymph.org/en/login?destination=lymphedema
        self.sentences = ["I like the exercises!!! After I finished learning the exercises by following the videos, my pain and soreness were much better.",
                            "Videos are very helpful in teaching how to do the exercises. It is nice that I can go back and watch it again & again. I am glad that patients can have it at home. I love the contents & hope patients can get it sooner. I enjoyed the videos a lot.",
                            "I love the videos that show the anatomy & fluid flow & deep breathing. I also love the lymphatic system video.",
                            "The videos of how to perform the lymphatic exercises were very easy to follow.",
                            "Videos are excellent-you could do as you watched.",
                            "Love the avatar videos. You can follow the videos and do the exercises.",
                            "It was helpful to have an animated model of the exercises, rather than a sheet with merely pictures of the exercises.",
                            "I love to follow the daily videos to do the exercises.",
                            "It made me realize that I can manage the loss of strength in my right arm and may be able to manage the numbness and tingling.  I will be able to help myself.",
                            "Being on this study allowed me to do something for myself, really take care of myself and focus on being healthy.",
                            "It helped me realize that I had excess fluid.  My arms got lighter each time I did the exercises.  My arms began to feel less heavy.  It noticed it in my clothes as well.",
                            "It help me to understand more about all my symptoms, and how to manage them with the exercises.",
                            "This is a very easy study and the videos helped to complete the exercise.",
                            "I can repeat & review particular sections whenever and wherever I want.",
                            "I like the fact that I can go to the site at any time even when I travel.",
                            "The [lymphatic] exercise were easy and could be completed anywhere.  According to my measurements there was a decrease in fluid. That was good news.",
                            "The exercises were easy to do and remember. If I noticed my arm was more stiff than usual, I would do the exercises more and they helped.",
                            "It is not about whether I can do it (self-care) or I feel I can do it. The breathing and pumping exercises (daily lymphatic exercise) are easily to do and I feel better after doing them. So, I do it every day.",
                            "I personally feel the exercise helped with the pain.",
                            "The exercises made my arm feel a lot better.",
                            "The exercise really helped increase my range of motion and was effective for decreasing my pain. I do the exercises every day.",
                            "The exercises definitely helped reduce pain and increase mobility.",
                            "The [lymphatic] exercise really helped increase my range of motion and was effective for decreasing my pain. I do the exercises every day.",
                            "The [lymphatic] exercise made my arm feel a lot better.",
                            "Being aware of lymphedema risk and informed about it helped me tremendously. I didn’t know what lymphedema was... I felt more in control rather than just hoping I would not get lymphedema. I was doing something to prevent it. It gave me a sense of empowerment.",
                            "The best thing I have done for myself was to participate in The-Optimal-Lymph-Flow program. I only had 1 node removed. I thought that I am fine. During the radiation, I had slight swelling in my arm and I started religiously doing the breathing and pumping exercises. It worked and now I am doing the exercises every day because I feel good after doing the exercises. Without the program, I probably would be like my friend who has a huge arm now.",
                            "I truly believe that participating in The-Optimal-Lymph-Flow program has been the pillar of strength for me following my mastectomy and lymph node dissection. The program enabled me to feel armed with knowledge and preventive measures to keep me from getting lymphedema.",
                            "It is a simple program and awareness of the result is also motivating.",
                            "I was very pleased that I could reduce my risk with very simple techniques (breathing, pumping, & walking).",
                            "The pumping & breathing are something I can do. I can do more and feel better.",
                            "Wonderful to have been aware before surgery of the exercises and get into the habit of doing them. After surgery, I didn’t have to review the direction and just began to do what I had been doing already.",
                            "I am doing the right exercise (breathing and pumping) on the daily basis. I feel good and I feel that I owe it to myself.",
                            "Being aware of factors that contribute to developing lymphedema and specific measures to alleviate symptoms has been instrumental in reducing any swelling. I have experienced and have motivated/aware of making choice to reduce my risk."]

        sentence_title = wx.StaticText(self.panel, label="Daily Empowerment")
        sentence_title.SetFont(self.font_text_title)
        random.seed(datetime.now())
        sentence = wx.StaticText(self.panel, label=self.sentences[random.randrange(len(self.sentences))], size=(500, 300))
        sentence.SetFont(self.font_text)
        dailySizer.Add(sentence_title, pos=(0, 0))
        dailySizer.Add(sentence, pos=(2, 0))

        infoSizer.Add(menuSizer, pos=(1, 0))
        infoSizer.Add(dailySizer, pos=(1, 4))

        topSizer.Add(lineSizer, 0, wx.CENTER)
        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(infoSizer, 0, wx.CENTER)
        combine.Add(topSizer, pos=(2, 0))
        self.panel.SetSizer(combine)


    def open_bodygame(self, event):
        self.game = bodygame3.BodyGameRuntime(self.info)
        self.game.run()

    def open_instruction(self, event):
        instruct = Instrcution_win(None, 'Instruction')

    def open_history(self, event):
        history = History_view(None, self.info)

    def open_trainingmode(self, event):
        self.train = trainingmode.BodyGameRuntime()
        self.train.run()

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

        self.width, self.height = wx.GetDisplaySize()
        ratio = self.height / 600.0
        self.player_width = 640 * ratio
        self.player_height = 360 * ratio
        self.height -= 100
        # self.width = 1100
        # self.height = self.player_height * 1.5 + 45

        self.sizer_w = 5
        self.sizer_h = 5

        super(Instrcution_win, self).__init__(parent, title=title, size=(self.width, self.height))
        isz = (16, 16)
        ico = wx.Icon('./data/imgs/others/logo.png', wx.BITMAP_TYPE_PNG, isz[0], isz[1])
        self.SetIcon(ico)
        self.init_ui()
        self.Show()

    def init_ui(self):
        self.panel = wx.Panel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box2 = wx.BoxSizer(wx.VERTICAL)
        box3 = wx.BoxSizer(wx.VERTICAL)

        self.font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.player = MoviePanel(self.panel, (self.player_width, self.player_height))

        self.text = wx.TextCtrl(self.panel, size=(self.player_width, self.player_height/2), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text.SetFont(self.font)
        self.text.SetBackgroundColour((255, 255, 255))
        # self.text.SetBackgroundColour((179, 236, 255))

        button1 = wx.Button(self.panel, label="Home")
        button1.Bind(wx.EVT_BUTTON, self.close)

        button_print = wx.Button(self.panel, id=wx.ID_PRINT, label="")
        button_print.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.OnBtnPrint, button_print)

        exer = [self.str['exe'][i] for i in range(1, 8)]
        self.lst = wx.ListBox(self.panel, size=(350, self.height - 25 - 45), choices=exer, style=wx.LB_SINGLE)
        self.lst.SetBackgroundColour((230, 230, 230))
        self.lst.SetSelection(0)

        box2.Add(self.lst, 0, wx.EXPAND)
        box2.Add(button1, 0, wx.EXPAND)
        box3.Add(self.player, 0, wx.EXPAND)

        text_sizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        text_sizer.Add(button_print, (0, 4))
        text_sizer.Add(self.text, (0, 0), span=(4, 0))  # for .avi .mpg video files

        # box3.Add(self.text, 0, wx.LEFT)
        box3.Add(text_sizer, 0, wx.LEFT)

        box.Add(box2, 0,wx.EXPAND)
        box.Add(box3, 1, wx.EXPAND)
        # box.Add(button_print, 2, wx.RIGHT)
        self.panel.SetSizer(box)
        self.panel.Fit()

        self.Centre()
        self.Bind(wx.EVT_LISTBOX, self.onListBox, self.lst)

        # default selection: exercise 1
        self.onListBox(None)


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
                             '\n1. Put your hands on the abdomen.'\
                             '\n2. Wait until the sign shows "start breathe in/out."'\
                             '\n3. Do deep breathing 4 times.'\
                             '\n4. Put down your hands.'

        self.str['ins'][2] = '\n  '\
                             '\n1. Raise your harms up and hold there.'\
                             '\n2. Wait until the sign shows "start breathe in/out."'\
                             '\n3. Do deep breathing 4 times.' \
                             '\n4. Put down your arms.'

        self.str['ins'][3] = '\n  '\
                             '\n1. Raise your arms up.'\
                             '\n2. Lower your elbows, let shoulder-elbow-hand be a V-shape.'\
                             '\n3. Raise your arms up again.'\
                             '\n4. Repeat this 4 times.'\
                             '\n5. Put down your arms.'

        self.str['ins'][4] = '\n  '\
                             '\n1. Raise your arms up till "T-pose."'\
                             '\n2. Move arms slowly to the chest.'\
                             '\n3. Back to "T-pose".'\
                             '\n4. Repeat this 4 times.'\
                             '\n5. Put down your arms.'

        self.str['ins'][5] = '\n  '\
                             '\n1. Raise your arms up  as high as possible and clasp.'\
                             '\n2. Bend your body to the left.'\
                             '\n3. Bend your body to the right.'\
                             '\n4. Repeat 4 times.'\
                             '\n5. Put down your arms.'

        self.str['ins'][6] = '\n  '\
                             '\n1. Put your hands on the abdomen.'\
                             '\n2. Rotate you shoulder.'\
                             '\n3. Repeat 4 times.'\
                             '\n4. Put down your hands.'

        self.str['ins'][7] = '\n  '\
                             '\n1. Raise and clasp your hands to the abdomen.'\
                             '\n2. Raise clasped hands toward to your forehead and keep elbows together.'\
                             '\n3. Slide your hands to the back of your head and spread the elbows open wide.'\
                             '\n4. Back to the abdomen.'\
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
                                '\n1. When you raise your arms, make sure that your hand, elbow, and shoulder are straight.'\
                                '\n2. When you bend your elbow, hand - elbow - shoulder should be "V-shape" not "L-shape"'\

        self.str['note'][4] = 'Tips :'\
                                '\n1. When you do the "T-pose", make sure that your hand, elbow, and shoulder are straight'\
                                '\n2. When you close your hands, make sure that your hand and shoulder are in the same height.'\

        self.str['note'][5] = 'Tips :'\
                                '\n1. When you bend your body, make sure that your hand, elbow, and shoulder are straight.'\
                                '\n2. Keep your body staight'

        self.str['note'][6] = 'Tips :'\
                                '\n1. Try to rotate your shoulders in a full circle'

        self.str['note'][7] = 'Tips :'\
                                '\n1. When you raise your arms to the forehead, keep two elbows as close as possible.'\
                                '\n2. When your hands are in the back, spread the elbows open as wide as possible.'\
                                '\n3. Keep your body staight.'

    def onListBox(self, event):
        self.text.Clear()
        ex = self.lst.GetSelection()+1
        self.text.AppendText(self.str['exe'][ex]+self.str['ins'][ex]+'\n\n')
        self.text.AppendText(self.str['note'][ex])
        if ex == 5:
            self.player.doLoadFile(os.path.abspath('data/video/ex'+str(ex)+'.mpg'))
        else:
            self.player.doLoadFile(os.path.abspath('data/video/tr'+str(ex)+'.mp4'))


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
    def __init__(self, parent, size, id=-1):
        #self.log = log
        wx.Panel.__init__(self, parent, id, style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN)

        self.sizer_w = 5
        self.sizer_h = 5

        # Create some controls
        self.mc = wx.media.MediaCtrl(self, size=size, style=wx.SIMPLE_BORDER)
        self.playButton = wx.Button(self, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.onPlay, self.playButton)

        self.pauseButton = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.onPause, self.pauseButton)

        self.stopButton = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self.onStop, self.stopButton)

        self.slider = wx.Slider(self, -1, 0, 0, 10)
        self.slider.SetMinSize((100, -1))
        self.Bind(wx.EVT_SLIDER, self.OnSeek, self.slider)

        # setup the button/label layout using a sizer
        sizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        # sizer.Add(loadButton, (1,1))
        sizer.Add(self.playButton, (2, 4))
        sizer.Add(self.pauseButton, (3, 4))
        sizer.Add(self.stopButton, (4, 4))
        sizer.Add(self.slider, (5, 4))
        sizer.Add(self.mc, (0, 0), span=(6, 0))  # for .avi .mpg video files
        self.SetSizer(sizer)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(100)


    def doLoadFile(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
            self.playButton.Disable()
        else:
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.playButton.Enable()
            # self.mc.Play()#ITS TO PROBLEM, WHY IT DOESNT PLAY HERE?#

    def onPlay(self, evt):
        self.mc.Play()
        self.GetSizer().Layout()
        self.slider.SetRange(0, self.mc.Length())

    def onPause(self, evt):
        self.mc.Pause()

    def onStop(self, evt):
        self.mc.Stop()

    def OnSeek(self, evt):
        offset = self.slider.GetValue()
        self.mc.Seek(offset)

    def OnTimer(self, evt):
        offset = self.mc.Tell()
        # update value of slider
        self.slider.SetValue(offset)

    def ShutdownDemo(self):
        self.timer.Stop()
        del self.timer


class History_view(wx.Frame):
    def __init__(self, parent, info, title='history log'):

        self.width, self.height = wx.GetDisplaySize()
        self.height -= 100
        self.sizer_w = 5
        self.sizer_h = 5
        self.sub_width = 260

        super(History_view, self).__init__(parent, title=title, size=(self.width, self.height))
        isz = (16, 16)
        ico = wx.Icon('./data/imgs/others/logo.png', wx.BITMAP_TYPE_PNG, isz[0], isz[1])
        self.SetIcon(ico)

        self.info = info
        self.no_hist_img = cv2.imread('./data/imgs/others/no_hist.jpg')
        self.init_ui()
        self.color_correct = (0.41, 0.75, 0.07, 0.6)
        self.color_line = ['#0096BF', '#005A73', '#BFA600', '#736400', '#ffae25', '#af7900', '#d957b4', '#75005b']
        self.Show()

    def init_ui(self, path='./output/log.xlsx'):
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

        box1 = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        box2 = wx.BoxSizer(wx.VERTICAL)
        box3 = wx.BoxSizer(wx.HORIZONTAL)

        if self.info.isPat:
            info_text = 'Patient:' + \
                        '\nName: ' + self.info.name.title() + \
                        '\nGender: ' + self.info.gender.title() + \
                        '\nID: ' + str(self.info.id)
        else:
            info_text = 'Clinician:' + \
                        '\nName: ' + self.info.name.title() + \
                        '\nGender: ' + self.info.gender.title()

        info = wx.StaticText(self.panel, wx.ID_ANY, label=info_text)
        info.SetFont(self.font)
        box1.Add(info, pos=(1, 2))

        ex_choices = log_xl.sheet_names
        self.choice = wx.Choice(self.panel, choices=ex_choices)
        self.choice.SetFont(self.font)
        # default selection: exercise 1
        self.choice.SetSelection(0)
        self.choice.Bind(wx.EVT_CHOICE, self.update_choice)
        box1.Add(self.choice, pos=(2, 2))

        # provide list of patients to review
        if self.info.isCli:
            self.name = wx.Choice(self.panel, choices=[])
            self.name.SetFont(self.font)
            self.name.Bind(wx.EVT_CHOICE, self.update_name_cli)
            box1.Add(self.name, pos=(3, 2))

            # self.score = wx.StaticText(self.panel, wx.ID_ANY, label="Score: ")
            # self.score.SetFont(self.font)
            # box1.Add(self.score, pos=(4, 2))

        line = wx.StaticLine(self.panel)
        box1.Add(line, pos=(5, 0), span=(0, int(self.sub_width / self.sizer_w / 4)), flag=wx.EXPAND|wx.BOTTOM)

        button1 = wx.Button(self.panel, label="Home")
        button1.Bind(wx.EVT_BUTTON, self.close)

        box2.Add(box1, 0)
        self.lst = wx.ListBox(self.panel, size=(self.sub_width, self.height - 230), choices=[], style=wx.LB_SINGLE)
        self.lst.SetFont(self.font)
        self.lst.SetBackgroundColour((230, 230, 230))
        self.Bind(wx.EVT_LISTBOX, self.update_figure, self.lst)
        box2.Add(self.lst, 0, wx.EXPAND)
        box2.Add(button1, 0, wx.EXPAND)
        box3.Add(box2, 0, wx.EXPAND)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.panel, -1, self.figure)
        box3.Add(self.canvas, 1, wx.EXPAND)

        self.panel.SetSizer(box3)
        self.panel.Fit()

        # default selection: exercise 1
        self.update_choice(None)

    def close(self, event):
        self.Destroy()

    def update_choice(self, event):
        cur_choice = self.choice.GetSelection()
        self.df = pd.read_excel(self.path, sheet_name=cur_choice)
        # self.df.fillna(0, inplace=True)
        self.lst.Clear()
        lst_choice = self.df.columns.values.tolist()
        idx_1 = [i for i, elem in enumerate(lst_choice) if 'time' in elem][0] + 1
        idx_2 = [i for i, elem in enumerate(lst_choice) if 'errmsg' in elem][0]
        self.lst.InsertItems(lst_choice[idx_1:idx_2], 0)
        self.lst.InsertItems(["Overall score"], 0)
        if (self.info.isCli):
            self.update_name_list_cli()

    def update_name_list_cli(self):
        df_unique_names = self.df['name'].unique()[1:]
        self.name.Clear()
        self.name.AppendItems(df_unique_names)
        self.name.SetSelection(0)
        self.cur_choice = self.name.GetStringSelection()

    def update_name_cli(self, event):
        self.cur_choice = self.name.GetStringSelection()
        if self.lst.GetStringSelection() != '':
            self.update_figure_cli()

    def update_figure(self, event):
        if self.info.isPat:
            self.update_figure_pat()
        elif self.info.isCli:
            self.update_figure_cli()

    # helper function for debugging
    def debug(self, arr):
        print(arr, arr.shape, type(arr))

    def get_score_list(self, name):
        self.axes.clear()
        self.axes.set_title("Patient: " + name + "\n" + "Overall score")

        # list of features
        list = np.array(self.lst.GetStrings())
        df_name = self.df[self.df['name'] == name]
        df_ideal = self.df[self.df['name'] == '$IDEAL VALUE$']

        total_score = np.zeros((df_name.shape[0], 1))
        no_ideal = True
        exercise_4 = False

        if self.choice.GetSelection() == 3:
            # selection by index
            exercise_4 = True

        # get total score for each day
        for i in range(1, len(list)):
            y = np.array(df_name[list[i]])
            # self.debug(y)
            y = np.reshape(y, (len(y), 1))
            y_min, y_max = self.find_min_max(y)
            y_span = y_max - y_min

            cri = -1
            if df_ideal[list[i]].dtype == float:
                cri = df_ideal[list[i]][0]
                no_ideal = False
            else:
                cri = y_max - y_span * 0.1

            if exercise_4:
                y = -abs(y - cri)
            else:
                if ("lower" not in list[i]) and ("push down" not in list[i]):
                    y = y - cri
                else:
                    y = cri - y

            if (np.all(pd.isnull(y))):
                continue
            else:
                total_score = total_score + y / y_span

        total_score = 1 + total_score / (len(list) - 1)
        # self.debug(total_score)

        y = total_score * 100
        x = np.arange(0, len(y))
        self.axes.plot(x, y, color=self.color_line[0])
        self.axes.set_xticks(x)
        # self.debug(y)

        y_min, y_max = self.find_min_max(y)
        # print(y_min, y_max)
        self.axes.set_ylim(y_min[0] - 5, y_max[0] + 5)

        x_name = np.array([x.split("-") for x in df_name['time']])
        x_name = np.array([(x[1] + "/" + x[2]) for x in x_name])
        prev_index = 0
        for i in range(1, len(x_name)):
            if x_name[prev_index] == x_name[i]:
                x_name[i] = ""
            else:
                prev_index = i
        self.axes.set_xticklabels(x_name, rotation=20, fontsize=6)
        self.canvas.draw()

    # general drawing function
    def draw_figure(self, name, item, df_name, df_ideal):
        y = np.array(df_name[item])
        x = np.arange(0, len(y))

        self.axes.set_xticks(x)
        self.axes.set_title("Patient: " + name + "\n" + item)
        self.axes.plot(x, y, color=self.color_line[0])

        y_min, y_max = self.find_min_max(y)
        y_span = y_max - y_min

        if df_ideal[item].dtype == float:
            cri = df_ideal[item][0]
        else:
            cri = y_max - y_span * 0.1

        self.axes.axhline(cri, color=self.color_correct, linestyle='-', linewidth=30)
        self.axes.set_ylim(min(y_min, cri) - 10, max(y_max, cri) + 10)

        x_name = np.array([a.split("-") for a in df_name['time']])
        x_name = np.array([(a[1] + "/" + a[2]) for a in x_name])
        prev_index = 0
        for i in range(1, len(x_name)):
            if x_name[prev_index] == x_name[i]:
                x_name[i] = ""
            else:
                prev_index = i
        self.axes.set_xticklabels(x_name, rotation=20, fontsize=6)
        self.canvas.draw()


    def update_figure_cli(self):
        df_name = self.df[self.df['name'] == self.cur_choice]
        df_ideal = self.df[self.df['name'] == '$IDEAL VALUE$']
        item = self.lst.GetStringSelection()
        self.axes.clear()
        # self.figure.texts.clear()

        if item == "Overall score":
            self.get_score_list(self.cur_choice)
            return

        # try:
        self.draw_figure(self.cur_choice, item, df_name, df_ideal)
        # except:
        #     self.axes.imshow(self.no_hist_img)
        #     self.canvas.draw()


    def update_figure_pat(self):
        df_name  = self.df[self.df['name'] == self.info.name]
        df_ideal = self.df[self.df['name'] == '$IDEAL VALUE$']
        item = self.lst.GetStringSelection()
        self.axes.clear()

        if item == "Overall score":
            self.get_score_list(self.info.name)
            return

        # try:
        self.draw_figure(self.info.name, item, df_name, df_ideal)
        # except:
        #     self.axes.imshow(self.no_hist_img)
        #     self.canvas.draw()

    def find_min_max(self, y):
        y_min = sys.float_info.max
        y_max = -sys.float_info.max
        for i in range(0, y.shape[0]):
            if (math.isnan(y[i])):
                continue
            if (y[i] < y_min):
                y_min = y[i]
            elif (y[i] > y_max):
                y_max = y[i]
        return (y_min, y_max)
