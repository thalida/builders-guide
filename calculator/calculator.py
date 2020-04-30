import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

import math
import calculator.utils


def get_ingredients(recipe, all_tags):
    if not calculator.utils.is_supported_recipe(recipe):
        return []

    ingredients = []
    recipe_type = recipe["type"]

    if recipe_type == "minecraft:crafting_shaped":
        ingredients = get_shaped_recipe_ingredients(recipe, all_tags)

    elif recipe_type == "minecraft:crafting_shapeless":
        ingredients = format_recipe_ingredients(recipe["ingredients"], all_tags)

    else:
        ingredients = format_recipe_ingredients(recipe["ingredient"], all_tags)

    return ingredients


def get_tag_values(tag, all_tags, amount_required=None):
    found_values = []
    tag_name = calculator.utils.parse_item_name(tag)
    ingredients = all_tags[tag_name]["values"]

    for ingredient in ingredients:
        is_tag = calculator.utils.is_tag_name(ingredient)
        if is_tag:
            found_values += get_tag_values(
                ingredient, all_tags, amount_required=amount_required
            )
        else:
            item = {"item": ingredient, "group": tag_name}
            if amount_required is not None:
                item["amount_required"] = amount_required
            found_values.append(item)

    return found_values


def get_shaped_recipe_ingredients(recipe, all_tags):
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
        new_ingredient_list = format_recipe_ingredients(
            ingredient, all_tags, force_amount_required=count, is_group=is_group
        )
        ingredient_list += new_ingredient_list

    return ingredient_list


def format_recipe_ingredients(
    ingredients, all_tags, is_group=False, force_amount_required=None, level=0
):
    collected_ingredients = []
    found_ingredients = {}

    if not isinstance(ingredients, list):
        ingredients = [ingredients]

    for ingredient in ingredients:
        group = None

        if isinstance(ingredient, list) or (
            isinstance(ingredient, dict) and ingredient.get("tag") is not None
        ):
            is_group = True
            if isinstance(ingredient, dict):
                next_ingredients = get_tag_values(ingredient.get("tag"), all_tags)
            else:
                next_ingredients = ingredient

            nested_ingredients = format_recipe_ingredients(
                next_ingredients,
                all_tags,
                force_amount_required=force_amount_required,
                is_group=is_group,
                level=level + 1,
            )

            collected_ingredients += nested_ingredients
            continue

        if isinstance(ingredient, dict):
            item = ingredient.get("item", ingredient.get("name"))
            group = ingredient.get("group")
        else:
            item = ingredient

        name = calculator.utils.parse_item_name(item)

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

        if group is not None:
            found_ingredients[name]["group"] = group

    collected_ingredients = list(found_ingredients.values()) + collected_ingredients
    if level == 0 and is_group:
        collected_ingredients = [collected_ingredients]

    return collected_ingredients


def is_recipe_error(result):
    return isinstance(result, dict) and result.get("error")


