from .klib import bodygame2

# __main__ = "Kinect v2 Body Analysis"
def main():
    game = bodygame2.BodyGameRuntime()
    game.run()