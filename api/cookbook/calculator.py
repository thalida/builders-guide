import log
import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import time
import math
from collections import defaultdict
from decorators import profile
import cookbook.utils

# Holds all cached responses
ingredients_cache = defaultdict(dict)

def get_ingredients(recipe, all_tags, version):
    """Get the ingredients for a given recipe

    Arguments:
        recipe {dict} -- Minecraft recipe
        all_tags {dict} -- All game tags

    Returns:
        list -- All ingredients for the recipe
    """
    cached_value = ingredients_cache.get(version, {}).get(recipe["name"])
    if cached_value is not None:
        return cached_value

    # If this recipe isn't supported return no ingredients
    if not cookbook.utils.is_supported_recipe(recipe):
        ingredients_cache[version][recipe["name"]] = []
        return []

    ingredients = []
    single_ingredient_recipes = [
        "minecraft:smelting",
        "minecraft:stonecutting",
        "minecraft:smoking",
        "minecraft:blasting"
    ]

    # Crafting recipes are a bit more complicated
    if recipe["type"] == 'minecraft:crafting_shaped':
        ingredients = get_shaped_recipe_ingredients(recipe, all_tags)
    elif recipe["type"] == 'minecraft:smithing':
        raw_ingredients = [
            recipe.get("base"),
            recipe.get("addition"),
        ]
        ingredients = format_recipe_ingredients(raw_ingredients, all_tags)
    else:
        raw_ingredients = recipe.get("ingredients", recipe.get("ingredient", []))

        if recipe["type"] in single_ingredient_recipes and len(raw_ingredients) > 1:
            raw_ingredients = [raw_ingredients]

        ingredients = format_recipe_ingredients(raw_ingredients, all_tags)

    ingredients_cache[version][recipe["name"]] = ingredients
    return ingredients


def get_shaped_recipe_ingredients(recipe, all_tags):
    """Shaped recipes are a bit complicated, we need to understand the shape
    in order to know the right amount of ingredients we need.

    Arguments:
        recipe {dict} -- Minecraft recipe
        all_tags {dict} -- All game tags

    Returns:
        list -- All of the ingredients for this recipe
    """
    ingredient_list = []
    pattern_counts = {}

    # Every shaped recipe has a pattern which describes where the ingredients
    # need to be placed in order to craft the correct item
    for row in recipe["pattern"]:
        for cell in row:
            # If the cell value is not as part of the recipe key let's skip
            if cell not in recipe["key"]:
                continue

            # Increment a counter of how many times we've seen this cell value
            if cell not in pattern_counts:
                pattern_counts[cell] = 1
            else:
                pattern_counts[cell] += 1

    # Now we have a mapping of cell values to the amount of times they're seen
    for key, count in pattern_counts.items():
        # Get the ingredient that maps to the cell
        ingredient = recipe["key"][key]

        # Oh, is the ingredient a list? That means it's an option set of items
        # that could be used to craft this recipe.
        is_group = isinstance(ingredient, list)

        # Format the recipe ingredients we've gotten and add them to the final
        # list of all ingredients for this recipe.
        ingredient_list += format_recipe_ingredients(
            ingredient, all_tags, force_amount_required=count, is_group=is_group
        )

    # Whew, finally done with this.
    return ingredient_list


def get_tag_values(tag, all_tags, amount_required=None):
    """Tags can have tags so get a list of all the tag values

    Arguments:
        tag {dict} -- Tag who's values (and nested values) you'd like to fetch
        all_tags {dict} -- List of all tags that are available

    Keyword Arguments:
        amount_required {int} -- How many of the tag do we need? (default: {None})

    Returns:
        list -- All the values of the tag
    """
    found_values = []
    tag_name = cookbook.utils.parse_item_name(tag)
    tag_values = all_tags[tag_name]["values"]

    for value in tag_values:
        is_tag = cookbook.utils.is_tag_name(value)

        # If it's a tag in a tag it's time for recursion baby!
        if is_tag:
            # += is python list math we're adding a list to a list
            found_values += get_tag_values(
                value, all_tags, amount_required=amount_required
            )
        # Oop basic tag, let's just format it correctly and save it to our list
        else:
            item = {"item": value, "group": tag_name}
            if amount_required is not None:
                item["amount_required"] = amount_required
            found_values.append(item)

    return found_values


