from composites.StaticBlock import StaticBlock
import random

class RandomRotateBlock(StaticBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finish()

    def draw(self):
        super().draw()
        self.pixmap_item.setRotation(random.choice([0, 90, 180, 270]))