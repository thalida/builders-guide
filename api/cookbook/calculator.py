import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import math
import cookbook.utils


def get_ingredients(recipe, all_tags):
    """Get the ingredients for a given recipe

    Arguments:
        recipe {dict} -- Minecraft recipe
        all_tags {dict} -- All game tags

    Returns:
        list -- All ingredients for the recipe
    """
    # If this recipe isn't supported return no ingredients
    if not cookbook.utils.is_supported_recipe(recipe):
        return []

    ingredients = []

    # Crafting recipes are a bit more complicated
    if recipe["type"] == "minecraft:crafting_shaped":
        ingredients = get_shaped_recipe_ingredients(recipe, all_tags)
    else:
        raw_ingredients = recipe.get("ingredients", recipe.get("ingredient", []))
        ingredients = format_recipe_ingredients(raw_ingredients, all_tags)

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
    ingredients, all_tags, is_group=False, force_amount_required=None, level=0
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

    for ingredient in ingredients:
        group = None

        # If we're working with a list of ingredients or a tag (which in the end
        # results in a list of ingredients)
        if isinstance(ingredient, list) or (
            isinstance(ingredient, dict) and ingredient.get("tag") is not None
        ):
            # if we're here we're workign with a group of ingredients, which means
            # they can be used interchangeably
            is_group = True

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
                is_group=is_group,
                level=level + 1,
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
    if level == 0 and is_group:
        formatted_ingredients = [formatted_ingredients]

    # :D
    return formatted_ingredients


def is_recipe_error(result):
    """

    Arguments:
        result {dict} -- create_recipe_tree response

    Returns:
        bool -- Is the recipe tree result an error response?\
    """
    return isinstance(result, dict) and result.get("error")


