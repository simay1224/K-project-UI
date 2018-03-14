import pandas as pd
from openpyxl import load_workbook, Workbook 
from xlrd import open_workbook
import sys

class Historylog(object):
    """ save the user's data from furture analysis and comparision
    """
    def __init__(self):
        self.excelPath = "./output/log.xlsx"
        self.excelWriter = pd.ExcelWriter(self.excelPath,engine='openpyxl')  #create excel file
        self.exersubset = 7
        self.colname = {}
        self.colname[1] = ["name", "time", "error"]
        self.colname[2] = ["name", "time", "error"]
        self.colname[3] = ["name", "time", "error"]
        self.colname[4] = ["name", "time", "error"]
        self.colname[5] = ["name", "time", "error"]
        self.colname[6] = ["name", "time", "error"]
        self.colname[7] = ["name", "time", "error"]
    
    def newlog(self, sheetnum=self.exersubset):
        """ if there is not log.xlsx exist, create one with sheetnum sheets
            sheetnum depends on howmany exercise we have
        """
        for i in xrange(1, sheetnum+1):
            dataframe = pd.DataFrame(columns = colname[i])
            if i == 1:
                dataframe.to_excel(excelWriter, 'exercise %s' %i, index=None)
                excelWriter.save()
                excelWriter.close()
            else:  # add sheet
                book = load_workbook(excelWriter.path)
                excelWriter.book = book
                dataframe.to_excel(excelWriter, 'exercise %s' %i, index=None)
                excelWriter.close()

    def addsheet(self, newexerno=[]):
        self.excelWriter=pd.ExcelWriter(self.excelPath,engine='openpyxl')
        for i in newexerno:
            if i > self.exersubset:
                book = load_workbook(excelWriter.path)
                excelWriter.book = book
                dataframe.to_excel(excelWriter, 'exercise %s' %i, index=None)
            else:
                print('already exist this exercise no')
        excelWriter.close()        

    def writein(self, userinfo, exeno, data):

