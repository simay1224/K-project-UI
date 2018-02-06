from collections import defaultdict
import pygame, pdb
pygame.init()

class Exeinst(object):
    "Exercise instruxtion"
    def __init__(self):
        self.leftbnd = 0
        self.upperbnd = 0
        self.str = defaultdict(dict)
        self.words = defaultdict(dict)
        self.part = [0, 0.5, 5./6, 1]
        self.str['exe'][1] = 'Exercise 1 : Muscle Tighting Deep Breathing'\
                             '\n  '\
                             '\n1. Put your hands on the belly position.'\
                             '\n2. Wait until the sign shows "start breath in/out."'\
                             '\n3. Do deep breathing 4 times.'\
                             '\n4. Put down your hands.'

        self.str['exe'][2] = 'Exercise 2 : Over The Head Pumping'\
                             '\n  '\
                             '\n1. Raise your hands up and hold there.'\
                             '\n2. Wait until the sign shows "start breath in/out."'\
                             '\n3. Do deep breathing 4 times.' \
                             '\n4. Put down your hands.'

        self.str['exe'][3] = 'Exercise 3 : Push Down Pumping'\
                             '\n  '\
                             '\n1. Raise your hands up.'\
                             '\n2. Lower your elbows, let shoulder-elbow-hand be a V-shape.'\
                             '\n3. Raise your hands up again.'\
                             '\n4. Repeat this repetition 4 times.'\
                             '\n5. Put down your hands.'

        self.str['exe'][4] = 'Exercise 4 : Horizontal Pumping'\
                             '\n  '\
                             '\n1. Raise your hands up till "T-pose."'\
                             '\n2. Move hands slowly to the chest.'\
                             '\n3. Back to "T-pose".'\
                             '\n4. Repeat this repetition 4 times.'\
                             '\n5. Put down your hands.'

        self.str['exe'][5] = 'Exercise 5 : Clasp and Spread'\
                             '\n  '\
                             '\n1. Raise and clasp your hands till the belly position.'\
                             '\n2. Raise clasped hands toward to your forehead\
                                   and keep elbows together.'\
                             '\n3. Slide your heands to the back of your\
                                   head and spread the elbows open wide.'\
                             '\n4. Back to the belly position.'\
                             '\n5. Repeat 4 times.'\
                             '\n6. Put down your hands.'


        self.str['exe'][6] = 'Exercise 6 : Shoulder Rolls'\
                             '\n  '\
                             '\n1. Put your hands on the belly position.'\
                             '\n2. Rotate you shoulder.'\
                             '\n3. Repeat 4 times.'\
                             '\n4. Put down your hands'

        
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

        self.str['note'][5] = 'Notice :'\
                                '\n1. When raising the hands to the forehead, keeping two elbows as close as possible.'\
                                '\n2. When the hands is in the back of your head, spread the elnows open as wide as possible.'\
                                '\n3. Keep your body staight.'

        self.str['note'][6] = 'Notice :'\
                                '\n1. Let your shoulders rotation movement as large as possible.'



        self.words['exe'][1] = [word.split(' ') for word in self.str['exe'][1].splitlines()]
        self.words['exe'][2] = [word.split(' ') for word in self.str['exe'][2].splitlines()]
        self.words['exe'][3] = [word.split(' ') for word in self.str['exe'][3].splitlines()]
        self.words['exe'][4] = [word.split(' ') for word in self.str['exe'][4].splitlines()]
        self.words['exe'][5] = [word.split(' ') for word in self.str['exe'][5].splitlines()]
        self.words['exe'][6] = [word.split(' ') for word in self.str['exe'][6].splitlines()]
        #self.words['exe'][7] = [word.split(' ') for word in self.str['exe'][7].splitlines()]

        self.words['note'][1] = [word.split(' ') for word in self.str['note'][1].splitlines()]
        self.words['note'][2] = [word.split(' ') for word in self.str['note'][2].splitlines()]
        self.words['note'][3] = [word.split(' ') for word in self.str['note'][3].splitlines()]
        self.words['note'][4] = [word.split(' ') for word in self.str['note'][4].splitlines()]
        self.words['note'][5] = [word.split(' ') for word in self.str['note'][5].splitlines()]
        self.words['note'][6] = [word.split(' ') for word in self.str['note'][6].splitlines()]
        # self.words['note'][7] = [word.split(' ') for word in self.str['note'][7].splitlines()]

        self.font_size = 40
        self.font = pygame.font.SysFont('Calibri', self.font_size)
        self.space = self.font.size(' ')[0]  # The width of a space.

    def position(self, surface, ratio, stype=2, region=1, height=0):
        """According to the scene type, ratio and the region number
           set up different upper bound and lower bound to the text"""
        if stype == 2:
            self.leftbnd = int(surface.get_width()*ratio)
            self.upperbnd = height*self.part[region-1]
        else:
            self.leftbnd = int(surface.get_width()*(1-ratio))
            self.upperbnd = height*self.part[region-1]
        return (self.leftbnd, self.upperbnd + 20)

    def blit_text(self, surface, exeno, ratio, stype, strtype='exe', text=None, region=1, color=(0, 255, 0, 255)):
        """Creat a text surface, this surface will change according to the scene type,
           ratio and the region number. According to the size of the surface, the text 
           will auto change line also auto change the font size"""

        if text == None:  # if there is no assign text, use the text in data base 
            words = self.words[strtype][exeno]
        else:
            words = [word.split(' ') for word in text.splitlines()]

        if stype == 2:  # avatar in upper-left, color frame in lower-right
            max_width = surface.get_width()*(1-ratio)
            height = surface.get_height()*ratio
        else:
            max_width = surface.get_width()*ratio
            height = surface.get_height()*(1-ratio)
        max_height = height*self.part[region]

        (x, y) = self.position(surface, ratio, stype, region, height)
        x_ori, y_ori = x, y

        for line in words:
            for word in line:
                word_surface = self.font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width+x_ori:
                    x = x_ori  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + self.space
            x = x_ori  # Reset the x.
            y += word_height  # Start on new row.

        if y > max_height + y_ori:  # change font size if it is out of the boundary
            print 'large'
            if self.font_size > 12:
                self.font_size = self.font_size - 2
                self.font = pygame.font.SysFont('Calibri', self.font_size)
        elif y < max_height  - 40 :
            print 'small'
            if self.font_size < 40:
                self.font_size = self.font_size + 2
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
        """According to the scene type, ratio and the region number
           set up different upper bound and lower bound to the text"""

        if stype == 2:
            self.upperbnd = int(surface.get_height()*ratio + (region-1)*height/4.)
        else:
            self.upperbnd = int(surface.get_height()*(1-ratio) + (region-1)*height/4.)
        return (20, self.upperbnd+20)

    def blit_text(self, surface, exeno, ratio, stype, text=None, region=1, color=(255, 0, 0, 255)):
        """Creat a text surface, this surface will change according to the scene type,
           ratio and the region number. According to the size of the surface, the text 
           will auto change line also auto change size"""

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

        (x, y) = self.position(surface, ratio, stype, region, height)
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
            x = x_ori  # Reset the x.
            y += word_height  # Start on new row.
        if y > max_height + y_ori:
            if self.font_size > 12:
                self.font_size = self.font_size - 2
                self.font = pygame.font.SysFont('Calibri', self.font_size)
            