from typing import List
from ciri.post_processing.mechanism.voting import voting

class selection():
    def __init__(self):
        self.selection_machanism = voting()

    def select(self, candidate: List):
        return self.selection_machanism.select(candidate)
