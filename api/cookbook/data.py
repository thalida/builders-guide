import log

import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import re
import glob
import json
import sys
from collections import defaultdict

import cookbook.utils
import cookbook.constants

cur_dir = os.path.dirname(sys.argv[0])

# Source Minecraft Data
DATA_DIR = "cookbook/data/"
MINECRAFT_DATA_DIR = DATA_DIR + "sources/minecraft/"
ITEM_FILES_DIR = MINECRAFT_DATA_DIR + "{version}/models/item/*"
RECIPES_FILES_DIR = MINECRAFT_DATA_DIR + "{version}/recipes/*"
ITEM_TAGS_FILES_DIR = MINECRAFT_DATA_DIR + "{version}/tags/items/*"

# Source Custom Data
CUSTOM_DATA_DIR = DATA_DIR + "sources/custom/"
CUSTOM_RECIPES_FILES_DIR = CUSTOM_DATA_DIR + "{version}/recipes/*"
CUSTOM_ITEM_TAGS_FILES_DIR = CUSTOM_DATA_DIR + "{version}/tags/items/*"
ITEM_MAPPINGS_FILE = CUSTOM_DATA_DIR + "{version}/item_mappings.json"

# Generated Data
GENERATED_DATA_DIR = DATA_DIR + "generated/"
ALL_ITEMS_FILE = GENERATED_DATA_DIR + "{version}/all_items.json"
ALL_RECIPES_FILE = GENERATED_DATA_DIR + "{version}/all_recipes.json"
ALL_ITEM_TAGS_FILE = GENERATED_DATA_DIR + "{version}/all_tags.json"

# Holds all cached responses
cache = defaultdict(dict)


def get_filename_from_path(fullpath):
    """^^
    Arguments:
        fullpath {string} -- Full file path ex. /path/to/dir/file.json

    Returns:
        string -- Filename ex. file
    """
    base = os.path.basename(fullpath)
    filename = os.path.splitext(base)[0]
    return filename


def fetch_item_mappings(version, force_create=False):
    """Get the generated item mappings, either get them from cache or from the
    filesystem

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Keyword Arguments:
        force_create {bool} -- Force create from source files (default: {False})

    Returns:
        dict -- item_mappings, key is bad item name, value is corrected version
    """

    # Pull from cache if we don't want to force create
    if not force_create:
        cached_value = cache.get(version, {}).get("item_mappings")
        if cached_value is not None:
            return cached_value

    item_mappings = {}
    try:
        # Pull item_mappings from cached file
        target_file = ITEM_MAPPINGS_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()
            item_mappings = json.loads(data)
    except Exception as e:
        logger.exception(e)

    cache[version]["item_mappings"] = item_mappings
    return item_mappings


def genertate_all_items(version):
    """Generate all items by pulling the individual files from the directory

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        list -- all item names
    """
    raw_items = {}

    # Get the items, there is an individual file for each item, from the filesystem.
    # For each file generate a dictionary mapping the filename (item name) to
    # the contents of the file
    items_file_dir = ITEM_FILES_DIR.format(version=version)
    items_file_dir = os.path.join(cur_dir, items_file_dir)
    item_files = glob.glob(items_file_dir)
    for filepath in item_files:
        with open(filepath, "r") as f:
            data = f.read()
            item_data = json.loads(data)
            filename = get_filename_from_path(filepath)

            is_excluded = filename in cookbook.constants.EXCLUDED_ITEMS
            is_excluded_fuzzy = any(search in filename for search in cookbook.constants.EXCLUDED_ITEMS_FUZZY)

            excluded_items_regex = '(?:% s)' % '|'.join(cookbook.constants.EXCLUDED_ITEMS_REGEX)
            is_excluded_regex = re.match(excluded_items_regex, filename)

            entity_isnt_allowed = (
                item_data.get("parent") == "builtin/entity"
                and filename not in cookbook.constants.ALLOWED_ENTITIES
            )

            if is_excluded or is_excluded_fuzzy or is_excluded_regex or entity_isnt_allowed:
                continue

            raw_items[filename] = item_data

    items = []
    for name, data in raw_items.items():
        parent = data.get('parent', '/')
        parent_type, parent_name = parent.split('/')

        if name != parent_name and parent_name in ['crossbow', 'bow', 'fishing_rod']:
            continue

        items.append(name)

    items.sort()

    # Store the items we formatted and pulled from the system
    target_file = ALL_ITEMS_FILE.format(version=version)
    target_file = os.path.join(cur_dir, target_file)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(items, write_file)

    return items


