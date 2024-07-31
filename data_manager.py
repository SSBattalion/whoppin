# data_manager.py
import json
import os

class DataManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load_moderators(self):
        file_path = os.path.join(self.data_dir, 'moderators.json')
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_moderators(self, moderators):
        file_path = os.path.join(self.data_dir, 'moderators.json')
        with open(file_path, 'w') as f:
            json.dump(moderators, f)

    def load_membership(self):
        file_path = os.path.join(self.data_dir, 'membership.json')
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_membership(self, membership):
        file_path = os.path.join(self.data_dir, 'membership.json')
        with open(file_path, 'w') as f:
            json.dump(membership, f)