def create_recipe_tree(
    items, all_recipes, all_tags, supported_recipes, ancestors=None, recipe_multiplier=1, is_group=False
):
    """Using the list of `items` provided, generate it's recipe tree. A recipe tree
    is an item with a list of the recipes that craft it, each recipe has a set
    of ingredients they require, and each ingredient has a list of recipes that
    craft it... you can see how this goes on and on.

    Arguments:
        items {list} -- All the items to be crafted
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

    for (item_index, item) in enumerate(items):
        if isinstance(item, dict):
            amount_required = item.get("amount_required", 1)
        else:
            amount_required = 1

        amount_required *= recipe_multiplier

        # correctly format the item
        if has_no_ancestors:
            item = format_recipe_ingredients(
                item, all_tags, force_amount_required=amount_required,
            )

            if len(item) == 1:
                item = item[0]

        # A list of items is an option group, it means all of these items can
        # be used interchangeably.
        if isinstance(item, list):
            # We need to ge the recipe tree for all of these item(s)
            response = create_recipe_tree(
                item,
                all_recipes=all_recipes,
                all_tags=all_tags,
                supported_recipes=supported_recipes,
                ancestors=ancestors,
                is_group=True,
            )

            # Oh, dear -- did we get an error? I only throw errors if there's
            # a circular ref so let's pass it back up the tree!
            if is_recipe_error(response):
                return response

            # Add this response to our top_level tree
            tree.append(response)

            # Move onto the next item
            continue

        item_name = item["name"]

        if item_name in ancestors:
            # If we're here we've found a circular reference. That means the current
            # item has already been found earlier in the recipe tree. We should
            # quit because, that means our ancestor requires itself in order to
            # be crafted. Which is just a very awk state to be in.
            return {
                "error": True,
                "data": item_name,
            }

        # Wicked, let's setup our tree node structure.
        node = {
            "name": item_name,
            "group": item.get("group"),
            "amount_required": amount_required,
            "num_recipes": 0,
            "recipes": [],
            "selected": False
        }

        if not is_group:
            node["selected"] = True
        elif is_group and item_index == 0:
            node["selected"] = True

        # Create a new copy of the ancestors for this branch of the tree
        new_ancestors = ancestors.copy()

        # Add our item to the branch, we'll use this later!
        new_ancestors.append(item_name)

        # Get all of the recipes that create this item
        found_recipes = supported_recipes.get(item_name)

        # Oh! This item does not need to be crafted, let's continue
        if found_recipes is None:
            tree.append(node)
            continue

        node_has_circular_ref = False
        recipe_tree = []

        # For every recipe we want to get it's ingredients, then generate another
        # branch of the recipe tree for how to craft those items -- sounds like
        # a lot and it is! Let's get started...
        for (recipe_index, recipe_name) in enumerate(found_recipes):
            recipe = all_recipes[recipe_name]

            # Somehow this recipe isn't supported, and ya know what. F-it let's skip
            if not cookbook.utils.is_supported_recipe(recipe):
                continue

            # How much does this recipe create?
            recipe_result_count = recipe["result"].get("count", 1)
            # How many times do we need to call this recipe?
            next_recipe_multiplier = math.ceil(amount_required / recipe_result_count)
            # How much is created in the end?
            amount_created = recipe_result_count * next_recipe_multiplier

            # Get a list of all the ingredients
            ingredients = get_ingredients(recipe, all_tags)

            # Create our recipe tree for each ingredient -- this logic has
            # it's own function instead of calling recipe_tree again because
            # ingredients can be a list of arrays of any depth. Yep.
            response = create_recipe_tree(
                ingredients,
                all_recipes=all_recipes,
                all_tags=all_tags,
                supported_recipes=supported_recipes,
                ancestors=new_ancestors,
                recipe_multiplier=next_recipe_multiplier,
            )

            # Oh, dear -- did we get an error? I only throw errors if there's
            # a circular ref so let's handle that!
            if is_recipe_error(response):
                # Check if our current item is the item with the circular reference.
                # Basically, are we the ancestor who somehow needed ourself in
                # our recipe tree?
                if response.get("data") == item_name:
                    # Rage quit and handle this issue.
                    node_has_circular_ref = True
                    break
                # Oh, we're not the correct ancestor, let's pass this error UP
                # the tree!
                else:
                    return response

            # Wow wow, we've finally made it! We have a final recipe node for
            # a given item!
            recipe_node = {
                "name": recipe_name,
                "type": recipe["type"],
                "recipe_result_count": recipe_result_count,
                "amount_required": amount_required,
                "amount_created": amount_created,
                "ingredients": response,
                "selected": recipe_index == 0,
            }
            recipe_tree.append(recipe_node)

        # So, we rage quit. Let's throw away our entire tree, and pretend that
        # never happened!
        if node_has_circular_ref:
            recipe_tree = []

        node["num_recipes"] = len(recipe_tree)
        node["recipes"] = recipe_tree
        tree.append(node)

    # Wow, we got a tree -- perfect!
    return tree


def create_shopping_list(
    tree, path=None, have_already=None, parent_node=None, shopping_list=None
):
    """Based on the recipe tree create the shopping list we need

    Arguments:
        tree {list} -- A create_recipe_tree recipe tree.

    Keyword Arguments:
        path {dict} -- Recipe trees have a lot of branches, in order to create a
                        shopping list we can specify the paths (branches) we
                        want to take (default: {None})
        have_already {dict} -- Key value pair of items to how much you already have
                                in your base / inventory (default: {None})
        parent_node {str} -- Item name that came before (default: {None})
        shopping_list {dict} -- The final resulting shopping list (default: {None})

    Returns:
        dict -- Our shopping list by item
    """
    if shopping_list is None:
        shopping_list = {}

    if path is None:
        path = {}

    if have_already is None:
        have_already = {}

    for node_idx, node in enumerate(tree):
        # check if we've set a path for this node
        node_path = path.get(str(node_idx), {})
        has_node_path = path.get(str(node_idx)) is not None

        # If this node is a list that means all of the items in the list can be
        # used interchangely -- let's pick the chosen item we'd like to craft with!
        if isinstance(node, list):
            chosen_node = None
            # In order to choose the correct item to craft with, we need to check
            # if we've set a value in the path.
            if has_node_path:
                find_node = node_path.get("name")
                # Search through every node to see if one matches the node in
                # our path. If so, that's the chosen node!
                for nested_node in node:
                    if nested_node["name"] == find_node:
                        chosen_node = nested_node
                        break

            # Ah, no node could be found, let's just choose the first one in the list
            if chosen_node is None:
                chosen_node = node[0]

            # Let's gethis recursive shopping list going!
            new_shopping_list = create_shopping_list(
                [chosen_node],
                path={"0": node_path},
                parent_node=parent_node,
                shopping_list=shopping_list,
                have_already=have_already,
            )
            # Make sure our dict stays up to date and skip to the next node
            shopping_list.update(new_shopping_list)
            continue

        node_name = node["name"]
        amount_required = node["amount_required"]

        # We've found a node we haven't seen before! Let's get it's dict setup
        if node_name not in shopping_list:
            amount_available = have_already.get(node_name, 0)
            shopping_list[node_name] = {
                "amount_required": 0,
                "amount_used_for": {},
                "amount_available": amount_available,
                "started_with": amount_available,
                "has_recipe": node["num_recipes"] > 0,
            }

        if parent_node:
            shopping_list[node_name]["amount_used_for"][parent_node] = amount_required

        have_amount = shopping_list[node_name].get("amount_available", 0)
        amount_available = have_amount - amount_required
        shopping_list[node_name]["amount_required"] += amount_required

        # Wicked, we had enough available already to craft our item!
        if amount_available >= 0:
            shopping_list[node_name]["amount_available"] = amount_available
            continue

        # No recipes required to craft this item, so we can move on
        if node["num_recipes"] == 0:
            continue

        # Now time to choose a recipe to craft with, either pick the recipe
        # set by the path or...
        chosen_recipe = None
        if has_node_path:
            node_path_recipe = node_path.get("recipe")
            for recipe in node["recipes"]:
                if recipe["name"] == node_path_recipe:
                    chosen_recipe = recipe
                    break

        # ... choose the first recipe available
        if chosen_recipe is None:
            chosen_recipe = node["recipes"][0]

        # The following logic is about making sure we have all the right amount
        # counts for this item in our shopping list!
        # v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v

        recipe_amount_created = chosen_recipe.get("amount_created", 1)
        recipe_result_count = chosen_recipe.get("recipe_result_count")

        if recipe_result_count is not None:
            shopping_list[node_name]["amount_recipe_creates"] = chosen_recipe.get(
                "recipe_result_count"
            )

        missing_amount = abs(amount_available)
        recipe_multiplier = math.ceil(missing_amount / recipe_amount_created)
        amount_created = recipe_amount_created * recipe_multiplier

        if "total_created" not in shopping_list[node_name]:
            shopping_list[node_name]["total_created"] = 0

        shopping_list[node_name]["total_created"] += amount_created
        shopping_list[node_name]["amount_available"] = amount_created - missing_amount

        # ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

        # Now it's time to get the shopping list required for every ingredient!
        node_path_ingredients = node_path.get("ingredients", {})
        ingredients = chosen_recipe["ingredients"]
        for idx, ingredient in enumerate(ingredients):
            ingredient_item = None

            ingredient_path = node_path_ingredients.get(str(idx), {})
            has_ingredient_path = node_path_ingredients.get(str(idx)) is not None

            # Very similar logic to earlier, if we're working with a list of
            # ingredients that means it's an option group. We need to choose the
            # one ingredient we'd like to craft with!
            if isinstance(ingredient, list) and has_ingredient_path:
                find_ingredient = ingredient_path["name"]
                for nested_ingredient in ingredient:
                    if nested_ingredient["name"] == find_ingredient:
                        ingredient_item = nested_ingredient
                        break
            elif isinstance(ingredient, dict):
                ingredient_item = ingredient

            # If we don't have a chosen ingredient item we  must be workign with
            # a list without a path (or it has a broken one!)
            if ingredient_item is None:
                ingredient_item = ingredient[0]

            # Now get a new shopping list!
            new_shopping_list = create_shopping_list(
                [ingredient_item],
                path={"0": ingredient_path},
                parent_node=node_name,
                shopping_list=shopping_list,
                have_already=have_already,
            )
            # Let's join our current list with the new data
            shopping_list.update(new_shopping_list)

    # And, we're done!
    return shopping_list
