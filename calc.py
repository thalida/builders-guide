from pprint import pprint
import logging
import traceback
import os

os.environ["TZ"] = "UTC"

import glob
import json
from collections import defaultdict
import math

RECIPES_FILES_DIR = "data/minecraft/{version}/recipes/*"
ITEM_TAGS_FILES_DIR = "data/minecraft/{version}/tags/items/*"

CALCULATOR_RECIPES_FILES_DIR = "data/calculator/{version}/recipes/*"

ALL_RECIPES_FILE = "data/generated/{version}/all_recipes.json"
ALL_ITEM_TAGS_FILE = "data/generated/{version}/all_item_tags.json"
RECIPE_TREE_OUTPUT_FILE = "data/generated/{version}/recipe_tree.json"
SHOPPING_LIST_OUTPUT_FILE = "data/generated/{version}/shopping_list.json"

UNKNOWN_RESULT = "result:unknown"
ERROR_CIRCULAR_REF = "error_circular_ref_on"


def is_tag_name(orig_item_name):
    return orig_item_name.find("#") != -1


def parse_item_name(orig_item_name):
    return orig_item_name.split(":", 1)[-1]


def get_filename_from_path(fullpath):
    base = os.path.basename(fullpath)
    filename = os.path.splitext(base)[0]

    return filename


def fetch_all_recipes(version, force_create=False):
    if force_create:
        return create_all_recipes(version)

    recipes = {}
    try:
        target_file = ALL_RECIPES_FILE.format(version=version)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                recipes = json.loads(data)
            except Exception:
                raise

    except Exception:
        # print(traceback.print_exc())
        recipes = create_all_recipes(version)

    return recipes


def create_all_recipes(version):
    print("CREATING ALL RECIPES COLLECTION FROM FILE SYSTEM")

    recipes = {}
    recipes_file_dir = RECIPES_FILES_DIR.format(version=version)
    recipe_files = glob.glob(recipes_file_dir)

    calculator_recipes_file_dir = CALCULATOR_RECIPES_FILES_DIR.format(version=version)
    calculator_recipe_files = glob.glob(calculator_recipes_file_dir)

    all_recipe_files = calculator_recipe_files + recipe_files
    for filepath in all_recipe_files:
        with open(filepath, "r") as f:
            data = f.read()
            recipe_data = json.loads(data)
            filename = get_filename_from_path(filepath)

            recipe_result = recipe_data.get("result")
            if isinstance(recipe_result, str):
                recipe_data["result"] = {"item": recipe_result}

            recipes[filename] = recipe_data

    target_file = ALL_RECIPES_FILE.format(version=version)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(recipes, write_file)

    return recipes


def fetch_all_item_tags(version, force_create=False):
    if force_create:
        return create_all_item_tags(version)

    item_tags = {}
    try:
        target_file = ALL_ITEM_TAGS_FILE.format(version=version)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                item_tags = json.loads(data)
            except Exception:
                raise

    except Exception:
        # print(traceback.print_exc())
        item_tags = create_all_item_tags(version)

    return item_tags


def create_all_item_tags(version):
    print("CREATING ALL ITEM TAGS COLLECTION FROM FILE SYSTEM")
    item_tags = {}
    item_tags_file_dir = ITEM_TAGS_FILES_DIR.format(version=version)
    item_tag_files = glob.glob(item_tags_file_dir)
    for filepath in item_tag_files:
        with open(filepath, "r") as f:
            data = f.read()
            item_tag_data = json.loads(data)
            filename = get_filename_from_path(filepath)
            item_tags[filename] = item_tag_data

    target_file = ALL_ITEM_TAGS_FILE.format(version=version)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(item_tags, write_file)

    return item_tags


def is_supported_recipe(recipe):
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

    return recipe_type in supported_types or is_custom_recipe(recipe)


def is_custom_recipe(recipe):
    recipe_type = recipe["type"]
    custom_types = ["calculator:naturally_occurring"]

    return recipe_type in custom_types


def get_supported_recipe_results(recipes):
    grouped_by_result = defaultdict(list)

    for recipe_name, recipe in recipes.items():
        if not is_supported_recipe(recipe):
            continue

        recipe_result = recipe.get("result", UNKNOWN_RESULT)

        if recipe_result != UNKNOWN_RESULT:
            if isinstance(recipe_result, dict):
                recipe_result = recipe_result["item"]

            recipe_result = parse_item_name(recipe_result)

        grouped_by_result[recipe_result].append(recipe_name)

    return grouped_by_result


def get_ingredients(recipe, all_item_tags):
    if not is_supported_recipe(recipe):
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


def get_tag_values(tag, all_item_tags):
    found_values = []
    tag_name = parse_item_name(tag)
    ingredients = all_item_tags[tag_name]["values"]

    for ingredient in ingredients:
        is_tag = is_tag_name(ingredient)
        if is_tag:
            found_values += get_tag_values(ingredient, all_item_tags)
        else:
            found_values.append(ingredient)

    return found_values


def get_simple_recipe_ingredients(recipe, all_item_tags):
    ingredient_list = parse_recipe_ingredients(recipe["ingredient"], all_item_tags)
    return ingredient_list


