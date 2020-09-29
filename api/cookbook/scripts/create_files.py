import json
import os
import sys

COLORS = [
    "black",
    "blue",
    "brown",
    "cyan",
    "gray",
    "green",
    "light_blue",
    "light_gray",
    "lime",
    "magenta",
    "orange",
    "pink",
    "purple",
    "red",
    "white",
    "yellow"
]

CURR_DIR = os.path.dirname(sys.argv[0])
ITEM_FILE_TPL = './templates/recipes/item.json'
ITEM_FILE_PATH = os.path.join(CURR_DIR, ITEM_FILE_TPL)

TAG_FILE_TPL = './templates/tags/item.json'
TAG_FILE_PATH = os.path.join(CURR_DIR, TAG_FILE_TPL)

def create_concrete_recipes():
    tpl_json = None
    with open(ITEM_FILE_PATH, 'r') as file:
        tpl_contents = file.read()
        tpl_json = json.loads(tpl_contents)

    for color in COLORS:
        item = f'{color}_concrete'

        item_json = tpl_json.copy()
        item_json['type'] = 'cookbook:game_mechanic'
        item_json['name'] = item
        item_json['ingredients'] = [
            f'minecraft:{color}_concrete_powder',
            'minecraft:water'
        ]
        item_json['result']['item'] = f'minecraft:{item}'

        output_file = f'./outputs/recipes/{item}.json'
        output_path = os.path.join(CURR_DIR, output_file)
        with open(output_path, "w") as write_file:
            json.dump(item_json, write_file, indent=2)

def create_concrete_tag():
    tpl_json = None
    with open(TAG_FILE_PATH, 'r') as file:
        tpl_contents = file.read()
        tpl_json = json.loads(tpl_contents)

    tag_values = []
    for color in COLORS:
        item = f'minecraft:{color}_concrete'
        tag_values.append(item)

    tag_json = tpl_json.copy()
    tag_json['values'] = tag_values

    output_file = f'./outputs/tags/concrete.json'
    output_path = os.path.join(CURR_DIR, output_file)
    with open(output_path, "w") as write_file:
        json.dump(tag_json, write_file, indent=2)

def create_concrete_powder_tag():
    tpl_json = None
    with open(TAG_FILE_PATH, 'r') as file:
        tpl_contents = file.read()
        tpl_json = json.loads(tpl_contents)

    tag_values = []
    for color in COLORS:
        item = f'minecraft:{color}_concrete_powder'
        tag_values.append(item)

    tag_json = tpl_json.copy()
    tag_json['values'] = tag_values

    output_file = f'./outputs/tags/concrete_powder.json'
    output_path = os.path.join(CURR_DIR, output_file)
    with open(output_path, "w") as write_file:
        json.dump(tag_json, write_file, indent=2)

def create_terracotta_tag():
    tpl_json = None
    with open(TAG_FILE_PATH, 'r') as file:
        tpl_contents = file.read()
        tpl_json = json.loads(tpl_contents)

    tag_values = []
    for color in COLORS:
        item = f'minecraft:{color}_terracotta'
        tag_values.append(item)

    tag_json = tpl_json.copy()
    tag_json['values'] = tag_values

    output_file = f'./outputs/tags/terracotta.json'
    output_path = os.path.join(CURR_DIR, output_file)
    with open(output_path, "w") as write_file:
        json.dump(tag_json, write_file, indent=2)

def create_dyed_shulker_recipes():
    tpl_json = None
    with open(ITEM_FILE_PATH, 'r') as file:
        tpl_contents = file.read()
        tpl_json = json.loads(tpl_contents)

    for color in COLORS:
        item = f'{color}_shulker_box'

        item_json = tpl_json.copy()
        item_json['type'] = 'cookbook:recipe'
        item_json['name'] = item
        item_json['ingredients'] = [
            'minecraft:shulker_box',
            f'minecraft:{color}_dye'
        ]
        item_json['result']['item'] = f'minecraft:{item}'

        output_file = f'./outputs/recipes/{item}.json'
        output_path = os.path.join(CURR_DIR, output_file)
        with open(output_path, "w") as write_file:
            json.dump(item_json, write_file, indent=2)

def create_bucket_recipes():
    tpl_json = None
    with open(ITEM_FILE_PATH, 'r') as file:
        tpl_contents = file.read()
        tpl_json = json.loads(tpl_contents)

    can_bucket = [
        'cod',
        'lava',
        'pufferfish',
        'salmon',
        'tropical_fish',
        'water'
    ]

    for item_name in can_bucket:
        item = f'{item_name}_bucket'

        item_json = tpl_json.copy()
        item_json['type'] = 'cookbook:recipe'
        item_json['name'] = item
        item_json['ingredients'] = [
            f'minecraft:{item_name}',
            'minecraft:bucket'
        ]
        item_json['result']['item'] = f'minecraft:{item}'

        output_file = f'./outputs/recipes/{item}.json'
        output_path = os.path.join(CURR_DIR, output_file)
        with open(output_path, "w") as write_file:
            json.dump(item_json, write_file, indent=2)


def main():
    # create_concrete_recipes()
    # create_concrete_tag()
    # create_concrete_powder_tag()
    # create_terracotta_tag()
    # create_dyed_shulker_recipes()
    create_bucket_recipes()

if __name__ == '__main__':
    main()
