import pandas as pd
import os.path
from openpyxl import load_workbook


class Historylog(object):
    """ save the user's data from furture analysis and comparision.
        different exercises will be record in different sheets
        so far, we have 7 exercises as following.
        #1 : Muscle Tighting Deep Breathing
        #2 : Over The Head Pumping
        #3 : Push Down Pumping
        #4 : Horizontal Pumping
        #5 : Reach to the Sky
        #6 : Shoulder Rolls
        #7 : Clasp and Spread
    """

    def __init__(self):
        self.excelPath = "./output/log.xlsx"

        # record feature
        common = ["name", "age", "gender", "time"]
        backup = ["errmsg"]
        # exercise recoding feature
        brth  = ["mindepth", "maxdepth", "avgdepth"]  # breathing exercise feature
        hs    = ["sync_rate"]                         # hand exercise feature => hand breath sync rate
        shld  = []
        clsp  = []
        swing = []
        # cols title for different exercise sheets
        self.colname = {}
        self.colname[1] = common + brth + backup
        self.colname[2] = common + brth + hs + backup
        self.colname[3] = common + backup
        self.colname[4] = common + backup
        self.colname[5] = common + swing + backup
        self.colname[6] = common + shld + backup
        self.colname[7] = common + clsp + backup
    
    def newlog(self, sheetnum=7):
        """ if there is not log.xlsx exist, create one with sheetnum sheets
            sheetnum depends on howmany exercise we have
        """
        excelWriter = pd.ExcelWriter(self.excelPath, engine='openpyxl')  #create excel file
        for i in xrange(1, sheetnum+1):
            dataframe = pd.DataFrame(columns = self.colname[i])
            if i == 1:
                dataframe.to_excel(excelWriter, 'exercise %s' %i, index=None)
                excelWriter.save()
            else:  # add sheet
                book = load_workbook(excelWriter.path)
                excelWriter.book = book
                dataframe.to_excel(excelWriter, 'exercise %s' %i, index=None)
                excelWriter.save()
            excelWriter.close()

    def addsheet(self, num=1):
        """ adding num new sheet
        """
        excelWriter = pd.ExcelWriter(self.excelPath,engine='openpyxl')
        book = load_workbook(excelWriter.path)
        excelWriter.book = book
        for i in range(num):
            sheetnum = len(book.worksheets)
            dataframe.to_excel(excelWriter, 'exercise %s' %sheetnum+1, index=None)
        excelWriter.save()
        excelWriter.close()        

    def writein(self, userinfo, exerno, time, data=[], errmsg=[]):
        """ write the user record in to log file
            userinfo : the infomation user input in the initial msgbox
            exerno : exercise number
            data : list-like object, which contains vary results depend on the exercise type
            time :  
        """
        if not os.path.isfile(self.excelPath):
            self.newlog()
        excelWriter = pd.ExcelWriter(self.excelPath, engine='openpyxl')
        book = load_workbook(excelWriter.path)
        sheet = book['exercise %s' %exerno]
        date = time.year+time.month+time.day+time.hour+time.minute
        userrecord = [userinfo.name, userinfo.age, user.gender, date] + data + errmsg
        sheet.append(userrecord)
        sheet.save(self.excelPath)
        excelWriter.close()

            