def get_shapeless_recipe_ingredients(recipe, all_item_tags):
    ingredient_list = parse_recipe_ingredients(recipe["ingredients"], all_item_tags)
    return ingredient_list


def get_shaped_recipe_ingredients(recipe, all_item_tags):
    ingredient_list = []
    pattern_counts = {}
    for row in recipe["pattern"]:
        for cell in row:
            if cell not in recipe["key"]:
                continue

            if cell not in pattern_counts:
                pattern_counts[cell] = 1
            else:
                pattern_counts[cell] += 1

    for key, count in pattern_counts.items():
        ingredient = recipe["key"][key]
        is_group = isinstance(ingredient, list)
        new_ingredient_list = parse_recipe_ingredients(
            ingredient, all_item_tags, force_amount_required=count, is_group=is_group
        )
        ingredient_list += new_ingredient_list

    return ingredient_list


def parse_recipe_ingredients(
    ingredients, all_item_tags, is_group=False, force_amount_required=None,
):
    collected_ingredients = []
    found_ingredients = {}

    if not isinstance(ingredients, list):
        ingredients = [ingredients]

    for ingredient in ingredients:
        if isinstance(ingredient, list) or (
            isinstance(ingredient, dict) and ingredient.get("tag") is not None
        ):
            if isinstance(ingredient, dict):
                next_ingredients = get_tag_values(ingredient.get("tag"), all_item_tags)
            else:
                next_ingredients = ingredient

            nested_ingredients = parse_recipe_ingredients(
                next_ingredients,
                all_item_tags,
                force_amount_required=force_amount_required,
                is_group=True,
            )

            collected_ingredients += nested_ingredients
            continue

        if isinstance(ingredient, dict):
            item = ingredient.get("item")
        else:
            item = ingredient

        name = parse_item_name(item)

        if force_amount_required is not None:
            found_ingredients[name] = {
                "name": name,
                "amount_required": force_amount_required,
            }
        else:
            if name not in found_ingredients:
                found_ingredients[name] = {
                    "name": name,
                    "amount_required": 1,
                }
            else:
                found_ingredients[name]["amount_required"] += 1

    collected_ingredients = list(found_ingredients.values()) + collected_ingredients

    if is_group:
        collected_ingredients = [collected_ingredients]

    return collected_ingredients


def create_recipe_tree(
    all_recipes, all_item_tags, supported_recipe_results, items, ancestors=None,
):

    if ancestors is None:
        ancestors = []

    tree = []

    for item in items:
        curr_item_name = item["name"]

        if curr_item_name in ancestors:
            return {
                "error": True,
                "type": ERROR_CIRCULAR_REF,
                "data": curr_item_name,
            }

        amount_required = item.get("amount_required", 1)
        node = {
            "name": curr_item_name,
            "amount_required": amount_required,
            "num_recipes": 0,
            "recipes": [],
        }

        new_ancestors = ancestors.copy()
        new_ancestors.append(curr_item_name)

        found_recipes = supported_recipe_results.get(curr_item_name)
        if found_recipes is None:
            tree.append(node)
            continue

        node_has_circular_ref = False
        recipe_tree = []
        for recipe_name in found_recipes:
            recipe = all_recipes[recipe_name]

            if not is_supported_recipe(recipe):
                continue

            recipe_result_count = recipe["result"].get("count", 1)
            recipe_multiplier = math.ceil(amount_required / recipe_result_count)
            amount_created = recipe_result_count * recipe_multiplier

            ingredients = get_ingredients(recipe, all_item_tags)
            ingredient_tree = create_ingredient_tree(
                ingredients,
                all_recipes,
                all_item_tags,
                supported_recipe_results,
                recipe_multiplier,
                ancestors=new_ancestors,
            )

            if isinstance(ingredient_tree, dict):
                if ingredient_tree.get("data") == curr_item_name:
                    node_has_circular_ref = True
                    break
                else:
                    return ingredient_tree

            recipe_node = {
                "name": recipe_name,
                "type": recipe["type"],
                "recipe_result_count": recipe_result_count,
                "amount_required": amount_required,
                "amount_created": amount_created,
                "ingredients": ingredient_tree,
            }
            recipe_tree.append(recipe_node)

        if node_has_circular_ref:
            recipe_tree = []

        node["num_recipes"] = len(recipe_tree)
        node["recipes"] = recipe_tree
        tree.append(node)

    return tree


def create_ingredient_tree(
    ingredients,
    all_recipes,
    all_item_tags,
    supported_recipe_results,
    recipe_multiplier,
    ancestors=None,
):
    ingredient_tree = []

    for ingredient in ingredients:
        if isinstance(ingredient, list):
            new_ingredient_tree = create_ingredient_tree(
                ingredient,
                all_recipes,
                all_item_tags,
                supported_recipe_results,
                recipe_multiplier,
                ancestors=ancestors,
            )

            if isinstance(new_ingredient_tree, dict):
                ingredient_tree = new_ingredient_tree
                break

            ingredient_tree.append(new_ingredient_tree)
            continue

        ingredient["amount_required"] *= recipe_multiplier

        new_recipe_tree = create_recipe_tree(
            all_recipes,
            all_item_tags,
            supported_recipe_results,
            items=[ingredient],
            ancestors=ancestors,
        )

        if isinstance(new_recipe_tree, dict):
            ingredient_tree = new_recipe_tree
            break

        ingredient_tree += new_recipe_tree

    return ingredient_tree


