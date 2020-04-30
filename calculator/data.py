import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import glob
import json
import sys

import calculator.utils
from collections import defaultdict

DATA_DIR = "calculator/data/"
MINECRAFT_DATA_DIR = DATA_DIR + "sources/minecraft/"
ITEM_FILES_DIR = MINECRAFT_DATA_DIR + "{version}/models/item/*"
RECIPES_FILES_DIR = MINECRAFT_DATA_DIR + "{version}/recipes/*"
ITEM_TAGS_FILES_DIR = MINECRAFT_DATA_DIR + "{version}/tags/items/*"

CUSTOM_DATA_DIR = DATA_DIR + "sources/custom/"
CUSTOM_RECIPES_FILES_DIR = CUSTOM_DATA_DIR + "{version}/recipes/*"
ITEM_MAPPINGS_FILE = CUSTOM_DATA_DIR + "{version}/item_mappings.json"

GENERATED_DATA_DIR = DATA_DIR + "generated/"
ALL_ITEMS_FILE = GENERATED_DATA_DIR + "{version}/all_items.json"
ALL_RECIPES_FILE = GENERATED_DATA_DIR + "{version}/all_recipes.json"
ALL_ITEM_TAGS_FILE = GENERATED_DATA_DIR + "{version}/all_tags.json"
RECIPE_TREE_OUTPUT_FILE = GENERATED_DATA_DIR + "{version}/recipe_tree.json"
SHOPPING_LIST_OUTPUT_FILE = GENERATED_DATA_DIR + "{version}/shopping_list.json"


cur_dir = os.path.dirname(sys.argv[0])
cache = defaultdict(dict)


def get_filename_from_path(fullpath):
    base = os.path.basename(fullpath)
    filename = os.path.splitext(base)[0]
    return filename


def fetch_item_mappings(version, force_create=False):
    if not force_create:
        cached_value = cache.get(version, {}).get("item_mappings")
        if cached_value is not None:
            return cached_value

    item_mappings = {}
    try:
        target_file = ITEM_MAPPINGS_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()
            item_mappings = json.loads(data)
            cache[version]["item_mappings"] = item_mappings
    except Exception as e:
        logger.exception(e)

    cache[version]["item_mappings"] = item_mappings
    return item_mappings


def create_all_items(version):
    items = {}
    items_file_dir = ITEM_FILES_DIR.format(version=version)
    items_file_dir = os.path.join(cur_dir, items_file_dir)
    item_files = glob.glob(items_file_dir)
    for filepath in item_files:
        with open(filepath, "r") as f:
            data = f.read()
            item_data = json.loads(data)
            filename = get_filename_from_path(filepath)
            items[filename] = item_data

    target_file = ALL_ITEMS_FILE.format(version=version)
    target_file = os.path.join(cur_dir, target_file)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(items, write_file)

    return items


def fetch_all_items(version, force_create=False):
    if force_create:
        return create_all_items(version)

    cached_value = cache.get(version, {}).get("items")
    if cached_value is not None:
        return cached_value

    items = {}
    try:
        target_file = ALL_ITEMS_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                items = json.loads(data)
            except Exception as e:
                logger.exception(e)

    except Exception:
        items = create_all_items(version)

    cache[version]["items"] = items
    return items


def create_all_recipes(version):
    recipes = {}
    recipes_file_dir = RECIPES_FILES_DIR.format(version=version)
    recipes_file_dir = os.path.join(cur_dir, recipes_file_dir)
    recipe_files = glob.glob(recipes_file_dir)

    custom_recipes_file_dir = CUSTOM_RECIPES_FILES_DIR.format(version=version)
    custom_recipes_file_dir = os.path.join(cur_dir, custom_recipes_file_dir)
    custom_recipe_files = glob.glob(custom_recipes_file_dir)

    all_recipe_files = custom_recipe_files + recipe_files
    for filepath in all_recipe_files:
        prefix = "calculator-" if CUSTOM_DATA_DIR in filepath else ""
        with open(filepath, "r") as f:
            data = f.read()
            recipe_data = json.loads(data)
            filename = get_filename_from_path(filepath)
            recipe_name = prefix + filename

            recipe_result = recipe_data.get("result")
            if isinstance(recipe_result, str):
                recipe_data["result"] = {"item": recipe_result}

            recipes[recipe_name] = recipe_data

    target_file = ALL_RECIPES_FILE.format(version=version)
    target_file = os.path.join(cur_dir, target_file)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(recipes, write_file)

    return recipes


