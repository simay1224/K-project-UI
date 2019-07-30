import datetime, sys


class Kparam(object):
    """ Kinect intervention project parameters' initialization
    """

    def __init__(self, exeno='', username=''):
        self.kinect = True
        if sys.platform == "darwin":
            print('D '*100, 'ARWIN')
        
            self.kinect = False

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
        self.c_inst = (0, 90, 115, 255)
        self.c_tips = (106, 57, 0, 0) #was (19, 144, 178, 0)
        # eval part
        self.c_guide     = (0, 90, 106, 255)  #was (0, 90, 115, 255)
        self.c_eval_well = (106, 57, 0, 0)  # was (19, 144, 178, 0)
        self.c_eval_err  = (106, 4, 0, 255) #was (230, 115, 0, 255)
        self.c_stop = (200,4,10,255)
        self.c_togo      = (106, 4, 10, 255) # was (255, 20, 100, 255), now iti smaroon
        # style
        self.s_normal = 'montserrat'
        self.s_emp = 'montserrat'
        self.eval_fs_title = 80 # was 100
        self.eval_fs_guide = 80
        self.eval_fs_msg = 90  #make it bigger, was 70
        self.eval_fs_cnt = 100
        self.inst_size = 40

        if sys.platform == "darwin":
            self.eval_fs_title -= 10
            self.eval_fs_guide -= 10
            self.eval_fs_msg -= 10
            self.eval_fs_cnt -= 10
            self.inst_size -= 10


        #  === UI setting  ===
        #  (based on 1920*1080 setting)
        self.eval_LB = 120  # evaluation Left bound
        self.eval_RB = 980  # evaluation Right bound
        self.video_LB = 1080  # video Left bound
        self.video_RB = 1830  # video Right bound
        # video size 750*420
        self.vid_w = 750
        self.vid_h = 420
        self.vid_w_t = 825  # video width for taining mode
        self.vid_h_t = 462  # video height for taining mode
        self.video1_UB = 110  # video1 upper bound
        self.video2_UB = 560  # video2 upper bound
        #button details
        self.button_w = 200
        self.button_h = 60
        self.button_left1 = self.video_LB
        self.button_dst = 50 #distance between each button
        self.button_left2 = self.button_left1 +  self.button_w + self.button_dst
        self.button_left3 = self.button_left2 +  self.button_w + self.button_dst
        self.button_top = 40

        self.button_right1 = self.button_left1 +self.button_w 
        self.button_right2 = self.button_left2 +self.button_w 
        self.button_right3 = self.button_left3 +self.button_w 

        self.button_bottom = self.button_top + self.button_h 

        self.c_button_play = (106, 83, 0)
        self.c_button_pause = (106, 30, 0)
        self.c_button_stop = (57, 1, 94)
        # eval sections
        self.eval_sec1 = 110
        self.eval_sec2 = 330 -50# was 330
        self.eval_sec3 = 455 - 50 #was 330
        self.eval_sec4 = 835
        self.eval_sec5 = 900
        self.eval_sec6 = 1080
        self.eval_sec = [self.eval_sec1, self.eval_sec2, self.eval_sec3,
                         self.eval_sec4, self.eval_sec5, self.eval_sec6]