def format_recipe_ingredients(
    ingredients, all_tags, is_group=False, force_amount_required=None, level=0, group_at_level=0
):
    """Given a list of raw ingredients format them to be used by the calculator

    Arguments:
        ingredients {list} -- List of recipe ingredients
        all_tags {dict} -- List of all tags that are available


    Keyword Arguments:
        is_group {bool} -- Are we working with an item group (default: {False})
        force_amount_required {int} -- Value we'd like to set amount_required to (default: {None})
        level {int} -- How many levels deep of ingredients are we? (default: {0})

    Returns:
        list -- All of the ingredients we've formatted
    """
    formatted_ingredients = []
    found_ingredients = {}

    # Make sure we're working with a list of ingredients
    if not isinstance(ingredients, list):
        ingredients = [ingredients]

    for (index, ingredient) in enumerate(ingredients):
        group = None

        # If we're working with a list of ingredients or a tag (which in the end
        # results in a list of ingredients)
        if isinstance(ingredient, list) or (
            isinstance(ingredient, dict) and ingredient.get("tag") is not None
        ):
            # if we're here we're workign with a group of ingredients, which means
            # they can be used interchangeably
            group_at_level = level + 1

            # If it's a dictionary, get all the tag values so we interate over
            # a list of items
            if isinstance(ingredient, dict):
                next_ingredients = get_tag_values(ingredient.get("tag"), all_tags)
            else:
                next_ingredients = ingredient

            # Time for recursion! Let's call this function again with this
            # nested list of ingredients and add the output to our collection of
            # formatted ingredients.
            formatted_ingredients += format_recipe_ingredients(
                next_ingredients,
                all_tags,
                force_amount_required=force_amount_required,
                is_group=True,
                level=level + 1,
                group_at_level=group_at_level,
            )

            # Move on to the next, nothing else to see here
            continue

        if isinstance(ingredient, dict):
            item = ingredient.get("item", ingredient.get("name"))
            group = ingredient.get("group")
        else:
            item = ingredient

        # Parse the item name
        name = cookbook.utils.parse_item_name(item)

        # If we want to force set the amount required do so!
        if force_amount_required is not None:
            found_ingredients[name] = {
                "name": name,
                "amount_required": force_amount_required,
            }
        else:
            # Oh, this is our first time seeing this ingredient so let's setup the dict
            if name not in found_ingredients:
                found_ingredients[name] = {
                    "name": name,
                    "amount_required": 1,
                }
            # Not our first time, add to our count of amount required for this item
            else:
                found_ingredients[name]["amount_required"] += 1

        # If we're a part of a group make sure to set the group
        if group is not None:
            found_ingredients[name]["group"] = group

    # Add the top level basic found ingredients then append our nested recursively
    # found ingredients
    formatted_ingredients = list(found_ingredients.values()) + formatted_ingredients

    # If we're at the top level and we're working with a group, make sure it's
    # combined together in a single list
    if is_group and level == group_at_level:
        formatted_ingredients = [formatted_ingredients]

    # :D
    return formatted_ingredients

