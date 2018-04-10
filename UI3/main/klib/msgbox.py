import wx, pdb

class Msgbox(wx.Frame):

    def __init__(self, parent, title):    
        super(Msgbox, self).__init__(parent, title=title, 
            size=(400, 260), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.fname  = 'Jane'
        self.lname  = 'Doe'
        self.age    = 'unknown'
        self.gender = 'unknown' 
        self.InitUI()
        self.Centre()
        self.Show()     

    def InitUI(self):
      
        self.panel = wx.Panel(self)
        
        sizer = wx.GridBagSizer(6, 5)

        line = wx.StaticLine(self.panel)
        sizer.Add(line, pos=(1, 0), span=(1, 6), 
            flag=wx.EXPAND|wx.BOTTOM, border=10)
        # Name
        text1 = wx.StaticText(self.panel, label="First Name")
        sizer.Add(text1, pos=(2, 0), flag=wx.LEFT, border=10)

        self.tc1 = wx.TextCtrl(self.panel)
        sizer.Add(self.tc1, pos=(2, 1), span=(1, 1))

        text2 = wx.StaticText(self.panel, label="Last Name")
        sizer.Add(text2, pos=(2, 2), flag=wx.LEFT|wx.EXPAND, border=10)

        self.tc2 = wx.TextCtrl(self.panel)
        sizer.Add(self.tc2, pos=(2, 3), span=(2, 1))

        # Age
        text3 = wx.StaticText(self.panel, label="Age")
        sizer.Add(text3, pos=(3, 0), flag=wx.LEFT, border=10)

        self.tc3 = wx.TextCtrl(self.panel)
        sizer.Add(self.tc3, pos=(3, 1), span=(1, 1))

        sb = wx.StaticBox(self.panel, label="Please Select Your Gender")
        self.rb_female = wx.RadioButton(self.panel, label="Female")
        self.rb_male   = wx.RadioButton(self.panel, label="Male")
        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        boxsizer.Add(self.rb_female, 
            flag=wx.Center|wx.TOP, border=5)
        boxsizer.Add(self.rb_male,
            flag=wx.Center, border=5)
        sizer.Add(boxsizer, pos=(4, 1), span=(2, 3), 
            flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        button1 = wx.Button(self.panel, label="Ok")
        sizer.Add(button1, pos=(6, 1))
        button1.Bind(wx.EVT_BUTTON, self.ok)

        button2 = wx.Button(self.panel, label="Cancel")
        sizer.Add(button2, pos=(6, 3), span=(1, 1),  
            flag=wx.BOTTOM|wx.RIGHT, border=5)
        button2.Bind(wx.EVT_BUTTON, self.cancel)

        sizer.AddGrowableCol(2)
        
        self.panel.SetSizer(sizer)

    def ok(self, event):
        self.fname = self.tc1.GetValue()
        self.lname = self.tc2.GetValue()
        self.name = '%s %s' %(self.fname.lower(), self.lname.lower())
        try:
            self.age = int(self.tc3.GetValue())
        except:
            self.age = self.tc3.GetValue()
        if self.rb_female.GetValue():
            self.gender = 'female'
        elif self.rb_male.GetValue():
            self.gender = 'male'
        error = ''
        error_flag = False
        if len(self.lname) == 0 or len(self.fname) == 0:
            error = 'please enter your name\n'
            error_flag = True
        if self.age != '':
            if type(self.age) == int:
                if 0 < self.age < 150:
                    pass
                else:
                    error = 'age out of range\n'
                    error_flag = True
            else:
                if self.age != 'unknown':
                    error = 'age should be an integer\n'
                    error_flag = True
                else:
                    self.age = 0
        else:
            error = 'please enter your age\n'
            error_flag = True

        if (not self.rb_female.GetValue()) and (not self.rb_male.GetValue()) :
            error += 'please choose your gender'
            error_flag = True
        if error_flag:
            dlg = wx.MessageDialog(self.panel, error,'', wx.YES_NO | wx.ICON_ERROR)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()          
        else:
            message = 'Is the following infomation correct?\nName: %s\nAge: %s\nGender: %s' %(self.fname+' '+self.lname, self.age, self.gender)
            dlg = wx.MessageDialog(self.panel, message,'Double check the infomation', wx.YES_NO | wx.ICON_INFORMATION)
            result = dlg.ShowModal() == wx.ID_YES
            if result:
                dlg.Destroy()
                self.Destroy()
            else:
                dlg.Destroy()

    def cancel(self, event):
        self.fname = 'Jane'
        self.lname = 'Doe'
        self.name = '%s %s' %(self.fname.lower(), self.lname.lower())
        self.age = 'unknown'
        self.gender = 'unknown'
        message = 'Do you want to use following information?\nName: %s\nAge: %s\nGender: %s' %(self.fname+' '+self.lname, self.age, self.gender)
        dlg = wx.MessageDialog(self.panel, message,'Double check the infomation', wx.YES_NO | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_YES
        if result:
            dlg.Destroy()
            self.Destroy()
        else:
            dlg.Destroy()
        self.fname = ''
        self.lname = ''
        self.tc1.SetValue('')
        self.tc2.SetValue('')
        self.tc3.SetValue('')
        self.rb_female.SetValue(False)
        self.rb_male.SetValue(False)

# if __name__ == '__main__':
#     app = wx.App()
#     ex = Msgbox(None, title="Welcome")
#     app.MainLoop()

