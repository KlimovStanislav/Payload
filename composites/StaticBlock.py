from composites.Block import Block

class StaticBlock(Block):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def remove(self):
        self.exists = False
        self.w.remove_static_block(self)

    def finish(self):
        self.draw()
        self.w.append_static_block(self)