from typing import List

class BasePool(List):
    def __init__(self, max_len: int):
        super().__init__()
        self.cur_len = 0
        self.max_len = max_len
        self.full_status = False
        self.pool = []

    def add(self, input):
        if self.full_status == True:
            return False
        self.pool.append(input)
        self.cur_len += 1
        if self.cur_len == self.max_len:
            self.full_status = True
        return True
