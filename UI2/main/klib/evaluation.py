import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d as gf

class Evaluation(object):
    def __init__(self):
        pass

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
                ax.plot(gf(brth.breath_list, 10), color='g')
                if len(brth.ngframe) != 0:
                    for i in brth.ngframe:
                        y1 = brth.breath_list[i]
                        if y1 < 15000:
                            y2 = y1+10000
                        else:
                            y2 = y1-10000    
                        ax.annotate('Not deep breath', xy=(i, y1+10), xytext=(i, y2),\
                                    arrowprops=dict(facecolor='red', shrink=0.05),)
                plt.title('Breath in and out')
                fig.savefig('output/Exer'+str(exeno)+'_bio_1.jpg')                
            else:  # did both hand and breath test (i.e. exer 2)
                ax.plot(hs.hstate[:, 0]*20000, color='b')
                ax.plot(hs.hstate[:, 1]*20000-20000, color='r')
                # ax.plot(gf(self.breath_list, 10)/self.breath_list[0]*2, color='g')
                ax.plot(gf(brth.breath_list, 10), color='g')
                if len(brth.ngframe) != 0:
                    for i in brth.ngframe:
                        y1 = brth.breath_list[i]#/self.breath_list[0]*2
                        y2 = 1.5*10000
                        ax.annotate('breath not deep enough', xy=(i, y1), xytext=(i, y2),\
                                    arrowprops=dict(facecolor='red', shrink=0.05),)
                if len(brth.missingbreath) != 0:
                    for i in brth.missingbreath:
                        x = sum(i)/2
                        y1 = brth.breath_list[x]#/self.breath_list[0]*2 
                        y2 = 1*10000
                        ax.annotate('missing breath', xy=(x, y1), xytext=(x, y2),\
                                    arrowprops=dict(facecolor='green', shrink=0.05),)
                plt.title('Breath in and out & hands open and close')
                fig.savefig('output/Exer'+str(exeno)+'_biohoc_1.jpg')        
        plt.close(fig)



        # if exeno == 1:       
        #     ax.plot(gf(brth.breath_list, 10), color='g')
        #     if len(brth.ngframe) != 0:
        #         for i in brth.ngframe:
        #             y1 = brth.breath_list[i]
        #             if y1 < 15000:
        #                 y2 = y1+10000
        #             else:
        #                 y2 = y1-10000    
        #             ax.annotate('Not deep breath', xy=(i, y1+10), xytext=(i, y2),\
        #                          arrowprops=dict(facecolor='red', shrink=0.05),)
        #     plt.title('Breath in and out')
        #     fig.savefig('output/bio_1.jpg')
        # elif exeno == 2:
        #     ax.plot(hs.hstate[:, 0]*20000, color='b')
        #     ax.plot(hs.hstate[:, 1]*20000-20000, color='r')
        #     # ax.plot(gf(self.breath_list, 10)/self.breath_list[0]*2, color='g')
        #     ax.plot(gf(brth.breath_list, 10), color='g')
        #     if len(brth.ngframe) != 0:
        #         for i in brth.ngframe:
        #             y1 = brth.breath_list[i]#/self.breath_list[0]*2
        #             y2 = 1.5*10000
        #             ax.annotate('breath not deep enough', xy=(i, y1), xytext=(i, y2),\
        #                          arrowprops=dict(facecolor='red', shrink=0.05),)
        #     if len(brth.missingbreath) != 0:
        #         for i in brth.missingbreath:
        #             x = sum(i)/2
        #             y1 = brth.breath_list[x]#/self.breath_list[0]*2 
        #             y2 = 1*10000
        #             ax.annotate('missing breath', xy=(x, y1), xytext=(x, y2),\
        #                          arrowprops=dict(facecolor='green', shrink=0.05),)

        #     plt.title('Breath in and out & hands open and close')
        #     fig.savefig('output/biohoc_1.jpg')
        #     plt.show()
        #     # pdb.set_trace()
        # plt.close(fig)

    def errmsg(self, errs=[], dolist=None, contents=['breath eval', 'hand eval', 'exercise motion']):
        print('\nevaluation:\n')
        for idx, err in enumerate(errs):
            if len(err) != 0:
                for text in set(err):
                    print (contents[idx]+' : '+text)
                    print('\n')
            elif dolist[idx]:  # done without err
                print(contents[idx]+' : perfect !!')
            else:
                print(contents[idx]+' : did not test this part.')
            
                