# @profile
def create_recipe_tree(
    items,
    selected_build_paths,
    version,
    all_recipes,
    all_tags,
    supported_recipes,
    ancestors=None,
    is_group=False,
):
    """Using the list of `items` provided, generate it's recipe tree. A recipe tree
    is an item with a list of the recipes that craft it, each recipe has a set
    of ingredients they require, and each ingredient has a list of recipes that
    craft it... you can see how this goes on and on.

    Arguments:
        items {list} -- All the items to be crafted
        selected_build_paths {list} - The already selected build paths
        all_recipes {dict} -- All the recipes in the game
        all_tags {dict} -- All the tags in the game
        supported_recipes {dict} -- Only the supported recipes in the game!

    Keyword Arguments:
        ancestors {list} -- All the item names we've had in this branch of the tree (default: {None})

    Returns:
        list -- Our entire recipe tree!
    """

    # If no ancestors setup the list
    has_no_ancestors = ancestors is None or len(ancestors) == 0
    if ancestors is None:
        ancestors = []

    tree = []
    stats = {
        'node_is_circular': False,
        'most_efficient_node': None,
        'min_items_required': 0,
    }

    found_selected_node = not is_group
    selected_node_idx = None

    for (item_index, item) in enumerate(items):
        if isinstance(item, dict):
            amount_required = item.get("amount_required", 1)
        else:
            amount_required = 1

        try:
            amount_required = int(amount_required)
        except:
            amount_required = 1

        # correctly format the item
        if has_no_ancestors:
            item = format_recipe_ingredients(
                item,
                all_tags,
                force_amount_required=amount_required,
                is_group=isinstance(item, list)
            )

            if len(item) == 1:
                item = item[0]

        # A list of items is an option group, it means all of these items can
        # be used interchangeably.
        if isinstance(item, list):
            # We need to ge the recipe tree for all of these item(s)
            response, res_stats = create_recipe_tree(
                item,
                selected_build_paths,
                version=version,
                all_recipes=all_recipes,
                all_tags=all_tags,
                supported_recipes=supported_recipes,
                ancestors=ancestors,
                is_group=True,
            )

            if res_stats["node_is_circular"]:
                stats["node_is_circular"] = True

            stats["min_items_required"] += amount_required

            # Add this response to our top_level tree
            tree.append(response)

            # Move onto the next item
            continue

        item_name = item["name"]

        # Skip any ingredients which are self placeholders
        if item_name == 'self':
            continue

        # Wicked, let's setup our tree node structure.
        node = {
            "id": f'node-{item_name}-{time.time()}',
            "name": item_name,
            "group": item.get("group"),
            "amount_required": amount_required,
            "num_recipes": 0,
            "recipes": [],
            "selected": not is_group,
            "stats": {
                "max_recipe_efficiency": None,
                "min_recipe_ingredients": None,
            }
        }

        if is_group and item_name in selected_build_paths:
            node["selected"] = True
            found_selected_node = True

        if not is_group:
            stats["min_items_required"] += amount_required

        # Get all of the recipes that create this item
        found_recipes = supported_recipes.get(item_name)

        # If TRUE we've found a circular reference. That means the current
        # item has already been found earlier in the recipe tree.
        is_circular_ref = item_name in ancestors

        # If FALSE this item does not need to be crafted
        has_recipes = found_recipes is not None

        if is_circular_ref or not has_recipes:
            node["stats"]["max_recipe_efficiency"] = 0
            node["stats"]["min_recipe_ingredients"] = 0

            if (
                stats["most_efficient_node"] is None or
                stats["most_efficient_node"] < 0
            ):
                stats["most_efficient_node"] = 0
                selected_node_idx = len(tree)

            if is_circular_ref:
                stats["node_is_circular"] = True

            tree.append(node)
            continue

        custom_recipes = []
        game_recipes = []
        for recipe_name in found_recipes:
            if "custom-" in recipe_name:
                custom_recipes.append(recipe_name)
            else:
                game_recipes.append(recipe_name)

        custom_recipes.sort()
        game_recipes.sort()
        sorted_recipes = custom_recipes + game_recipes

        # Create a new copy of the ancestors for this branch of the tree
        new_ancestors = ancestors.copy()
        # Add our item to the branch, we'll use this later!
        new_ancestors.append(item_name)

        recipe_tree = []
        found_circular_node = False

        item_build_path = selected_build_paths.get(item_name, {})
        selected_recipe = item_build_path.get('recipe', {})
        found_selected_recipe = False
        selected_recipe_idx = None

        # For every recipe we want to get it's ingredients, then generate another
        # branch of the recipe tree for how to craft those items -- sounds like
        # a lot and it is! Let's get started...
        for (recipe_index, recipe_name) in enumerate(sorted_recipes):
            recipe = all_recipes[recipe_name]

            # Somehow this recipe isn't supported, and ya know what. F-it let's skip
            if not cookbook.utils.is_supported_recipe(recipe):
                continue

            # What does this recipe create?
            result_name = cookbook.utils.parse_item_name(recipe["result"].get("item"))

            # And how much of it does this recipe make?
            amount_created = recipe["result"].get("count", 1)

            # Get a list of all the ingredients
            ingredients = get_ingredients(recipe, all_tags, version)

            new_selected_build_paths = selected_recipe.get('ingredients', {})

            # Create our recipe tree for each ingredient -- this logic has
            # it's own function instead of calling recipe_tree again because
            # ingredients can be a list of arrays of any depth. Yep.
            response, recipe_stats = create_recipe_tree(
                ingredients,
                new_selected_build_paths,
                version=version,
                all_recipes=all_recipes,
                all_tags=all_tags,
                supported_recipes=supported_recipes,
                ancestors=new_ancestors,
            )

            recipe_efficiency = amount_created - recipe_stats["min_items_required"] + recipe_stats['most_efficient_node']

            if recipe_stats["node_is_circular"]:
                stats["node_is_circular"] = True
                recipe_efficiency = -2 * abs(recipe_efficiency)

            # Wow wow, we've finally made it! We have a final recipe node for
            # a given item!
            recipe_node = {
                "id": f'recipe-{recipe_name}-{time.time()}',
                "name": recipe.get("name", recipe_name),
                "type": recipe["type"],
                "result_name": result_name,
                "amount_required": amount_required,
                "amount_created": amount_created,
                "ingredients": response,
                "efficiency": recipe_efficiency,
                "selected": False,
                "recipe_stats": recipe_stats,
            }

            if recipe_node['name'] == selected_recipe.get('name'):
                found_selected_recipe = True
                recipe_node['selected'] = True
            elif (
                node["stats"]["max_recipe_efficiency"] is None or
                recipe_efficiency > node["stats"]["max_recipe_efficiency"]
            ):
                node["stats"]["max_recipe_efficiency"] = recipe_efficiency
                node["stats"]["min_recipe_ingredients"] = recipe_stats["min_items_required"]
                selected_recipe_idx = len(recipe_tree)

            recipe_tree.append(recipe_node)

        if not found_selected_recipe and selected_recipe_idx is not None:
            recipe_tree[selected_recipe_idx]["selected"] = True

        if node["stats"]["max_recipe_efficiency"] is None:
            node["stats"]["max_recipe_efficiency"] = 0

        if node["stats"]["min_recipe_ingredients"] is None:
            node["stats"]["min_recipe_ingredients"] = 0

        if not is_group:
            stats["min_items_required"] += node["stats"]["min_recipe_ingredients"]

        if (
            stats["most_efficient_node"] is None or
            node["stats"]["max_recipe_efficiency"] > stats["most_efficient_node"]
        ):
            stats["most_efficient_node"] = node["stats"]["max_recipe_efficiency"]
            selected_node_idx = len(tree)

            if is_group:
                stats["min_items_required"] = node["stats"]["min_recipe_ingredients"]

        node["num_recipes"] = len(recipe_tree)
        node["recipes"] = recipe_tree
        tree.append(node)

    if not found_selected_node and is_group:
        tree[selected_node_idx]["selected"] = True

    if stats["most_efficient_node"] is None:
        stats["most_efficient_node"] = 0

    # Wow, we got a tree -- perfect!
    return tree, stats