def fetch_all_items(version, force_create=False):
    """Get all items from the cache, the already generated file of parsed data,
    or generate the data.

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Keyword Arguments:
        force_create {bool} -- Force create from source files (default: {False})

    Returns:
        dict -- all items keyed by item name
    """
    # Skip trying to fetch from cached sources and force create
    if force_create:
        items = genertate_all_items(version)

        # Add it to the cache for quick retrival
        cache[version]["items"] = items
        return items

    # Pull data from cache if it exists
    cached_value = cache.get(version, {}).get("items")
    if cached_value is not None:
        return cached_value

    items = {}

    try:
        # Fetch all items from the generated file in the system
        target_file = ALL_ITEMS_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                items = json.loads(data)
            except Exception as e:
                logger.exception(e)

    except Exception:
        # If we run into an problems just recreate the dict of all items
        items = genertate_all_items(version)

    # Add it to the cache for quick retrival
    cache[version]["items"] = items
    return items


def generate_all_recipes(version):
    """Generate all recipes by pulling the individual files from the directory

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        dict -- All of the recipes keyed by recipe name
    """
    recipes = {}

    # Collect all the standard Minecraft recipes
    recipes_file_dir = RECIPES_FILES_DIR.format(version=version)
    recipes_file_dir = os.path.join(cur_dir, recipes_file_dir)
    recipe_files = glob.glob(recipes_file_dir)

    # Collect all of the custom recipes I created
    custom_recipes_file_dir = CUSTOM_RECIPES_FILES_DIR.format(version=version)
    custom_recipes_file_dir = os.path.join(cur_dir, custom_recipes_file_dir)
    custom_recipe_files = glob.glob(custom_recipes_file_dir)

    # combine both sets of recipes, custom_recipe_files MUST be the first
    # set of items in the array
    all_recipe_files = custom_recipe_files + recipe_files
    for filepath in all_recipe_files:
        # prefix all custom recipes with "custom" so that we don't overwrite
        # any existing Minecraft recipes with the same name
        prefix = "custom-" if CUSTOM_DATA_DIR in filepath else ""
        with open(filepath, "r") as f:
            data = f.read()
            recipe_data = json.loads(data)
            filename = get_filename_from_path(filepath)
            recipe_name = recipe_data.get("name", prefix + filename)

            # Sometimes Minecraft data as recipes results as strings instead of
            # dicts, let's make sure it's always a dict
            recipe_result = recipe_data.get("result")
            if isinstance(recipe_result, str):
                recipe_data["result"] = {"item": recipe_result}

            recipe_data["name"] = recipe_name
            recipes[recipe_name] = recipe_data

    # Write the formatted recipe data to a file
    target_file = ALL_RECIPES_FILE.format(version=version)
    target_file = os.path.join(cur_dir, target_file)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(recipes, write_file)

    return recipes


def fetch_all_recipes(version, force_create=False):
    """Get all recipes from the cache, the already generated file of parsed data,
    or generate the data.

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Keyword Arguments:
        force_create {bool} -- Force create from source files (default: {False})

    Returns:
        dict -- all items keyed by item name
    """

    # Skip everything else, just force generate all recipes data
    if force_create:
        recipes = generate_all_recipes(version)

        # Save what we have to the cache
        cache[version]["recipes"] = recipes
        return recipes

    # Pull the recipes from our cache!
    cached_value = cache.get(version, {}).get("recipes")
    if cached_value is not None:
        return cached_value

    recipes = {}

    try:
        # Cached recipes was not available to let's pull the already formatted data
        # from the filesystem
        target_file = ALL_RECIPES_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                recipes = json.loads(data)
            except Exception:
                raise

    except Exception:
        # Ooops, we couldn't find the generated file or ran into an error let's
        # just regenerate everything again.
        recipes = generate_all_recipes(version)

    # Save what we have to the cache
    cache[version]["recipes"] = recipes
    return recipes


