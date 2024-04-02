import os
import random
from pathlib import Path
from typing import Dict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ciri.ciri_logger import logger


class ShotSelection:
    """
    Class to handle shot selection based on various methods.
    """

    def __init__(
        self,
        args: Dict,
        input_file_content: str,
    ):
        self.system = args.system
        self.selection_method = args.shot_selection
        self.validconfig_shot_num = args.validconfig_shot_num
        self.misconfig_shot_num = args.misconfig_shot_num
        self.input_file_content = input_file_content

        # Define base path for shot selections
        cur_file_path = os.path.dirname(os.path.abspath(__file__))
        self.shot_pool_path = Path(cur_file_path, "shot_pool", self.system)
        self.total_shot_num = len(os.listdir(os.path.join(self.shot_pool_path, "erroneous")))

        # Mapping of selection methods to their respective functions
        self.selection_methods = {
            "random": self._random_shot_selection,
            "category": self._diff_category_selection,
            "similarity": self._similarity_selection,
            "category+similarity": self._category_similarity,
        }

        # Shot number dictionary for each category and system 
        self.shot_num_dict = {
            "hcommon": {
                "syntax": [1, 2, 3, 4, 5, 6, 7],
                "range": [8, 9, 10, 11, 12, 13],
                "dependency": [14, 15],
                "version": [16],
            },
            "hbase": {
                "syntax": [1, 2, 3, 4],
                "range": [5, 6, 7, 8, 9],
                "dependency": [10, 11],
                "version": [12],
            },
            "alluxio": {
                "syntax": [1, 2, 3, 4, 5],
                "range": [6, 7, 8, 9, 10],
                "dependency": [11, 12],
                "version": [13],
            },
            "hdfs": {
                "syntax": [1, 2, 3, 4, 5, 6, 7],
                "range": [8, 9, 10, 11, 12, 13],
                "dependency": [14, 15],
                "version": [16],
            },
            "yarn": {
                "syntax": [1, 2, 3],
                "range": [4, 5, 6, 7],
                "dependency": [8, 9],
                "version": [10],
            },
            "zookeeper": {
                "syntax": [1, 2, 3, 4],
                "range": [5, 6, 7, 8],
            },
            "redis": {
                "syntax": [1, 2, 3, 4, 5],
                "range": [6, 7, 8, 9, 10],
                "dependency": [11],
                "version": [12],
            },
            "postgresql": {
                "syntax": [1, 2, 3],
                "range": [4, 5],
                "dependency": [6, 7],
                "version": [8],
            },
            "etcd": {
                "syntax": [1, 2, 3],
                "range": [4, 5, 6],
                "dependency": [7],
                "version": [8],
            },
            "django": {
                "syntax": [1, 2, 3],
                "range": [4, 5],
                "version": [6],
            },
        }

    def select(self):
        """Main method to select the shot based on the selection method."""
        shot_content = []

        # Select erroneous shots
        if self.misconfig_shot_num:
            selection_func = self.selection_methods.get(self.selection_method)
            if not selection_func:
                raise ValueError(
                    f"Invalid shot selection method {self.selection_method}"
                )
            shot_list = selection_func()
            shot_content.append(self._get_shot_content("erroneous", shot_list))
            logger.info(f"Wrong shot number:\n{shot_list}\n")

        # Select correct shots
        if self.validconfig_shot_num:
            shot_list = self._correct_shot_selection()
            shot_content.append(self._get_shot_content("correct", shot_list))
            logger.info(f"Correct shot number:\n{shot_list}\n")
            
        shot_content_str = "\n".join(shot_content) + "\n"
        logger.debug(f"[Ciri] Shot content: \n{shot_content_str}")
        return shot_content_str

    def _get_shot_content(self, shot_type: str, shot_list: list) -> str:
        """Retrieve shot content based on the shot type and shot list."""
        shot_file_list = [
            Path(os.path.join(self.shot_pool_path, f"{shot_type}/{shot}")).read_text()
            for shot in shot_list
        ]
        return "\n".join(shot_file_list)

    def _random_shot_selection(self):
        """Select shots randomly."""
        return random.sample(
            range(1, self.total_shot_num + 1), self.misconfig_shot_num
        )

    def _diff_category_selection(self):
        """Selects shots from different categories."""
        
        # We have four category with the shot number
        if self.misconfig_shot_num > 4:
            raise ValueError(
                "Sorry, for diff category selection we only support at most 4 shot"
            )
        selected_category = random.sample(
            list(self.shot_num_dict[self.system].keys()), self.misconfig_shot_num
        )
        # Sample a shot from each selected category
        shot_list = [random.choice(self.shot_num_dict[self.system][category]) for category in selected_category]
        return shot_list

    def _similarity_selection(self):
        """Selects shots based on their similarity."""
        most_similar_shot = self._similarity_sorted_selection(
            1, self.total_shot_num
        )
        random.shuffle(most_similar_shot)
        return most_similar_shot

    def _category_similarity(self):
        """Selects shots from different categories, if multiple shots in a category, select the most similar one."""
        if self.misconfig_shot_num > 4:
            raise ValueError(
                "Sorry, for diff category and similarity selection \
                        we only support at most 4 shot"
            )
        selected_category = random.sample(
            list(self.shot_num_dict[self.system].keys()), self.misconfig_shot_num
        )
        shot_list = []
        for category in selected_category:
            begin = self.shot_num_dict[self.system][category][0]
            end = self.shot_num_dict[self.system][category][-1]
            shot_list.extend(self._similarity_sorted_selection(begin, end, 1))
        random.shuffle(shot_list)
        return shot_list

    def _similarity_sorted_selection(self, begin, end, num=None):
        if num is None:
            num = self.misconfig_shot_num
        shot_file_list = [
            Path(os.path.join(self.shot_pool_path, f"erroneous/{i}")).read_text()
            for i in range(begin, end + 1)
        ]
        count_vectorizer = CountVectorizer(stop_words="english")
        count_matrix = count_vectorizer.fit_transform(
            [self.input_file_content] + shot_file_list
        )
        similarity = cosine_similarity(count_matrix[0:1], count_matrix[1:])
        most_similar_shot = list(similarity.argsort()[0][::-1][:num] + begin)
        most_similar_shot.reverse()
        return most_similar_shot

    def _correct_shot_selection(self):
        """Randomly selects correct shots."""
        return random.sample(
            range(1, self.total_shot_num + 1), self.validconfig_shot_num
        )

