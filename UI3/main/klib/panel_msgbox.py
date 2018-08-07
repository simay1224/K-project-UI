import wx, pdb, sys

class Msgbox(wx.Frame):

    def __init__(self, parent=None, title="Info"):
        self.font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.font_field =  wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD, False, 'Arial')
        self.font_button = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Arial')
        self.font_title = wx.Font(36, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Lucida Handwriting')

        self.width, self.height = wx.GetDisplaySize()
        self.height -= 100
        self.sizer_w = 10
        self.sizer_h = 10

        super(Msgbox, self).__init__(parent, title=title, size=(self.width, self.height), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        isz = (16, 16)
        ico = wx.Icon('./data/imgs/others/logo.png', wx.BITMAP_TYPE_PNG, isz[0], isz[1])
        self.SetIcon(ico)

        self.fname = ''
        self.lname = ''
        self.name = ''
        self.id = ''
        self.num = ''
        self.gender = ''
        self.isCli = False
        self.isPat = False

        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        self.panel = wx.Panel(self)

        combine = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        topSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        lineSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        patiSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        clinSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        infoSizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)
        sizer = wx.GridBagSizer(self.sizer_w, self.sizer_h)

        # title
        text = wx.StaticText(self.panel, label="LymphCoach")
        text.SetFont(self.font_title)
        topSizer.Add(text, 0, wx.CENTER)

        line = wx.StaticLine(self.panel)
        lineSizer.Add(line, pos=(0, 0), span=(2, int(self.width/self.sizer_w/2)), flag=wx.EXPAND|wx.BOTTOM)

        # -------------- Patient -------------- #

        patient = wx.StaticText(self.panel, label="Patient")
        patient.SetFont(self.font_field)
        patiSizer.Add(patient, pos=(1, 0), flag=wx.CENTER)

        # Name
        text1 = wx.StaticText(self.panel, label="First Name")
        text1.SetFont(self.font)
        patiSizer.Add(text1, pos=(2, 0), flag=wx.LEFT)

        self.tc1 = wx.TextCtrl(self.panel)
        patiSizer.Add(self.tc1, pos=(2, 1), flag=wx.EXPAND)

        text2 = wx.StaticText(self.panel, label="Last Name")
        text2.SetFont(self.font)
        patiSizer.Add(text2, pos=(3, 0), flag=wx.LEFT)

        self.tc2 = wx.TextCtrl(self.panel)
        patiSizer.Add(self.tc2, pos=(3, 1), flag=wx.EXPAND)

        # ID
        text3 = wx.StaticText(self.panel, label="ID")
        text3.SetFont(self.font)
        patiSizer.Add(text3, pos=(4, 0), flag=wx.LEFT)

        self.tc3 = wx.TextCtrl(self.panel)
        patiSizer.Add(self.tc3, pos=(4, 1), flag=wx.EXPAND)

        sb = wx.StaticBox(self.panel, label="Please Select Your Gender")
        sb.SetFont(self.font)
        self.rb_female = wx.RadioButton(self.panel, label="Female", style=wx.RB_GROUP)
        self.rb_female.SetFont(self.font)
        self.rb_male = wx.RadioButton(self.panel, label="Male")
        self.rb_male.SetFont(self.font)

        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        boxsizer.Add(self.rb_female)
        boxsizer.Add(self.rb_male)
        patiSizer.Add(boxsizer, pos=(5, 0), span=(0, 3), flag=wx.EXPAND)

        # -------------- Clinician -------------- #

        clinician = wx.StaticText(self.panel, label="Clinician")
        clinician.SetFont(self.font_field)
        clinSizer.Add(clinician, pos=(1, 0), flag=wx.CENTER)

        # Name
        text1 = wx.StaticText(self.panel, label="First Name")
        text1.SetFont(self.font)
        clinSizer.Add(text1, pos=(2, 0), flag=wx.LEFT)

        self.tcc1 = wx.TextCtrl(self.panel)
        clinSizer.Add(self.tcc1, pos=(2, 1), flag=wx.EXPAND)

        text2 = wx.StaticText(self.panel, label="Last Name")
        text2.SetFont(self.font)
        clinSizer.Add(text2, pos=(3, 0), flag=wx.LEFT)

        self.tcc2 = wx.TextCtrl(self.panel)
        clinSizer.Add(self.tcc2, pos=(3, 1), flag=wx.EXPAND)

        text3 = wx.StaticText(self.panel, label="Access #\n(112233)")
        text3.SetFont(self.font)
        clinSizer.Add(text3, pos=(4, 0), flag=wx.LEFT)

        text4 = wx.StaticText(self.panel, label="Only for Clinician Access");
        text4.SetFont(self.font_button)
        clinSizer.Add(text4, pos=(5, 0), flag=wx.LEFT)

        self.tcc3 = wx.TextCtrl(self.panel)
        clinSizer.Add(self.tcc3, pos=(4, 1), flag=wx.EXPAND)

        # -------------- General -------------- #

        self.button_pat = wx.RadioButton(self.panel, label="Patient Login", style=wx.RB_GROUP)
        self.button_pat.SetFont(self.font)
        self.button_cli = wx.RadioButton(self.panel, label="Clinician Login")
        self.button_cli.SetFont(self.font)

        sizer.Add(self.button_pat, pos=(1, 1), span=(0, 0), flag=wx.LEFT, border=10)
        sizer.Add(self.button_cli, pos=(1, 4), span=(0, 0), flag=wx.LEFT, border=10)

        button1 = wx.Button(self.panel, size=(200, 50), label="Ok")
        sizer.Add(button1, pos=(2, 0), span=(0, 0), flag=wx.LEFT, border=10)
        button1.SetFont(self.font_button)
        button1.Bind(wx.EVT_BUTTON, self.ok)

        button2 = wx.Button(self.panel, size=(200, 50), label="Cancel")
        sizer.Add(button2, pos=(2, 5), span=(0, 0), flag=wx.RIGHT, border=10)
        button2.SetFont(self.font_button)
        button2.Bind(wx.EVT_BUTTON, self.cancel)

        infoSizer.Add(patiSizer, pos=(1, 0), span=(0, 0), flag=wx.LEFT)
        line = wx.StaticLine(self.panel, -1, size=(1, self.height / 5), style=wx.LI_VERTICAL)
        infoSizer.Add(line, pos=(1, 2), span=(1, 0), flag=wx.EXPAND)
        infoSizer.Add(clinSizer, pos=(1, 4), span=(0, 0), flag=wx.RIGHT)

        topSizer.Add(titleSizer, 0, wx.CENTER)
        topSizer.Add(lineSizer, 0, wx.CENTER)
        topSizer.Add(infoSizer, 0, wx.CENTER)
        topSizer.Add(sizer, 0, wx.CENTER)
        combine.Add(topSizer, pos=(2, 0))
        self.panel.SetSizer(combine)

    def ok(self, event):
        # -------------- Patient -------------- #
        self.fname = self.tc1.GetValue()
        self.lname = self.tc2.GetValue()
        # id could involve chars
        self.id = self.tc3.GetValue()

        if self.rb_female.GetValue():
            self.gender = 'Female'
        elif self.rb_male.GetValue():
            self.gender = 'Male'
        else:
            self.gender = ''
        # -------------- Clinician -------------- #
        self.fcname = self.tcc1.GetValue()
        self.lcname = self.tcc2.GetValue()
        self.num = self.tcc3.GetValue()
        if (self.num != ''):
            try:
                self.num = int(self.num)
            except:
                pass
        # -------------- General -------------- #
        if self.button_pat.GetValue():
            self.isPat = True
        else:
            self.isPat = False
        if self.button_cli.GetValue():
            self.isCli = True
        else:
            self.isCli = False

        # self.cliInfo = True if (len(self.fcname) != 0 or len(self.lcname) != 0) else False
        # self.patInfo = True if (len(self.fname) != 0 or len(self.lname) != 0 or self.id != '') else False
        # self.cliNum = True if (self.num != '') else False
        #
        # self.isCli = True if ((self.cliInfo or self.cliNum) and (not self.patInfo)) else False
        # self.isPat = True if (self.patInfo and (not self.cliNum)) else False

        error = ''
        error_flag = False

        if self.isCli and self.isPat:
            error += 'please only enter necessary information'
            error_flag = True
        elif (not self.isCli) and (not self.isPat):
            error += 'please enter information to verify your identity'
            error_flag = True
        else:
            if self.isPat:
                error += 'Patient Log in:\n'
                if len(self.lname) == 0 or len(self.fname) == 0:
                    error += '\tplease complete your name\n'
                    error_flag = True
                # id could be non-integer
                if self.id == '':
                    error += '\tplease enter your id\n'
                    error_flag = True
                if (not self.rb_female.GetValue()) and (not self.rb_male.GetValue()):
                    error += '\tplease choose your gender\n'
                    error_flag = True
                if len(self.fcname) == 0 or len(self.lcname) == 0:
                    error += '\tplease enter your clinician\'s name\n'
                    error_flag = True
            else:
                error += 'Clinician Log in:\n'
                if len(self.fcname) == 0 or len(self.lcname) == 0:
                    error += '\tplease complete your name\n'
                    error_flag = True
                if self.num != '':
                    if type(self.num) != int:
                        error += '\tid should be an integer\n'
                        error_flag = True
                    if self.num != 112233:
                        error += '\tpermission number is not correct\n'
                        error_flag = True
                else:
                    error += '\tplease enter permission number\n'
                    error_flag = True

        if error_flag:
            dlg = wx.MessageDialog(self.panel, error,'', wx.YES_NO | wx.ICON_ERROR)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()

        else:
            message = 'Is the following infomation correct?\nPatient:\n\tName: %s\n\tID: %s\n\tGender: %s' % (self.fname+' '+self.lname, self.id, self.gender)
            if self.isCli:
                message = 'Is the following infomation correct?\nClinician:\n\tName: %s' % (self.fcname+' '+self.lcname)
            dlg = wx.MessageDialog(self.panel, message, 'Double check the infomation', wx.YES_NO | wx.ICON_INFORMATION)
            result = dlg.ShowModal() == wx.ID_YES

            if result:
                if (self.isPat):
                    self.name = (self.fname + ' ' + self.lname).lower()
                if (self.isCli):
                    self.name = (self.fcname + ' ' + self.lcname).lower()
                dlg.Destroy()
                self.Destroy()
            else:
                dlg.Destroy()

    def cancel(self, event):
        self.fname = 'Jane'
        self.lname = 'Doe'
        self.fcname = 'CliDefault'
        self.lcname = 'CliDefault'
        self.isPat = True
        self.isCli = False
        self.id = '190008'
        self.gender = 'Female'
        message = 'Do you want to use following information?\nName: %s\nID: %s\nGender: %s' %(self.fname+' '+self.lname, self.id, self.gender)
        dlg = wx.MessageDialog(self.panel, message,'Double check the infomation', wx.YES_NO | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_YES

        dlg.Destroy()
        if result:
            self.name = (self.fname + ' ' + self.lname).lower()
            self.Destroy()
        else:
            self.reset()

    def reset(self):
        self.fname = ''
        self.lname = ''
        self.fcname = ''
        self.lcname = ''
        self.id = ''
        self.num = ''
        self.gender = ''
        self.isCli = False
        self.isPat = False
        self.tc1.SetValue('')
        self.tc2.SetValue('')
        self.tc3.SetValue('')
        self.tcc1.SetValue('')
        self.tcc2.SetValue('')
        self.tcc3.SetValue('')
        self.rb_female.SetValue(False)
        self.rb_male.SetValue(False)
        self.button_pat.SetValue(False)
        self.button_cli.SetValue(False)

    def _pass(self):
        self.fname = 'Jane'
        self.lname = 'Doe'
        # self.fname = 'test'
        # self.lname = 'test'
        self.fcname = 'CliDefault'
        self.lcname = 'CliDefault'
        self.name = (self.fname + ' ' + self.lname).lower()
        # self.id = '190008'
        self.id = '11201'
        self.gender = 'Female'
        self.isPat = True
        self.isCli = False
