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
ERROR_CIRCULAR_REF = "error_circular_ref_on"


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


def get_is_supported_recipe(recipe):
    recipe_type = recipe["type"]
    supported_types = [
        "minecraft:blasting",
        "minecraft:campfire_cooking",
        "minecraft:crafting_shaped",
        "minecraft:crafting_shapeless",
        "minecraft:smelting",
        "minecraft:smoking",
        "minecraft:stonecutting",
    ]

    return recipe_type in supported_types


def get_ingredients(recipe, all_item_tags):
    if not get_is_supported_recipe(recipe):
        return []

    ingredients = []
    recipe_type = recipe["type"]
    if recipe_type == "minecraft:crafting_shapeless":
        ingredients = get_shapeless_recipe_ingredients(recipe, all_item_tags)

    elif recipe_type == "minecraft:crafting_shaped":
        ingredients = get_shaped_recipe_ingredients(recipe, all_item_tags)

    else:
        ingredients = get_simple_recipe_ingredients(recipe, all_item_tags)

    return ingredients


def get_simple_recipe_ingredients(recipe, all_item_tags):
    ingredient_list = []

    if isinstance(recipe["ingredient"], dict):
        if recipe["ingredient"].get("item") is not None:
            is_group = False
            ingredients = [recipe["ingredient"]]
        elif recipe["ingredient"].get("tag") is not None:
            is_group = True
            tag_name = parse_item_name(recipe["ingredient"].get("tag"))
            ingredients = all_item_tags[tag_name]["values"]
    elif isinstance(recipe["ingredient"], list):
        is_group = True
        ingredients = recipe["ingredient"]

    collected_ingredients = []
    for ingredient in ingredients:
        if isinstance(ingredient, dict):
            item = ingredient.get("item")
        else:
            item = ingredient

        name = parse_item_name(item)
        collected_ingredients.append({"name": name, "amount_required": 1})

    if is_group:
        ingredient_list.append(collected_ingredients)
    else:
        ingredient_list += collected_ingredients

    return ingredient_list


def get_shapeless_recipe_ingredients(recipe, all_item_tags):
    ingredient_list = []
    ingredient_collection = defaultdict(dict)
    for ingredient in recipe["ingredients"]:
        is_group = False
        if isinstance(ingredient, dict):
            if ingredient.get("item") is not None:
                ingredients = [ingredient]
                is_group = False
            if ingredient.get("tag") is not None:
                tag_name = parse_item_name(ingredient.get("tag"))
                ingredients = all_item_tags[tag_name]["values"]
                is_group = True
        elif isinstance(ingredient, list):
            ingredients = ingredient
            is_group = True

        collection_idx = len(ingredient_collection.keys()) + 1 if is_group else 0
        for nested_ingredient in ingredients:
            if isinstance(nested_ingredient, dict):
                item = nested_ingredient.get("item")
            else:
                item = nested_ingredient

            name = parse_item_name(item)

            if item not in ingredient_collection[collection_idx]:
                ingredient_collection[collection_idx][item] = {
                    "name": name,
                    "amount_required": 1,
                }
            else:
                ingredient_collection[collection_idx][item]["amount_required"] += 1

        if collection_idx > 0:
            items = list(ingredient_collection[collection_idx].values())
            ingredient_list.append(items)

    ingredient_list = list(ingredient_collection[0].values()) + ingredient_list

    return ingredient_list


def get_shaped_recipe_ingredients(recipe, all_item_tags):
    pattern = recipe["pattern"]
    pattern_key = recipe["key"]
    ingredient_list = []
    pattern_counts = {}
    for row in pattern:
        for cell in row:
            if cell not in pattern_key:
                continue

            if cell not in pattern_counts:
                pattern_counts[cell] = 1
            else:
                pattern_counts[cell] += 1

    for key, count in pattern_counts.items():
        ingredient = pattern_key[key]

        if isinstance(ingredient, dict):
            if ingredient.get("item") is not None:
                is_group = False
                ingredients = [ingredient]
            elif ingredient.get("tag") is not None:
                is_group = True
                tag_name = parse_item_name(ingredient.get("tag"))
                ingredients = all_item_tags[tag_name]["values"]
        elif isinstance(ingredient, list):
            is_group = True
            ingredients = ingredient

        collected_ingredients = []
        for nested_ingredient in ingredients:
            if isinstance(nested_ingredient, dict):
                item = nested_ingredient.get("item")
            else:
                item = nested_ingredient

            name = parse_item_name(item)
            collected_ingredients.append({"name": name, "amount_required": count})

        if is_group:
            ingredient_list.append(collected_ingredients)
        else:
            ingredient_list += collected_ingredients

    return ingredient_list


