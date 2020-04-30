import os
import logging
import re

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

ITEM_LIST_REGEX = (
    r"^(?P<amount1>[\d,]+)?(.*?)(?P<name>[A-Za-z\-_ ]+)(.*?)(?P<amount2>[\d,]+)?$"
)
WORD_SEPERATORS_REGEX = r"[\W_]+"


def raise_error(msg, **kwargs):
    msg = "Error!" if msg is None else msg
    msg = msg.format(**kwargs)
    logger.exception(msg)


def parse_item_name(orig_item_name):
    return orig_item_name.split(":", 1)[-1]


def is_tag_name(orig_item_name):
    return orig_item_name.find("#") != -1


def is_custom_recipe(recipe):
    recipe_type = recipe["type"]
    custom_types = ["calculator:naturally_occurring"]

    return recipe_type in custom_types


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

    is_supported = recipe_type in supported_types
    is_custom = is_custom_recipe(recipe)

    return is_supported or is_custom


def parse_items_from_string(input_strings, all_crafting_data):
    items = []
    no_name_found = []
    no_recipe_found = []
    no_item_found = []

    if not isinstance(input_strings, list):
        input_strings = [input_strings]

    try:
        for line in input_strings:
            matches = re.match(ITEM_LIST_REGEX, line, re.MULTILINE | re.IGNORECASE)
            groups = matches.groupdict()

            if groups.get("name") is None:
                no_name_found.append(line)
                continue

            if groups.get("amount1") is not None:
                amount = groups.get("amount1")
            elif groups.get("amount2") is not None:
                amount = groups.get("amount2")
            else:
                amount = 1

            amount = int(amount)
            name_parts = re.split(WORD_SEPERATORS_REGEX, groups.get("name"))
            name_parts = [word for word in name_parts if len(word) > 0]
            name = "_".join(name_parts).lower()
            name = all_crafting_data["item_mappings"].get(name, name)

            if all_crafting_data["recipes"].get(name) is None:
                no_recipe_found.append(name)

            if all_crafting_data["items"].get(name) is None:
                no_item_found.append(name)

            item = {"amount_required": amount}

            if (
                all_crafting_data["recipes"].get(name) is None
                and all_crafting_data["tags"].get(name) is not None
            ):
                item["tag"] = name
            else:
                item["name"] = name

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
