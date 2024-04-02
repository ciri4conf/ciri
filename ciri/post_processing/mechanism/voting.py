from typing import List

class voting():
    def select(self, candidate: List) -> List:
        candidate.sort()
        max_count = 0 
        common_element = []
        i = 0
        while i < len(candidate):
            j = i + 1
            while j < len(candidate) and candidate[j] == candidate[i]:
                j += 1
            if j - i > max_count:
                max_count = j - i
                common_element = [candidate[i]]
            elif j - i == max_count:
                common_element.append(candidate[i])
            i = j
        return common_element

