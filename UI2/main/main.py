from .klib import bodygame3

# __main__ = "Kinect v2 Body Analysis"
def main():
    game = bodygame3.BodyGameRuntime()
    game.run()
    return game