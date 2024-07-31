import json
import os

class DataManager:
    def __init__(self):
        self.data_files = {
            'moderators': 'moderators.json',
            'membership': 'membership.json'
        }

    def load_moderators(self):
        file_path = self.data_files['moderators']
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_moderators(self, moderators):
        file_path = self.data_files['moderators']
        with open(file_path, 'w') as f:
            json.dump(moderators, f)

    def load_membership(self):
        file_path = self.data_files['membership']
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_membership(self, membership):
        file_path = self.data_files['membership']
        with open(file_path, 'w') as f:
            json.dump(membership, f)