def create_shopping_list(
    path,
    have_already=None,
    parent_used_leftovers=False,
    parent_node=None,
    shopping_list=None,
    recipe_multiplier=1,
    level=0
):
    """Based on the recipe tree create the shopping list we need

    Arguments:
        path {dict} -- Recipe trees have a lot of branches, in order to create a
                        shopping list we can specify the paths (branches) we
                        want to take (default: {None})

    Keyword Arguments:
        have_already {dict} -- Key value pair of items to how much you already have
                                in your base / inventory (default: {None})
        parent_node {str} -- Item name that came before (default: {None})
        shopping_list {dict} -- The final resulting shopping list (default: {None})

    Returns:
        dict -- Our shopping list by item
    """

    if shopping_list is None:
        shopping_list = {}

    if have_already is None:
        have_already = {}

    for node_name, node in path.items():
        node_used_leftovers = parent_used_leftovers
        # node_name = node["name"]
        amount_required = node["amount_required"]

        if not isinstance(amount_required, int):
            amount_required = 0

        amount_required = amount_required * recipe_multiplier

        # We've found a node we haven't seen before! Let's get it's dict setup
        if node_name not in shopping_list:
            have = have_already.get(node_name, 0)
            shopping_list[node_name] = {
                "name": node_name,
                "level": level,
                "has_recipe": node.get('recipe') is not None,
                "amount_required": 0,
                "amount_available": have,
                "have": have,
                "implied_have": 0,
                "amount_used_for": {
                    "self": 0,
                    "recipes": 0,
                },
                "requires": [],
                "total_created": 0,
            }

        if level < shopping_list[node_name]["level"]:
            shopping_list[node_name]["level"] = level

        have = shopping_list[node_name].get("have", 0)
        amount_available = shopping_list[node_name].get("amount_available", 0)
        total_created = shopping_list[node_name].get("total_created", 0)

        if parent_node:
            if parent_node not in shopping_list[node_name]["amount_used_for"]:
                 shopping_list[node_name]["amount_used_for"][parent_node] = 0

            if not node_used_leftovers:
                shopping_list[node_name]["amount_used_for"]["recipes"] += amount_required
                shopping_list[node_name]["amount_used_for"][parent_node] += amount_required

            if node_name not in shopping_list[parent_node]["requires"]:
                shopping_list[parent_node]["requires"].append(node_name)
        else:
            shopping_list[node_name]["amount_used_for"]["self"] += amount_required

        if node_used_leftovers:
             shopping_list[node_name]["implied_have"] += amount_required
        else:
            shopping_list[node_name]["amount_required"] += amount_required
            amount_available -= amount_required

            # Wicked, we had enough available already to craft our item!
            if amount_available >= 0:
                shopping_list[node_name]["amount_available"] = amount_available
                node_used_leftovers = True

        # No recipes required to craft this item, so we can move on
        if node.get('recipe') is None:
            continue

        # The following logic is about making sure we have all the right amount
        # counts for this item in our shopping list!
        # v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v

        recipe_amount_created = node["recipe"].get("amount_created", 1)
        shopping_list[node_name]["amount_recipe_creates"] = recipe_amount_created
        shopping_list[node_name]["recipe_type"] = node["recipe"]["type"]

        if node_used_leftovers:
            next_recipe_multiplier = 0
        else:
            missing_amount = abs(amount_available)
            next_recipe_multiplier = math.ceil(missing_amount / recipe_amount_created)
            amount_created = recipe_amount_created * next_recipe_multiplier
            shopping_list[node_name]["total_created"] += amount_created
            shopping_list[node_name]["amount_available"] = amount_created - missing_amount

        # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        # Now it's time to get the shopping list required for every ingredient!
        new_shopping_list = create_shopping_list(
            node["recipe"].get('ingredients', {}),
            parent_node=node_name,
            shopping_list=shopping_list,
            have_already=have_already,
            parent_used_leftovers=node_used_leftovers,
            recipe_multiplier=next_recipe_multiplier,
            level=level + 1
        )

        # Let's join our current list with the new data
        shopping_list.update(new_shopping_list)

    # And, we're done!
    return shopping_list
