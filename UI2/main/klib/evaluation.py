import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf
from collections import defaultdict
import pygame


class Evaluation(object):
    def __init__(self):
        self.upperbnd = 0
        self.words = defaultdict(list)
        self.font_size = 60
        self.font = pygame.font.SysFont('Calibri', self.font_size)
        self.space = self.font.size(' ')[0]

    def run(self, exeno, brth, hs, errs=[]):
        """ exercise performance evaluation
        """
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        if len(brth.breath_list) == 0:
            if len(hs.hstate) == 0:
                pass  # did not do hand and breathe test
            else:  # only did hand test
                pass
        else:  # did breath test
            if len(hs.hstate) == 0:  # only did breathe test (i.e. exer 1)
                ax.plot(gf(brth.breath_list, 5), color='g')
                if len(brth.ngframe) != 0:
                    for i in brth.ngframe:
                        y1 = brth.breath_list[i]
                        y2 = y1 - 20
                        # if y1 < 0:
                        #     y2 = y1+10
                        # else:
                        #     y2 = y1-10    
                        ax.annotate('Not deep breath', xy=(i, y1-2), xytext=(i, y2),\
                                    arrowprops=dict(facecolor='red', shrink=0.05),)
                plt.title('Breath in and out')
                fig.savefig('output/Exer'+str(exeno)+'_bio_1.jpg')                
            else:  # did both hand and breath test (i.e. exer 2)
                ax.plot(hs.hstate[:, 0]*15, color='b')
                ax.plot(hs.hstate[:, 1]*15-20, color='r')
                # ax.plot(gf(self.breath_list, 10)/self.breath_list[0]*2, color='g')
                ax.plot(gf(brth.breath_list, 5), color='g')
                if len(brth.ngframe) != 0:
                    for i in brth.ngframe:
                        y1 = brth.breath_list[i]#/self.breath_list[0]*2
                        y2 = 1.5*10
                        ax.annotate('breath not deep enough', xy=(i, y1), xytext=(i, y2),\
                                    arrowprops=dict(facecolor='red', shrink=0.05),)
                if len(brth.missingbreath) != 0:
                    for i in brth.missingbreath:
                        x = sum(i)/2
                        y1 = brth.breath_list[x]#/self.breath_list[0]*2 
                        y2 = 1*10
                        ax.annotate('missing breath', xy=(x, y1), xytext=(x, y2),\
                                    arrowprops=dict(facecolor='green', shrink=0.05),)
                plt.title('Breath in and out & hands open and close')
                fig.savefig('output/Exer'+str(exeno)+'_biohoc_1.jpg')        
        plt.close(fig)

    def errmsg(self, errs=[], dolist=None, contents=['Breath eval', 'Hand eval', 'Exercise motion', 'Shoulder State', 'Clasp & Spread', 'Swing']):
        print('\nevaluation:\n')
        for idx, err in enumerate(errs):
            if len(err) != 0:
                for text in set(err):
                    print (('%18s' % contents[idx])+' : '+text)
                    print('\n')
            elif dolist[idx]:  # done without err
                print(('%18s' % contents[idx])+' : Perfect !!')
            else:
                print(('%18s' % contents[idx])+' : Did not test this part.')

    def position(self, surface, ratio, stype=2, region=1, height=0):
        """According to the scene type, ratio and the region number
           set up different upper bound and lower bound to the text"""

        if stype == 2:
            self.upperbnd = int(surface.get_height()*ratio + (region-1)*height/4.)
        else:
            self.upperbnd = int(surface.get_height()*(1-ratio) + (region-1)*height/4.)
        return (20, self.upperbnd+20)

    def blit_text(self, surface, exeno, kp, text=None, region=1, color=(255, 0, 0, 255)):
        """Creat a text surface, this surface will change according to the scene type,
           ratio and the region number. According to the size of the surface, the text 
           will auto change line also auto change size"""

        if text == None:
            words = self.words[exeno]
        else:
            words = [word.split(' ') for word in text.splitlines()]

        if kp.scene_type == 2:
            max_width = surface.get_width()*kp.ratio
            height = surface.get_height()*(1-kp.ratio)
        else:
            max_width = surface.get_width()*(1-kp.ratio)
            height = surface.get_height()*kp.ratio
        max_height = height/4

        (x, y) = self.position(surface, kp.ratio, kp.scene_type, region, height)
        x_ori, y_ori = x, y

        for line in words:
            for word in line:
                word_surface = self.font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width+x_ori:  # change line(row)
                    x = x_ori  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + self.space
            x = x_ori  # Reset the x
            y += word_height  # Start on new row.
        if y > max_height + y_ori:
            if self.font_size > 12:
                self.font_size = self.font_size - 2
                self.font = pygame.font.SysFont('Calibri', self.font_size)           
                


