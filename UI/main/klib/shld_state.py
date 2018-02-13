class Shld_statue(object):
    """ detect the shoulder state.
        So far, we detect 1. shoulder rotate 2. shoulder up-and-down. 
    """

    def __init__(self):
        self.cnt = 0
        self.fcnt = 0
        self.ignore = 30  # ignore first XX frames
        self.range = 50   # find local min max within this range
        self.cycle = False
        self.flag = True
        self.type = 0
        self.lylist = []
        self.ldlist = []
        self.rylist = []
        self.rdlist = []        

    def findtops(self, bdimg, shld, bdidx):
        """ find the shoulder top. 
            (currently close this function, 
             if wnat to open need to input bodyidx data.)
        """
        return np.where(bdimg[:shld[1], shld[0]] != bdidx)[0][::-1][0]+1

    def findminmax(self, data, rng=50, start=0, ignore=10, dtype='height'):
        """ find local min & max. 
        """
        foo = argrelextrema(gf(data, 5), np.less_equal, order=rng)[0]
        vall = foo[np.where((np.roll(foo, 1)-foo) != -1)[0]]
        vall = vall[vall >= ignore][start:]
        foo = argrelextrema(gf(data, 5), np.greater_equal, order=rng)[0]
        peak = foo[np.where((np.roll(foo, 1)-foo) != -1)[0]]
        peak = peak[peak >= ignore][start:]
        if dtype == 'height':
            return [peak, vall]
        elif dtype == 'depth':
            peakvalue = gf(data, 5)[peak]
            vallvalue = gf(data, 5)[vall]
            return [peak, vall, peakvalue, vallvalue]

    def chkdepth(self, peak, vall, th=30):
        """ check the depth change in this cycle
            if too small => shlder up-and-down.
        """
        if (peak[0]-vall[0]) > th:
            return True
        else:
            return False

    def findcycle(self, y, z, trig=0):
        """ check the shlder motion sequence to find out whrther
            the user finish one cycle.
        """
        if (max(len(y[0]), len(y[1]), len(z[0]), len(z[1])) \
            - min(len(y[0]), len(y[1]), len(z[0]), len(z[1]))) > 1:
            return 0 

        num = (len(y[0])+len(y[1])+len(z[0])+len(z[1])-1)/4

        if num > 0:
            chk = chkdepth(z[2], z[3])
            if chk:
                return 1  # shlder roll
            else:
                return 2  # up-and-down
        else:
            return 0  # not a cycle
    
    def statechk(self, ylist, dlist):
        """ check shoulder is 1. rotate 2. up and down.
        """
        y = self.findminmax(ylist, self.rng, self.cnt, ignore=self.ign, dtype='height')
        z = self.findminmax(dlist, self.rng, self.cnt, ignore=self.ign, dtype='depth')        
        if len(y[0]) and len(y[1]) and len(z[0]) and len(z[1]) and self.flag:
            self.flag = False
            self.ign = min(y[0][0], y[1][0], z[0][0], z[1][0])
        self.type = self.findcycle(y, z)

        if self.type == 1:
            self.cnt += self.type  # cycle number
            self.type = 0
        elif self.type == 2:
            print('simple up and down')
            self.type = 0
            pass
        else:
            pass

    def run(self, depth, joints):
        self.fcnt += 1
        lshld = [int(joints[4].x), int(joints[4].y)]
        rshld = [int(joints[8].x), int(joints[8].y)]  

        self.lylist.append(lshld[1])
        self.ldlist.append(depth[lshld[1], lshld[0]])
        self.rylist.append(rshld[1])
        self.rdlist.append(depth[rshld[1], rshld[0]])
        if (self.fcnt >= 50) and (self.fcnt%20 == 0):
            self.statechk(lylist, ldlist)
            #self.statechk(rylist, rdlist)