def create_recipe_tree(
    items,
    all_recipes,
    all_tags,
    supported_recipes,
    ancestors=None,
    force_format_items=False,
):

    if ancestors is None:
        ancestors = []

    tree = []

    for item in items:
        if isinstance(item, dict):
            amount_required = item.get("amount_required", 1)
        else:
            amount_required = 1

        if force_format_items:
            item = format_recipe_ingredients(
                item, all_tags, force_amount_required=amount_required,
            )
            if len(item) == 1:
                item = item[0]

        if isinstance(item, list):
            nested_tree = create_recipe_tree(
                item,
                all_recipes=all_recipes,
                all_tags=all_tags,
                supported_recipes=supported_recipes,
                ancestors=ancestors,
            )
            tree.append(nested_tree)
            continue

        item_name = item["name"]
        if item_name in ancestors:
            return {
                "error": True,
                "data": item_name,
            }

        amount_required = item.get("amount_required", 1)
        node = {
            "name": item_name,
            "group": item.get("group"),
            "amount_required": amount_required,
            "num_recipes": 0,
            "recipes": [],
        }

        new_ancestors = ancestors.copy()
        new_ancestors.append(item_name)

        found_recipes = supported_recipes.get(item_name)
        if found_recipes is None:
            tree.append(node)
            continue

        node_has_circular_ref = False
        recipe_tree = []
        for recipe_name in found_recipes:
            recipe = all_recipes[recipe_name]

            if not calculator.utils.is_supported_recipe(recipe):
                continue

            recipe_result_count = recipe["result"].get("count", 1)
            recipe_multiplier = math.ceil(amount_required / recipe_result_count)
            amount_created = recipe_result_count * recipe_multiplier

            ingredients = get_ingredients(recipe, all_tags)
            response = create_ingredient_tree(
                ingredients,
                all_recipes,
                all_tags,
                supported_recipes,
                recipe_multiplier,
                ancestors=new_ancestors,
            )

            if is_recipe_error(response):
                if response.get("data") == item_name:
                    node_has_circular_ref = True
                    break
                else:
                    return response

            recipe_node = {
                "name": recipe_name,
                "type": recipe["type"],
                "recipe_result_count": recipe_result_count,
                "amount_required": amount_required,
                "amount_created": amount_created,
                "ingredients": response,
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
    all_tags,
    supported_recipes,
    recipe_multiplier,
    ancestors=None,
):
    ingredient_tree = []

    for ingredient in ingredients:
        if isinstance(ingredient, list):
            is_nested_ingredient = True
            response = create_ingredient_tree(
                ingredient,
                all_recipes,
                all_tags,
                supported_recipes,
                recipe_multiplier,
                ancestors=ancestors,
            )
        else:
            is_nested_ingredient = False
            ingredient["amount_required"] *= recipe_multiplier
            response = create_recipe_tree(
                [ingredient],
                all_recipes=all_recipes,
                all_tags=all_tags,
                supported_recipes=supported_recipes,
                ancestors=ancestors,
            )

        if is_recipe_error(response):
            ingredient_tree = response
            break

        if is_nested_ingredient:
            ingredient_tree.append(response)
        else:
            ingredient_tree += response

    return ingredient_tree


def create_shopping_list(
    tree, path=None, have_already=None, parent_node=None, shopping_list=None
):
    if shopping_list is None:
        shopping_list = {}

    if path is None:
        path = {}

    if have_already is None:
        have_already = {}

    for node_idx, node in enumerate(tree):
        node_path = path.get(node_idx, {})
        has_node_path = path.get(node_idx) is not None

        if isinstance(node, list):
            chosen_node = None
            if has_node_path:
                find_node = node_path.get("name")
                for nested_node in node:
                    if nested_node["name"] == find_node:
                        chosen_node = nested_node
                        break

            if chosen_node is None:
                chosen_node = node[0]

            new_shopping_list = create_shopping_list(
                [chosen_node],
                path={0: node_path},
                parent_node=parent_node,
                shopping_list=shopping_list,
                have_already=have_already,
            )
            shopping_list.update(new_shopping_list)
            continue

        node_name = node["name"]
        amount_required = node["amount_required"]

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

        if amount_available >= 0:
            shopping_list[node_name]["amount_available"] = amount_available
            continue

        if node["num_recipes"] == 0:
            continue

        chosen_recipe = None
        if has_node_path:
            node_path_recipe = node_path.get("recipe")
            for recipe in node["recipes"]:
                if recipe["name"] == node_path_recipe:
                    chosen_recipe = recipe
                    break

        if chosen_recipe is None:
            chosen_recipe = node["recipes"][0]

        recipe_amount_created = chosen_recipe.get("amount_created", 0)
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

        node_path_ingredients = node_path.get("ingredients", {})
        ingredients = chosen_recipe["ingredients"]

        for idx, ingredient in enumerate(ingredients):
            ingredient_item = None

            ingredient_path = node_path_ingredients.get(idx, {})
            has_ingredient_path = node_path_ingredients.get(idx) is not None

            if isinstance(ingredient, list) and has_ingredient_path:
                find_ingredient = ingredient_path["name"]
                for nested_ingredient in ingredient:
                    if nested_ingredient["name"] == find_ingredient:
                        ingredient_item = nested_ingredient
                        break
            elif isinstance(ingredient, dict):
                ingredient_item = ingredient

            if ingredient_item is None:
                ingredient_item = ingredient[0]

            new_shopping_list = create_shopping_list(
                [ingredient_item],
                path={0: ingredient_path},
                parent_node=node_name,
                shopping_list=shopping_list,
                have_already=have_already,
            )
            shopping_list.update(new_shopping_list)

    return shopping_list
