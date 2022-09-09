import os
import json
from pprint import pprint

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_SETTING_PATH = os.path.join(ROOT_DIR, 'server_setting.json')
PRESET_PATH = os.path.join(ROOT_DIR, 'preset.json')

def get_server_id():
    with open(SERVER_SETTING_PATH) as f:
        payload = json.loads(f.read())
        return int(payload['server']['server_id'])


def store_in_root_name(name):
    return os.path.join(ROOT_DIR, name)


def get_fall_2021():
    with open(os.path.join(ROOT_DIR, 'fall_2021.json')) as f:
        data = json.loads(f.read())
        res = []
        for class_name, val in data['classes'].items():
            _, full_name, description = val
            res.append({
                "class_name": class_name,
                "full_name": full_name,
                "description": description
            })
    return res

if __name__ == '__main__':
    pprint(get_fall_2021())