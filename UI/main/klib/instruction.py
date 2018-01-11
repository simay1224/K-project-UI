from collections import defaultdict
import pygame
pygame.init()


class Exeinst(object):
    "Exercise instruxtion"
    def __init__(self):
        self.leftbnd = 0
        # self.pos = defaultdict(lambda: (0, 0))
        self.str = defaultdict(dict)
        self.words = defaultdict(dict)
        self.str['exe'][1] = 'Exercise 1 : Muscle Tighting Deep Breathing'\
                             '\n1. Put your hands on the belly position'\
                             '\n2. Wait until the sign shows "start breath in/out"'
                             '\n3. Do deep breathing 4 times.' \
                             '\n4. Put down your hands.'\
        self.str['exe'][2] = 'Exercise 2 : Clasp and Spread'\
                             '\n  '\
                             '\n1. Raise your hands up and hold there.'\
                             '\n2. Wait until the sign shows "start breath in/out"'\
                             '\n3. Do deep breathing 4 times.' \
                             '\n4. Put down your hands.'\

        self.str['exe'][3] = 'Exercise 3 : Over Head Pumping'\
                             '\n1. Raise your hands up.'\
                             '\n2. Lower your elbows, let shoulder-elbow-hand be a V-shape.'\
                             '\n3. Raise your hands up again.'\
                             '\n4. Repeat this repetition 4 times.'\
                             '\n5. Put down your hands.'
        self.str['exe'][4] = 'Exercise 4 : Push Down Pumping'\
                             '\n1. Raise your hands up till "T-pose"'\
                             '\n2. Move hands slowly to the chest.'\
                             '\n3. Back to "T-pose".'\
                             '\n4. Repeat this repetition 4 times.'\
                             '\n5. Put down your hands.'                             
        

        self.str['note'][1] = 'Notice :'\
                                '\n1. Tight your muscle as much as you can.'\
                                '\n2. Breath as deep as you can.'
        self.str['note'][2] = 'Notice :'\
                                '\n1. When breathing in, you need to close your hands.'\
                                '\n2. When breathing out, you need to open your hands.'\
                                '\n3. Breath as deep as you can.'                              
        self.str['note'][3] = 'Notice :'\
                                '\n1. When you raise up your hands, make sure that your hand, elbow and shoulder are straight.'\
                                '\n2. When bending the elbow, hand-elbow-shoulder should be "V-shape" not "L-shape"'\
 
        self.str['note'][4] = 'Notice :'\
                                '\n1. When doing "T-pose", make sure that your hand, elbow and shoulder are straight'\
                                '\n2. When closing hands, make sure that your hand, and shoulder are in the same height.'\
                                


        self.words['exe'][1] = [word.split(' ') for word in self.str['exe'][1].splitlines()]
        self.words['exe'][2] = [word.split(' ') for word in self.str['exe'][2].splitlines()]
        self.words['exe'][3] = [word.split(' ') for word in self.str['exe'][3].splitlines()]
        self.words['exe'][4] = [word.split(' ') for word in self.str['exe'][4].splitlines()]

        self.words['note'][1] = [word.split(' ') for word in self.str['note'][1].splitlines()]
        self.words['note'][2] = [word.split(' ') for word in self.str['note'][2].splitlines()]
        self.words['note'][3] = [word.split(' ') for word in self.str['note'][3].splitlines()]
        self.words['note'][4] = [word.split(' ') for word in self.str['note'][4].splitlines()]

        self.font_size = 40
        self.font = pygame.font.SysFont('Calibri', self.font_size)
        self.space = self.font.size(' ')[0]  # The width of a space.



    def position(self, surface, ratio, stype=2):
        if stype == 2:
            self.leftbnd = int(surface.get_width()*ratio)
        else:
            self.leftbnd = int(surface.get_width()*(1-ratio))
        return (self.leftbnd, 20)      

    def blit_text(self, surface, exeno, ratio, stype, text=None):

        if text == None:
            words = self.words[exeno]
        else:
            words = [word.split(' ') for word in text.splitlines()] 
       
        if stype == 2:
            max_width = surface.get_width()*(1-ratio)
            max_height = surface.get_height()*ratio
        else:
            max_width = surface.get_width()*ratio
            max_height = surface.get_height()*(1-ratio)            

        # self.screen = pygame.display.set_mode(, pygame.RESIZABLE)

        (x, y) = self.position(surface, ratio, stype)
        x_ori, y_ori = x, y

        for line in words:
            for word in line:
                word_surface = self.font.render(word, 0, pygame.Color('green'))
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width+x_ori:
                    x = x_ori  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + self.space
            x = x_ori  # Reset the x.
            y += word_height  # Start on new row.
        if y > max_height + y_ori:
            if self.font_size > 12:
                self.font_size = self.font_size - 2
                self.font = pygame.font.SysFont('Calibri', self.font_size)

class Evalinst(object):
    "Evaluation instruction"
    def __init__(self):
        self.upperbnd = 0
        self.words = defaultdict(list)

        self.font_size = 60
        self.font = pygame.font.SysFont('Calibri', self.font_size)
        self.space = self.font.size(' ')[0]

    
    def position(self, surface, ratio, stype=2, region=1, height=0):
        if stype == 2:
            self.upperbnd = int(surface.get_height()*ratio + (region-1)*height/4.)
        else:
            self.upperbnd = int(surface.get_height()*(1-ratio) + (region-1)*height/4.)
        return (20, self.upperbnd+20)  

    def blit_text(self, surface, exeno, ratio, stype, text=None, region=1, color='red'):

        if text == None:
            words = self.words[exeno]
        else:
            words = [word.split(' ') for word in text.splitlines()] 
       
        if stype == 2:
            max_width = surface.get_width()*ratio
            height = surface.get_height()*(1-ratio)
        else:
            max_width = surface.get_width()*(1-ratio)
            height = surface.get_height()*ratio           
        max_height = height/4
        # self.screen = pygame.display.set_mode(, pygame.RESIZABLE)

        (x, y) = self.position(surface, ratio, stype, region, height)
        x_ori, y_ori = x, y

        for line in words:
            for word in line:
                word_surface = self.font.render(word, 0, pygame.Color(color))
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width+x_ori:
                    x = x_ori  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + self.space
            x = x_ori  # Reset the x.
            y += word_height  # Start on new row.
        if y > max_height + y_ori:
            if self.font_size > 12:
                self.font_size = self.font_size - 2
                self.font = pygame.font.SysFont('Calibri', self.font_size)