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
    all_recipes, all_item_tags, supported_recipe_results, items, ancestors=None,
):
    tree = []
    for item in items:
        curr_item_name = item["name"]
        amount_required = item.get("amount_required", 1)
        node = {"name": curr_item_name, "amount_required": amount_required}
        recipe_tree = []
        node_has_circular_ref = False

        found_recipes = supported_recipe_results.get(curr_item_name)
        if found_recipes is not None:
            if ancestors is None:
                ancestors = []

            new_ancestors = ancestors.copy()
            new_ancestors.append(curr_item_name)

            for recipe_name in found_recipes:
                recipe = all_recipes[recipe_name]

                if not is_supported_recipe(recipe):
                    continue

                recipe_result_count = recipe["result"].get("count", 1)
                recipe_multiplier = math.ceil(amount_required / recipe_result_count)
                amount_created = recipe_result_count * recipe_multiplier

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

                        nested_ingredient["amount_required"] *= recipe_multiplier

                        new_recipe_tree = create_recipe_tree(
                            all_recipes,
                            all_item_tags,
                            supported_recipe_results,
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
                    "name": recipe_name,
                    "type": recipe["type"],
                    "recipe_result_count": recipe_result_count,
                    "amount_required": amount_required,
                    "amount_created": amount_created,
                    "ingredients": ingredient_recipe_tree,
                }
                recipe_tree.append(recipe_node)

        if node_has_circular_ref:
            recipe_tree = []

        node["num_recipes"] = len(recipe_tree)
        node["recipes"] = recipe_tree
        tree.append(node)

    return tree


# def create_ingredient_tree(
#     curr_item_name,
#     ingredient_list,
#     ancestors,
#     recipe_multiplier,
#     all_recipes,
#     all_item_tags,
#     supported_recipe_results,
# ):
#     new_ancestors = ancestors.copy()
#     new_ancestors.append(curr_item_name)

#     ingredient_recipe_tree = []
#     node_has_circular_ref = False
#     tmp_ingredient_tree = []

#     for ingredient in ingredient_list:
#         if isinstance(ingredient, list):
#             has_options = True
#             (
#                 return_type,
#                 new_ingredient_tree,
#                 node_has_circular_ref,
#             ) = create_ingredient_tree(
#                 curr_item_name,
#                 ingredient,
#                 ancestors,
#                 recipe_multiplier,
#                 all_recipes,
#                 all_item_tags,
#                 supported_recipe_results,
#             )

#             if return_type == "return":
#                 return return_type, new_ingredient_tree, node_has_circular_ref

#             tmp_ingredient_tree += new_ingredient_tree

#         else:
#             has_options = False
#             if ingredient["name"] in ancestors:
#                 return (
#                     "return",
#                     {
#                         "error": True,
#                         "type": ERROR_CIRCULAR_REF,
#                         "data": ingredient["name"],
#                     },
#                     node_has_circular_ref,
#                 )

#             ingredient["amount_required"] *= recipe_multiplier
#             new_recipe_tree = create_recipe_tree(
#                 all_recipes,
#                 all_item_tags,
#                 supported_recipe_results,
#                 items=[ingredient],
#                 ancestors=new_ancestors,
#             )

#             if isinstance(new_recipe_tree, list):
#                 tmp_ingredient_tree += new_recipe_tree
#                 continue

#             if (
#                 new_recipe_tree.get("error")
#                 and new_recipe_tree.get("type") == ERROR_CIRCULAR_REF
#             ):
#                 if new_recipe_tree.get("data") == curr_item_name:
#                     node_has_circular_ref = True
#                     break
#                 else:
#                     return "return", new_recipe_tree, node_has_circular_ref

#         if node_has_circular_ref:
#             break

#     if has_options:
#         ingredient_recipe_tree.append(tmp_ingredient_tree)
#     else:
#         ingredient_recipe_tree += tmp_ingredient_tree

#     return "continue", ingredient_recipe_tree, node_has_circular_ref


def create_shopping_list(tree, path, parent_node=None, shopping_list=None):
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
                print("Ooops! There is no ingredient_item")
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
    recipe_tree = create_recipe_tree(
        all_recipes, all_item_tags, supported_recipe_results, nodes
    )
    recipe_tree_file = RECIPE_TREE_OUTPUT_FILE.format(version=version)
    with open(recipe_tree_file, "w") as write_file:
        json.dump(recipe_tree, write_file, indent=4, sort_keys=False)

    path = {
        "torch": {
            "recipe": "torch",
            "ingredients": [
                {
                    "charcoal": {
                        "recipe": "charcoal",
                        "ingredients": [{"oak_logs": {}}],
                    }
                },
                {"stick": {"recipe": "stick_from_bamboo_item"}},
            ],
        },
    }
    shopping_list = create_shopping_list(recipe_tree, path)
    shopping_list_file = SHOPPING_LIST_OUTPUT_FILE.format(version=version)
    with open(shopping_list_file, "w") as write_file:
        json.dump(shopping_list, write_file, indent=4, sort_keys=False)


if __name__ == "__main__":
    main()