def fetch_all_recipes(version, force_create=False):
    if force_create:
        return create_all_recipes(version)

    cached_value = cache.get(version, {}).get("recipes")
    if cached_value is not None:
        return cached_value

    recipes = {}
    try:
        target_file = ALL_RECIPES_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                recipes = json.loads(data)
            except Exception:
                raise

    except Exception:
        recipes = create_all_recipes(version)

    cache[version]["recipes"] = recipes

    return recipes


def create_all_tags(version):
    tags = {}
    tags_file_dir = ITEM_TAGS_FILES_DIR.format(version=version)
    tags_file_dir = os.path.join(cur_dir, tags_file_dir)
    item_tag_files = glob.glob(tags_file_dir)
    for filepath in item_tag_files:
        with open(filepath, "r") as f:
            data = f.read()
            item_tag_data = json.loads(data)
            filename = get_filename_from_path(filepath)
            tags[filename] = item_tag_data

    target_file = ALL_ITEM_TAGS_FILE.format(version=version)
    target_file = os.path.join(cur_dir, target_file)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(tags, write_file)

    return tags


def fetch_all_tags(version, force_create=False):
    if force_create:
        return create_all_tags(version)

    cached_value = cache.get(version, {}).get("tags")
    if cached_value is not None:
        return cached_value

    tags = {}
    try:
        target_file = ALL_ITEM_TAGS_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                tags = json.loads(data)
            except Exception:
                raise

    except Exception:
        tags = create_all_tags(version)

    cache[version]["tags"] = tags

    return tags


def get_supported_recipes_by_result(version, recipes, force_create=False):
    if not force_create:
        cached_value = cache.get(version, {}).get("supported_recipes_by_result")
        if cached_value is not None:
            return cached_value

    grouped_by_result = defaultdict(list)

    for recipe_name, recipe in recipes.items():
        if not calculator.utils.is_supported_recipe(recipe):
            continue

        recipe_result = recipe.get("result")

        if recipe_result is not None:
            if isinstance(recipe_result, dict):
                recipe_result = recipe_result["item"]

            recipe_result = calculator.utils.parse_item_name(recipe_result)

        grouped_by_result[recipe_result].append(recipe_name)

    cache[version]["supported_recipes_by_result"] = grouped_by_result

    return grouped_by_result


def get_supported_craftable_items(
    version, supported_recipes_by_result, force_create=False
):
    if not force_create:
        cached_value = cache.get(version, {}).get("supported_craftable_items")
        if cached_value is not None:
            return cached_value

    supported_craftable_items = list(supported_recipes_by_result.keys())
    supported_craftable_items.sort()

    cache[version]["supported_craftable_items"] = supported_craftable_items

    return supported_craftable_items


def get_all_crafting_data(version, force_create=False):
    items = fetch_all_items(version, force_create=force_create)
    tags = fetch_all_tags(version, force_create=force_create)
    recipes = fetch_all_recipes(version, force_create=force_create)
    item_mappings = fetch_item_mappings(version, force_create=force_create)

    supported_recipes_by_result = get_supported_recipes_by_result(
        version, recipes, force_create=force_create
    )
    supported_craftable_items = get_supported_craftable_items(
        version, supported_recipes_by_result, force_create=force_create
    )

    return {
        "items": items,
        "tags": tags,
        "recipes": recipes,
        "item_mappings": item_mappings,
        "supported_recipes": supported_recipes_by_result,
        "supported_craftable_items": supported_craftable_items,
    }
