import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf

class Evaluation(object):
    def __init__(self):
        pass

    def run(self, exeno, brth, err=[]):
        """ exercise performance evaluation
        """
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        if exeno == 1:       
            ax.plot(gf(brth.breath_list, 10), color='g')
            if len(brth.ngframe) != 0:
                for i in brth.ngframe:
                    y1 = brth.breath_list[i]
                    if y1 < 15000:
                        y2 = y1+10000
                    else:
                        y2 = y1-10000    
                    ax.annotate('Not deep breath', xy=(i, y1+10), xytext=(i, y2), arrowprops=dict(facecolor='red', shrink=0.05),)
            plt.title('Breath in and out')
            fig.savefig('output/bio_1.jpg')
        # elif exeno == 2:
        #     ax.plot(self.hstate[:,0]*20000, color='b')
        #     ax.plot(self.hstate[:,1]*20000-20000, color='r')
        #     # ax.plot(gf(self.breath_list, 10)/self.breath_list[0]*2, color='g')
        #     ax.plot(gf(self.breath_list, 10), color='g')
        #     if len(self.ngframe) != 0:
        #         for i in self.ngframe:
        #             y1 = self.breath_list[i]#/self.breath_list[0]*2
        #             y2 = 1.5*10000
        #             ax.annotate('breath not deep enough', xy=(i, y1), xytext=(i, y2),arrowprops=dict(facecolor='red', shrink=0.05),)
        #     if len(self.missingbreath) != 0:
        #         for i in self.missingbreath:
        #             x = sum(i)/2
        #             y1 = self.breath_list[x]#/self.breath_list[0]*2 
        #             y2 = 1*10000
        #             ax.annotate('missing breath', xy=(x, y1), xytext=(x, y2),arrowprops=dict(facecolor='green', shrink=0.05),)

        #     plt.title('Breath in and out & hands open and close')
        #     fig.savefig('output/biohoc.jpg')
        #     plt.show()
            # pdb.set_trace()
        plt.close(fig)

        print('\nevaluation:')
        if len(err) != 0:
            for i in err:
                print i
            print('\n')
        else:
            print('perfect !!\n')
