class Hand_status(object):

    def __init__(self):
        pass

    def hstus(self, hstus):
        if (hstus == 2): #Lhand open
            return 'Open'
        elif hstus == 0:
            return 'Unknown'
        elif hstus == 3:
            return 'Closed'
        elif hstus == 4:
            return 'Lasso'
        else:
            return 'Not detect'  

    def htext(self, lhstus, rhstus): 
        lstatus = self.hstus(lhstus)
        rstatus = self.hstus(rhstus)
        return 'Lhand : '+lstatus +'\nRhand : '+rstatus