"""UTILS
Generic-ish utils used across multiple parts of the calculator app
"""
import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import re
import inflect

inflect_engine = inflect.engine()


# Regex used to get the amount and item name from a string
ITEM_LIST_REGEX = (
    r"^(?P<amount1>[\d,]+)?(.*?)(?P<name>[A-Za-z\-_ ]+)(.*?)(?P<amount2>[\d,]+)?$"
)

# Regex used to split a string into words
WORD_SEPERATORS_REGEX = r"[\W_]+"


def parse_item_name(orig_item_name):
    """Get the actual item name from a string, Minecraft prepends items with
    'minecraft:' which we want to remove, ex. minecraft:oak_wood

    Arguments:
        orig_item_name {string} -- Original item name with decorators

    Returns:
        string -- string with any decorates denotated with "word:" removed
    """
    return orig_item_name.split(":", 1)[-1]


def is_tag_name(orig_item_name):
    """Checks if a given item name is a tag. Minecraft puts a # in front of any
    items which are actually tags. For example #minecraft:planks.

    Arguments:
        orig_item_name {string} -- An item name with it's :decorator:

    Returns:
        bool -- True if the itemname contains a "#"
    """
    return orig_item_name.find("#") != -1


def is_custom_recipe(recipe):
    """Checks if a recipe is one I added to the data, custom recipes are there
    to make up for missing or challenging recipe logic.

    Arguments:
        recipe {dict} -- recipe dictionary, which should include name and type keys

    Returns:
        bool -- True if the recipe type is within the supported custom_types
    """
    recipe_type = recipe["type"]
    custom_types = ["calculator:naturally_occurring"]

    return recipe_type in custom_types


def is_supported_recipe(recipe):
    """Check if the recipe is one of the types the calculator supports. Recipes
    that are excluded are mainly around cloning books, banners, etc. Also checks
    if the recipe is custom (which are supported).

    Arguments:
        recipe {dict} -- recipe dict, should include type

    Returns:
        bool -- True if the recipe is one of the support types below or is custom
    """
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

    is_supported = recipe_type in supported_types
    is_custom = is_custom_recipe(recipe)

    return is_supported or is_custom


def generate_correct_item_name(
    raw_name, item_mappings, all_items, all_tags, all_recipes, is_retry=False
):
    """Try to generate the correct item name, if the parsed name is not valid,
    then try to make it singular/plural and try again.

    Arguments:
        raw_name {string} -- The original name
        item_mappings {dict} -- Mapping of invalid item names to correct versions
        all_items {dict} -- All game items
        all_tags {dict} -- All game tags
        all_recipes {dict} -- All game recipes

    Keyword Arguments:
        is_retry {bool} -- Is this a retry? (default: {False})

    Returns:
        string or bool -- Either return the correctly generated string or False
    """
    # Let's format the name so it's snakecase
    # First split the name into separate words
    name_parts = re.split(WORD_SEPERATORS_REGEX, raw_name)

    # Discard any empty strings
    name_parts = [word for word in name_parts if len(word) > 0]

    # Check if the word is singular, if so we'll try to pluralize on the retry
    #   otherwise we'll try to make it singular on the retry
    is_singular = inflect_engine.singular_noun(name_parts[-1]) == False

    orig_last_word = name_parts[-1]
    if is_retry:
        if is_singular:
            last_word = inflect_engine.plural_noun(name_parts[-1])
        else:
            last_word = inflect_engine.singular_noun(name_parts[-1])

        if last_word is False:
            # TODO: Add logging here we shouldn't hit this case but ya never know
            last_word = orig_last_word

        name_parts[-1] = last_word

    # Rejoin the word with underscores
    name = "_".join(name_parts).lower()

    # Check if this itemname maps to something else
    name = item_mappings.get(name, name)

    # Check if the word is a valid item
    is_valid = is_valid_item(name, all_items, all_tags, all_recipes)

    # If it's not valid try to generate another version of the item name
    if not is_valid:
        if is_retry is False:
            return generate_correct_item_name(
                raw_name, item_mappings, all_items, all_tags, all_recipes, is_retry=True
            )
        else:
            return False

    return name


def is_valid_item(name, all_items, all_tags, all_recipes):
    return (
        all_items.get(name) is not None
        or all_tags.get(name) is not None
        or all_recipes.get(name) is not None
    )


def parse_items_from_string(
    input_strings, all_items, all_tags, all_recipes, item_mappings
):
    """Gvien an array of strings, convert them to a proper array of items in the
    form of {"name": string, "amount": int}. For example, given an input of
    ["7 torch"] => {"name": "torch", amount: 7}

    Arguments:
        input_strings {dict} -- The strings to be converted to proper items
        all_items {dict} -- All the minecraft items for a given version
        all_tags {dict} -- All the minecraft tags for a given version
        all_recipes {dict} -- All the minecraft recipes for a given version
        item_mappings {dict} -- A map of bad item names to correct values

    Returns:
        dict -- {
            items: A properly formatted list of all items parsed
            errors: A collection of all errors / problem items found
        }
    """
    items = []
    no_name_found = []
    no_recipe_found = []
    no_item_found = []

    # Make sure we're working with a list of strings
    if not isinstance(input_strings, list):
        input_strings = [input_strings]

    try:
        for line in input_strings:
            # Use regex to get the amount and name from the string
            matches = re.match(ITEM_LIST_REGEX, line, re.MULTILINE | re.IGNORECASE)
            groups = matches.groupdict()

            # If we couldn't parse the name, log to errors and move on
            if groups.get("name") is None:
                no_name_found.append(line)
                continue

            # Try to get the amount of the given item, the regex supports two formats:
            # Amount1 Name => 8 Wool
            # Name Amount2 => wool 8
            # By default we'll use the first amount we come across, for example:
            # 8 Oak Door 9 will result in amount of 8 (9 is discarded)
            # If no amount is provided we'll default to 1
            if groups.get("amount1") is not None:
                amount = groups.get("amount1")
            elif groups.get("amount2") is not None:
                amount = groups.get("amount2")
            else:
                amount = 1

            # Make sure it's an int -- no partial crafting allowed
            amount = int(amount)

            src_name = groups.get("name")
            name = generate_correct_item_name(
                src_name, item_mappings, all_items, all_tags, all_recipes
            )

            if name is False:
                name = src_name

            # Whew, we've made it -- let's setup the item dictionary with the amount
            item = {"amount_required": amount}

            if all_tags.get(name) is None:
                # Does this item exist in the list of all items?
                #   This *could* be a sign of two of different errors, either
                #   with the list of items stored or invalid name
                if all_items.get(name) is None:
                    no_item_found.append(name)

                # Does a recipe exist for this item?
                #   Not having a recipe *is* a valid state for example, red_tulip
                #   But, logging with errors in case there's a problem with the logic
                #   above for figuring out item name.
                if all_recipes.get(name) is None:
                    no_recipe_found.append(name)

            # If there's no recipe for this item BUT it has a matching tag then
            # let's call the item a tag.
            if all_recipes.get(name) is None and all_tags.get(name) is not None:
                item["tag"] = name
            else:
                item["name"] = name

            # aaand, we're done!
            items.append(item)

    except Exception as e:
        logger.exception(e)

    return {
        "items": items,
        "errors": {
            "no_name_found": no_name_found,
            "no_recipe_found": no_recipe_found,
            "no_item_found": no_item_found,
        },
    }
