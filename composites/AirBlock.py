from composites.Block import Block

class AirBlock(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finish()
        self.remove()

    def draw(self):
        pass