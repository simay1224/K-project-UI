import pygame,pdb

FPS = 30

pygame.init()
pygame.mixer.quit()
clock = pygame.time.Clock()
movie = pygame.movie.Movie('./video/ex2.mpg')
screen = pygame.display.set_mode(movie.get_size())
# movie_screen = pygame.Surface(movie.get_size()).convert()
movie_screen = pygame.Surface((1280,960)).convert()
movie.set_display(movie_screen)
movie.play()

playing = True
while playing:

    if pygame.key.get_focused():
        press = pygame.key.get_pressed()
        if press[114] == 1: # use 'r' to 
            print '3'
            movie.stop()
            del movie
            movie = pygame.movie.Movie('./video/ex3.mpg')
            screen = pygame.display.set_mode(movie.get_size())
            movie_screen = pygame.Surface((1280,960)).convert()
            movie.set_display(movie_screen)
            # movie.rewind()
            movie.play()
        if press[115] == 1: # use 's' to 
            print '2'
            movie.stop()
            del movie
            movie = pygame.movie.Movie('./video/ex2.mpg')
            screen = pygame.display.set_mode(movie.get_size())
            movie_screen = pygame.Surface((1280,960)).convert()
            movie.set_display(movie_screen)
            # movie.rewind()
            movie.play()
        if press[113] == 1: # use 'q' to
           print 'rewind' 
           movie.stop()          
           movie.rewind() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            movie.stop()
            del movie
            playing = False

    screen.blit(movie_screen,(0,0))
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()