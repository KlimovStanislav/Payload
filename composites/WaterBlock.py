from composites.Block import Block

class WaterBlock(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finish()