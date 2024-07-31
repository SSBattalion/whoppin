import json
import os

class DataManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.moderators_file = os.path.join(data_dir, 'oderators.json')
        self.membership_file = os.path.join(data_dir, 'embership.json')

    def load_moderators(self):
        try:
            with open(self.moderators_file, "r") as file:
                self.moderators = json.load(file)
        except FileNotFoundError:
            self.moderators = []

        # Add default moderators here
        default_moderators = ['alionardo_']
        for mod in default_moderators:
            if mod.lower() not in self.moderators:
                self.moderators.append(mod.lower())
        return self.moderators

    def load_membership(self):
        try:
            with open(self.membership_file, "r") as file:
                self.membership = json.load(file)
        except FileNotFoundError:
            self.membership = []
        return self.membership

    def save_membership(self, membership):
        with open(self.membership_file, "w") as file:
            json.dump(membership, file)

    def save_moderators(self, moderators):
        with open(self.moderators_file, "w") as file:
            json.dump(moderators, file)