def generate_all_tags(version):
    """Generate all tags by pulling the individual files from the directory

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        dict -- All of the tags keyed by tag name
    """

    tags = {}

    # Get and loop through all the tag files in the source Minecraft directory
    tags_file_dir = ITEM_TAGS_FILES_DIR.format(version=version)
    tags_file_dir = os.path.join(cur_dir, tags_file_dir)
    item_tag_files = glob.glob(tags_file_dir)

    # Collect all of the custom tags I created
    custom_tag_file_dir = CUSTOM_ITEM_TAGS_FILES_DIR.format(version=version)
    custom_tag_file_dir = os.path.join(cur_dir, custom_tag_file_dir)
    custom_tag_files = glob.glob(custom_tag_file_dir)

    # combine both sets of recipes, custom_recipe_files MUST be the first
    # set of items in the array
    all_tag_files = custom_tag_files + item_tag_files
    for filepath in all_tag_files:
        # prefix all custom recipes with "custom" so that we don't overwrite
        # any existing Minecraft recipes with the same name
        with open(filepath, "r") as f:
            data = f.read()
            item_tag_data = json.loads(data)
            filename = get_filename_from_path(filepath)
            tags[filename] = item_tag_data

    # Store the generated dictionary to the filesystem for easy access
    target_file = ALL_ITEM_TAGS_FILE.format(version=version)
    target_file = os.path.join(cur_dir, target_file)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w") as write_file:
        json.dump(tags, write_file)

    return tags


def fetch_all_tags(version, force_create=False):
    """Get all tags from the cache, the already generated file of parsed data,
    or generate the data.

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Keyword Arguments:
        force_create {bool} -- Force create from source files (default: {False})

    Returns:
        dict -- all tags keyed by tag name
    """

    # Force re-generation of the data and save it to the cache
    if force_create:
        tags = generate_all_tags(version)

        cache[version]["tags"] = tags
        return tags

    # Pull tag data from our cached data
    cached_value = cache.get(version, {}).get("tags")
    if cached_value is not None:
        return cached_value

    tags = {}
    try:
        # Pull tag data from the generated file in the system
        target_file = ALL_ITEM_TAGS_FILE.format(version=version)
        target_file = os.path.join(cur_dir, target_file)
        with open(target_file, "r") as f:
            data = f.read()

            try:
                tags = json.loads(data)
            except Exception:
                raise

    except Exception:
        # If we ran into a problem just re-generate the data
        tags = generate_all_tags(version)

    # Save to cache and return!
    cache[version]["tags"] = tags
    return tags


def get_supported_recipes_by_result(version, recipes, force_create=False):
    """Returns a dictionary of the recipes supported by the system grouped by
    the resulting item the recipe creates.

    Arguments:
        version {string} -- Version of Minecraft Java Edition
        recipes {list} -- All minecraft recipes for the same version

    Keyword Arguments:
        force_create {bool} -- Force create from recipe data (default: {False})

    Returns:
        dict -- Dictionary of all supported recipes grouped by resulting item name
    """

    # If we're not force creating pull from cache
    if not force_create:
        cached_value = cache.get(version, {}).get("supported_recipes_by_result")
        if cached_value is not None:
            return cached_value

    grouped_by_result = defaultdict(list)

    for recipe_name, recipe in recipes.items():
        # If the recipe is not supported, skip
        if not cookbook.utils.is_supported_recipe(recipe):
            continue

        recipe_result = recipe.get("result")

        if recipe_result is not None:
            if isinstance(recipe_result, dict):
                recipe_result = recipe_result["item"]

            # Pull the actual item name from the recipe result string
            recipe_result = cookbook.utils.parse_item_name(recipe_result)

        grouped_by_result[recipe_result].append(recipe_name)

    # Store this data in our cache
    cache[version]["supported_recipes_by_result"] = grouped_by_result
    return grouped_by_result


def get_supported_craftable_items(
    version, supported_recipes_by_result, force_create=False
):
    """Get a list of all the craftable items

    Arguments:
        version {string} -- Version of Minecraft Java Edition
        supported_recipes_by_result {dict} -- All of the recipes the game supports

    Keyword Arguments:
        force_create  {bool} -- Force create from supported_recipes_by_result (default: {False})

    Returns:
        list -- A list of names of the items that can be crafted
    """

    # Pull from cache is we don't want to force create
    if not force_create:
        cached_value = cache.get(version, {}).get("supported_craftable_items")
        if cached_value is not None:
            return cached_value

    # Get the keys from oru list of supported recipes by result
    supported_craftable_items = list(supported_recipes_by_result.keys())
    # Sort the data alphabetically
    supported_craftable_items.sort()

    # Store in the cache
    cache[version]["supported_craftable_items"] = supported_craftable_items
    return supported_craftable_items


def get_all_crafting_data(version, force_create=False):
    """ There's a lot of data available, let's just grab it all in one!

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Keyword Arguments:
        force_create  {bool} -- Force create all data (default: {False})

    Returns:
        [type] -- [description]
    """
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