def create_recipe_tree(
    all_recipes, all_item_tags, recipes_by_result, items, ancestors=None,
):
    tree = []
    for item in items:
        curr_item_name = item["name"]
        amount_required = item.get("amount_required", 1)
        node = {"name": curr_item_name, "amount_required": amount_required}
        recipe_tree = []
        node_has_circular_ref = False

        found_recipes = recipes_by_result.get(curr_item_name)
        if found_recipes is not None:
            if ancestors is None:
                ancestors = []

            new_ancestors = ancestors.copy()
            new_ancestors.append(curr_item_name)

            for recipe_key in found_recipes:
                recipe = all_recipes[recipe_key]

                is_supported_recipe = get_is_supported_recipe(recipe)

                if not is_supported_recipe:
                    continue

                ingredient_list = get_ingredients(recipe, all_item_tags)
                ingredient_recipe_tree = []

                for ingredient in ingredient_list:
                    ingredients = []

                    if isinstance(ingredient, dict):
                        has_options = False
                        ingredients = [ingredient]
                    elif isinstance(ingredient, list):
                        has_options = True
                        ingredients = ingredient

                    tmp_ingredient_tree = []
                    for nested_ingredient in ingredients:
                        if nested_ingredient["name"] in ancestors:
                            return {
                                "error": True,
                                "type": ERROR_CIRCULAR_REF,
                                "data": nested_ingredient["name"],
                            }

                        new_recipe_tree = create_recipe_tree(
                            all_recipes,
                            all_item_tags,
                            recipes_by_result,
                            items=[nested_ingredient],
                            ancestors=new_ancestors,
                        )

                        if isinstance(new_recipe_tree, list):
                            tmp_ingredient_tree += new_recipe_tree
                            continue

                        if (
                            new_recipe_tree.get("error")
                            and new_recipe_tree.get("type") == ERROR_CIRCULAR_REF
                        ):
                            if new_recipe_tree.get("data") == curr_item_name:
                                node_has_circular_ref = True
                                break
                            else:
                                return new_recipe_tree

                    if node_has_circular_ref:
                        break

                    if has_options:
                        ingredient_recipe_tree.append(tmp_ingredient_tree)
                    else:
                        ingredient_recipe_tree += tmp_ingredient_tree

                if node_has_circular_ref:
                    break

                recipe_node = {
                    "name": recipe_key,
                    "type": recipe["type"],
                    "amount_required": amount_required,
                    "amount_created": recipe["result"].get("count", 1),
                    "ingredients": ingredient_recipe_tree,
                }
                recipe_tree.append(recipe_node)

        if node_has_circular_ref:
            recipe_tree = []

        node["num_recipes"] = len(recipe_tree)
        node["recipes"] = recipe_tree
        tree.append(node)

    return tree


def main():
    all_recipes = fetch_all_recipes(force_create=True)
    all_item_tags = fetch_all_item_tags(force_create=True)
    recipes_by_result = group_recipes_by_result(recipes=all_recipes)
    recipe_result_names = list(recipes_by_result.keys())
    recipe_result_names.sort()

    nodes = [
        {"name": "torch", "amount_required": 1},
        {"name": "light_blue_concrete_powder", "amount_required": 2},
        {"name": "red_bed", "amount_required": 3},
        {"name": "blue_dye", "amount_required": 4},
        {"name": "purple_stained_glass_pane", "amount_required": 5},
    ]
    # nodes = [{"name": item_name} for item_name in recipe_result_names]
    recipe_tree = create_recipe_tree(
        all_recipes, all_item_tags, recipes_by_result, nodes
    )

    with open(CALCULATION_OUTPUT_FILE, "w") as write_file:
        json.dump(recipe_tree, write_file, indent=4, sort_keys=False)


if __name__ == "__main__":
    main()
