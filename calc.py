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
CALCULATION_OUTPUT_FILE = f"{GENERATED_FILES_DIR}/calculation_output.json"

UNKNOWN_RESULT = "result:unknown"


def parse_item_name(orig_item_name):
    return orig_item_name.split(":", 1)[-1]


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


def group_recipes_by_result(recipes):
    grouped_by_result = defaultdict(list)

    for recipe_key, recipe in recipes.items():
        recipe_result = recipe.get("result", UNKNOWN_RESULT)

        if recipe_result != UNKNOWN_RESULT:
            if isinstance(recipe_result, dict):
                recipe_result = recipe_result["item"]

            recipe_result = parse_item_name(recipe_result)

        grouped_by_result[recipe_result].append(recipe_key)

    return grouped_by_result


def create_recipe_tree(
    all_recipes, all_item_tags, recipes_by_result, items, prev_item_name=None
):

    tree = []
    for item in items:
        curr_item_name = item["name"]
        node = {"item_name": curr_item_name}
        recipe_tree = []
        force_as_terminal_node = False

        found_recipes = recipes_by_result.get(curr_item_name)
        if found_recipes is not None:
            for recipe_key in found_recipes:
                recipe = all_recipes[recipe_key]
                recipe_type = recipe["type"]
                ingrident_tree = []
                ingredients = []

                if (
                    recipe_type == "minecraft:smelting"
                    or recipe_type == "minecraft:blasting"
                ):
                    ingredients = [recipe["ingredient"]]

                elif recipe_type == "minecraft:crafting_shapeless":
                    ingredients = recipe["ingredients"]

                elif recipe_type == "minecraft:crafting_shaped":
                    ingredients = list(recipe["key"].values())

                # if (
                #     recipe_type == "minecraft:smelting"
                #     or recipe_type == "minecraft:blasting"
                # ):
                #     continue

                # if recipe_type == "minecraft:crafting_shapeless":
                #     ingredients = recipe["ingredients"]

                # elif recipe_type == "minecraft:crafting_shaped":
                #     ingredients = list(recipe["key"].values())

                for ingredient in ingredients:
                    if (
                        isinstance(ingredient, list)
                        or ingredient.get("tag") is not None
                    ):
                        print(f"TODO: HANDLE NESTED INGREDIENTS! for {curr_item_name}")
                        ingrident_tree.append({"__has_nested_ingredients": True})
                        continue

                    ingredient_name = parse_item_name(ingredient["item"])

                    if prev_item_name is not None and prev_item_name == ingredient_name:
                        node["__make_terminal_node"] = True
                        break

                    tmp_ingredient_tree = create_recipe_tree(
                        all_recipes,
                        all_item_tags,
                        recipes_by_result,
                        items=[{"name": ingredient_name, "require": 1}],
                        prev_item_name=curr_item_name,
                    )

                    if tmp_ingredient_tree[0].get("__make_terminal_node"):
                        force_as_terminal_node = True
                        break

                    ingrident_tree += tmp_ingredient_tree

                if force_as_terminal_node:
                    break

                recipe_node = {
                    "name": recipe_key,
                    "type": recipe_type,
                    "ingredients": ingrident_tree,
                }
                recipe_tree.append(recipe_node)

        if force_as_terminal_node:
            recipe_tree = []

        node["recipes"] = recipe_tree
        node["has_recipe"] = len(recipe_tree) > 0
        tree.append(node)

    return tree


def main():
    all_recipes = fetch_all_recipes(force_create=True)
    all_item_tags = fetch_all_item_tags(force_create=True)
    recipes_by_result = group_recipes_by_result(recipes=all_recipes)
    recipe_result_names = list(recipes_by_result.keys())
    recipe_result_names.sort()

    nodes = [
        {"name": "torch", "require": 1},
        {"name": "light_blue_concrete_powder", "require": 2},
        {"name": "red_bed", "require": 3},
        {"name": "blue_dye", "require": 4},
        {"name": "purple_stained_glass_pane", "require": 5},
    ]

    recipe_tree = create_recipe_tree(
        all_recipes, all_item_tags, recipes_by_result, nodes
    )

    with open(CALCULATION_OUTPUT_FILE, "w") as write_file:
        json.dump(recipe_tree, write_file, indent=4, sort_keys=False)


if __name__ == "__main__":
    main()
