import json
import os

class DataManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.directory = os.path.dirname(self.file_path)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)  # Initialize an empty JSON object

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_data(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    def save_membership(self, membership):
        data = self.load_data()
        data['membership'] = membership
        self.save_data(data)

    def load_membership(self):
        data = self.load_data()
        return data.get('membership', [])
