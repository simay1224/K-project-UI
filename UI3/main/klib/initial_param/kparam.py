import datetime


class Kparam(object):
    """ Kinect intervention project parameters' initialization 
    """

    def __init__(self,exeno='', username=''):

        self.bdjoints   = []
        self.now  = datetime.datetime.now() 
        self.dstr = './output/'+username+'data'+repr(self.now.year)+repr(self.now.month).zfill(2)\
                               +repr(self.now.day).zfill(2)+repr(self.now.hour).zfill(2)\
                               +repr(self.now.minute).zfill(2)+repr(self.now.second).zfill(2)+str(exeno)
        self.scale       = 1.0
        self.scene_type  = 2
        self.pre_scale   = 1.0  
        self.ini_scale   = 1.0
        self.ratio       = 0.5  # propotion of avatar and color frame
        self._done       = False
        self.finish      = False
        self.handmode    = False
        self.vid_rcd     = False
        self.model_draw  = False
        self.model_frame = False
        self.clipNo      = 0
        self.fno         = 0 
        self.framecnt    = 0

        # === Font setting ===
        # color
        # instruction part
        self.c_inst = (107, 71, 107, 255)
        self.c_tips = (45, 89, 134, 0)
        # eval part
        self.c_guide     = (107, 71, 107, 255)
        self.c_eval_well = (45, 89, 134, 0)
        self.c_eval_err  = (230, 115, 0, 255)
        self.c_togo      = (107, 71, 107, 255)
        # style
        self.s_normal = 'Arial'
        self.s_emp = 'Arial'
        self.eval_size = 80
        self.inst_size = 40


                  




