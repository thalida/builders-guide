from pprint import pprint
import logging
import traceback
import os

os.environ["TZ"] = "UTC"

import glob
import json
from collections import defaultdict
import math

RECIPES_FILES_DIR = "data/minecraft/recipes/*"
ITEM_TAGS_FILES_DIR = "data/minecraft/tags/items/*"
GENERATED_FILES_DIR = "data/generated"
ALL_RECIPES_FILE = f"{GENERATED_FILES_DIR}/all_recipes.json"
ALL_ITEM_TAGS_FILE = f"{GENERATED_FILES_DIR}/all_item_tags.json"

UNKNOWN_RESULT = "result:unknown"


def get_filename_from_path(fullpath):
    base = os.path.basename(fullpath)
    filename = os.path.splitext(base)[0]

    return filename


def create_all_recipes():
    print("CREATING ALL RECIPES COLLECTION FROM FILE SYSTEM")
    recipes = {}
    recipe_files = glob.glob(RECIPES_FILES_DIR)
    for filepath in recipe_files:
        with open(filepath, "r") as f:
            data = f.read()
            recipe_data = json.loads(data)
            filename = get_filename_from_path(filepath)

            recipe_result = recipe_data.get("result")
            if isinstance(recipe_result, str):
                recipe_data["result"] = {"item": recipe_result}

            recipes[filename] = recipe_data

    os.makedirs(os.path.dirname(ALL_RECIPES_FILE), exist_ok=True)
    with open(ALL_RECIPES_FILE, "w") as write_file:
        json.dump(recipes, write_file)

    return recipes


def fetch_all_recipes(force_create=False):
    if force_create:
        return create_all_recipes()

    recipes = {}
    try:
        with open(ALL_RECIPES_FILE, "r") as f:
            data = f.read()

            try:
                recipes = json.loads(data)
            except Exception:
                raise

    except Exception:
        # print(traceback.print_exc())
        recipes = create_all_recipes()

    return recipes


def group_recipes(recipes):
    groups = {"by_result": defaultdict(list)}

    for recipe_key, recipe in recipes.items():
        recipe_result = recipe.get("result", UNKNOWN_RESULT)

        if recipe_result != UNKNOWN_RESULT:
            if isinstance(recipe_result, dict):
                recipe_result = recipe_result["item"]

            recipe_result = recipe_result.split(":", 1)[-1]

        groups["by_result"][recipe_result].append(recipe_key)

    return groups


def create_all_item_tags():
    print("CREATING ALL ITEM TAGS COLLECTION FROM FILE SYSTEM")
    item_tags = {}
    item_tag_files = glob.glob(ITEM_TAGS_FILES_DIR)
    for filepath in item_tag_files:
        with open(filepath, "r") as f:
            data = f.read()
            item_tag_data = json.loads(data)
            filename = get_filename_from_path(filepath)
            item_tags[filename] = item_tag_data

    os.makedirs(os.path.dirname(ALL_ITEM_TAGS_FILE), exist_ok=True)
    with open(ALL_ITEM_TAGS_FILE, "w") as write_file:
        json.dump(item_tags, write_file)

    return item_tags


def fetch_all_item_tags(force_create=False):
    if force_create:
        return create_all_item_tags()

    item_tags = {}
    try:
        with open(ALL_ITEM_TAGS_FILE, "r") as f:
            data = f.read()

            try:
                item_tags = json.loads(data)
            except Exception:
                raise

    except Exception:
        # print(traceback.print_exc())
        item_tags = create_all_item_tags()

    return item_tags


def parse_ingredient_key(ingredient_key):
    is_tag = False

    if isinstance(ingredient_key, dict):
        if "item" in ingredient_key:
            ingredient_key = ingredient_key["item"]
        elif "tag" in ingredient_key:
            ingredient_key = ingredient_key["tag"]
            is_tag = True

    return ingredient_key.split(":", 1)[-1], is_tag


def calculate_resources(
    all_recipes, recipes_by_result, all_item_tags, target_items, calculated_items={}
):

    for item in target_items:
        item_key = item["key"]
        required_amount = item["require"]

        found_recipes = recipes_by_result.get(item_key)

        if found_recipes is None:
            continue

        # TODO: change to allow user to pick which recipe they want to use
        recipe_key = found_recipes[0]
        recipe = all_recipes[recipe_key]
        recipe_type = recipe["type"]

        if item_key not in calculated_items:
            calculated_items[item_key] = {"remaining": 0, "require": 0}

        have_amount = calculated_items[item_key]["remaining"]
        remaining_amount = have_amount - required_amount

        calculated_items[item_key]["require"] += required_amount

        if remaining_amount >= 0:
            calculated_items[item_key]["remaining"] = remaining_amount
            continue

        missing_amount = abs(remaining_amount)
        recipe_result_count = recipe["result"].get("count", 1)
        multiplier = math.ceil(missing_amount / recipe_result_count)
        final_result_count = recipe_result_count * multiplier
        calculated_items[item_key]["remaining"] = final_result_count - required_amount

        ingredients = {}
        if recipe_type == "minecraft:smelting":
            ingredient_key, is_tag = parse_ingredient_key(recipe["ingredient"])
            ingredients[ingredient_key] = {"require": 1, "has_options": is_tag}

        elif recipe_type == "minecraft:crafting_shapeless":
            for ingredient in recipe["ingredients"]:
                ingredient_key, is_tag = parse_ingredient_key(ingredient)
                if ingredient_key not in ingredients:
                    ingredients[ingredient_key] = {"require": 1, "has_options": is_tag}
                else:
                    ingredients[ingredient_key]["require"] += 1

        elif recipe_type == "minecraft:crafting_shaped":
            pattern = recipe["pattern"]
            pattern_key = recipe["key"]
            for row in pattern:
                for cell in row:
                    ingredient = pattern_key[cell]

                    # TODO: allow the user to choose which version of an ingrident
                    if isinstance(ingredient, list):
                        ingredient = ingredient[0]

                    ingredient_key, is_tag = parse_ingredient_key(ingredient)
                    if ingredient_key not in ingredients:
                        ingredients[ingredient_key] = {
                            "require": 1,
                            "has_options": is_tag,
                        }
                    else:
                        ingredients[ingredient_key]["require"] += 1

        for ingredient, ingredient_params in ingredients.items():
            print(ingredient, ingredient_params)
            target_items.append(
                {
                    "key": ingredient,
                    "require": ingredient_params["require"] * multiplier,
                    "has_options": is_tag,
                }
            )

    return calculated_items


def main():
    all_recipes = fetch_all_recipes(force_create=True)
    all_item_tags = fetch_all_item_tags(force_create=True)
    recipe_groups = group_recipes(recipes=all_recipes)
    recipes_by_result = recipe_groups["by_result"]
    recipe_result_keys = list(recipes_by_result.keys())
    recipe_result_keys.sort()

    # target_items = {
    #     "torch": {"require": 5},
    #     "light_blue_concrete_powder": {"require": 5},
    # }
    target_items = [
        {"key": "torch", "require": 5},
        {"key": "light_blue_concrete_powder", "require": 5},
    ]
    calculated_resources = calculate_resources(
        all_recipes, recipes_by_result, all_item_tags, target_items
    )


if __name__ == "__main__":
    main()