def create_shopping_list(tree, path={}, parent_node=None, shopping_list=None):
    # print(tree)
    if shopping_list is None:
        shopping_list = {}

    for node in tree:
        node_name = node["name"]
        amount_required = node["amount_required"]

        if node_name not in shopping_list:
            shopping_list[node_name] = {
                "amount_required": 0,
                "amount_used_for": {},
                "amount_recipe_creates": None,
            }

        if parent_node:
            shopping_list[node_name]["amount_used_for"][parent_node] = amount_required

        have_amount = shopping_list[node_name].get("amount_remaining", 0)
        amount_remaining = have_amount - amount_required
        shopping_list[node_name]["amount_required"] += amount_required

        if amount_remaining >= 0:
            shopping_list[node_name]["amount_remaining"] = amount_remaining
            continue

        if node["num_recipes"] == 0:
            continue

        if node_name in path:
            chosen_recipe_name = path[node_name]["recipe"]
            chosen_recipe = None
            for recipe in node["recipes"]:
                if recipe["name"] == chosen_recipe_name:
                    chosen_recipe = recipe
                    break
        else:
            chosen_recipe = node["recipes"][0]

        if chosen_recipe is None:
            print("Ooops! An invalid recipe was chosen")
            continue

        recipe_amount_created = chosen_recipe.get("amount_created", 0)
        shopping_list[node_name]["amount_recipe_creates"] = chosen_recipe.get(
            "recipe_result_count"
        )

        missing_amount = abs(amount_remaining)
        recipe_multiplier = math.ceil(missing_amount / recipe_amount_created)
        amount_created = recipe_amount_created * recipe_multiplier
        shopping_list[node_name]["amount_created"] = amount_created
        shopping_list[node_name]["amount_remaining"] = amount_created - missing_amount

        path_ingredients = path.get(node_name, {}).get("ingredients", [])
        ingredients = chosen_recipe["ingredients"]

        for idx, ingredient in enumerate(ingredients):
            ingredient_item = None
            ingredient_in_path = idx < len(path_ingredients)
            if ingredient_in_path:
                new_path = path_ingredients[idx]
            else:
                new_path = {}.copy()

            if isinstance(ingredient, list):
                if ingredient_in_path and path_ingredients[idx] is not None:
                    path_ingredient = list(path_ingredients[idx].keys())
                    chosen_ingredient = path_ingredient[0]
                    for nested_ingredient in ingredient:
                        if nested_ingredient["name"] == chosen_ingredient:
                            ingredient_item = nested_ingredient
                else:
                    ingredient_item = ingredient[0]
            else:
                ingredient_item = ingredient

            if ingredient_item is None:
                print("Ooops! There is no ingredient_item for", ingredient)
                continue

            new_shopping_list = create_shopping_list(
                [ingredient_item],
                new_path,
                parent_node=node_name,
                shopping_list=shopping_list,
            )
            shopping_list.update(new_shopping_list)

    return shopping_list


def main():
    version = 1.15
    all_recipes = fetch_all_recipes(version=version, force_create=True)
    all_item_tags = fetch_all_item_tags(version=version, force_create=True)
    supported_recipe_results = get_supported_recipe_results(recipes=all_recipes)
    supported_result_names = list(supported_recipe_results.keys())
    supported_result_names.sort()

    nodes = [
        {"name": "torch", "amount_required": 1},
        {"name": "light_blue_concrete_powder", "amount_required": 2},
        {"name": "red_bed", "amount_required": 3},
        {"name": "blue_dye", "amount_required": 4},
        {"name": "purple_stained_glass_pane", "amount_required": 5},
    ]
    # nodes = [{"name": item_name} for item_name in supported_result_names]
    new_recipe_tree = create_recipe_tree(
        all_recipes, all_item_tags, supported_recipe_results, nodes
    )
    recipe_tree_file = RECIPE_TREE_OUTPUT_FILE.format(version=version)
    with open(recipe_tree_file, "w") as write_file:
        json.dump(new_recipe_tree, write_file, indent=4, sort_keys=False)

    path = {
        "torch": {
            "recipe": "torch",
            "ingredients": [
                {"charcoal": {"recipe": "charcoal", "ingredients": [{"oak_log": {}}],}},
                {"stick": {"recipe": "stick_from_bamboo_item"}},
            ],
        },
    }
    # path = {}
    shopping_list = create_shopping_list(new_recipe_tree, path)
    shopping_list_file = SHOPPING_LIST_OUTPUT_FILE.format(version=version)
    with open(shopping_list_file, "w") as write_file:
        json.dump(shopping_list, write_file, indent=4, sort_keys=False)


if __name__ == "__main__":
    main()
