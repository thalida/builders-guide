import os
import logging

os.environ["TZ"] = "UTC"
logger = logging.getLogger(__name__)

from flask import Flask, jsonify, request, abort

import calculator.utils
import calculator.data
import calculator.calculator

os.environ["TZ"] = "UTC"
app = Flask(__name__)

BAD_REQUEST = 400
SERVER_ERROR = 500


@app.route("/api/<version>/items", methods=["GET"])
def api_get_items(version):
    """GET all items for a given version of Minecraft Java Edition

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        list -- all items
    """
    try:
        return calculator.data.fetch_all_items(version, force_create=app.debug)
    except Exception:
        abort(SERVER_ERROR)


@app.route("/api/<version>/recipes", methods=["GET"])
def api_get_recipes(version):
    """GET all recipes for a given version of Minecraft Java Edition

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        list -- all recipes
    """
    try:
        return calculator.data.fetch_all_recipes(version, force_create=app.debug)
    except Exception:
        abort(SERVER_ERROR)


@app.route("/api/<version>/tags", methods=["GET"])
def api_get_tags(version):
    """GET all tags for a given version of Minecraft Java Edition

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        list -- all tags
    """
    try:
        return calculator.data.fetch_all_tags(version, force_create=app.debug)
    except Exception:
        abort(SERVER_ERROR)


@app.route("/api/<version>/item_mappings", methods=["GET"])
def api_get_item_mappings(version):
    """GET a mapping of all incorrect names of items to their correct version

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        list -- all item mappings
    """
    try:
        return calculator.data.fetch_item_mappings(version, force_create=app.debug)
    except Exception:
        abort(SERVER_ERROR)


@app.route("/api/<version>/supported_recipes_and_items", methods=["GET"])
def api_get_supported_recipes_and_items(version):
    """GET all supported recipes and craftable items
        Supported recipes consist of anything that pass utils.is_supported_recipe()

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        dict -- supported recipes and craftable items
    """

    try:
        recipes = calculator.data.fetch_all_recipes(version, force_create=app.debug)
        supported_recipes_by_result = calculator.data.get_supported_recipes_by_result(
            version, recipes, force_create=app.debug
        )
        supported_craftable_items = calculator.data.get_supported_craftable_items(
            version, supported_recipes_by_result, force_create=app.debug
        )
        response = {
            "supported_recipes_by_result": supported_recipes_by_result,
            "supported_craftable_items": supported_craftable_items,
        }
        return jsonify(response)
    except Exception:
        abort(SERVER_ERROR)


@app.route("/api/<version>/all_crafting_data", methods=["GET"])
def api_get_all_crafting_data(version):
    """GET all crafting data for a given version of Minecraft Java Edition
        Crafting data is a dictionary with all:
        - items
        - tags
        - recipes
        - item_mappings
        - supported_recipes
        - supported_craftable_items

    Arguments:
        version {string} -- Version of Minecraft Java Edition

    Returns:
        dict -- all crafting data
    """
    try:
        return calculator.data.get_all_crafting_data(version, force_create=app.debug)
    except Exception:
        abort(SERVER_ERROR)


@app.route("/api/<version>/parse_items_from_string", methods=["POST"])
def api_parse_items_from_string(version):
    """GET parse items from a array of strings

    Arguments:
        version {string} -- Version of Minecraft Java Edition
        parse_strings {list} -- Strings to be parsed and converted to item list

    Returns:
        dict -- parsed strings and any errors found
    """
    try:
        req_json = request.get_json(force=True)
        parse_strings = req_json.get("parse_strings", [])
    except Exception:
        abort(BAD_REQUEST)

    try:
        all_crafting_data = calculator.data.get_all_crafting_data(
            version, force_create=app.debug
        )
        return calculator.utils.parse_items_from_string(
            parse_strings,
            all_items=all_crafting_data["items"],
            all_tags=all_crafting_data["tags"],
            all_recipes=all_crafting_data["recipes"],
            item_mappings=all_crafting_data["item_mappings"],
        )
    except Exception:
        abort(SERVER_ERROR)


@app.route("/api/<version>/calculate_resources", methods=["POST"])
def api_calculate_resources(version):
    """Calculate resources required to craft the provided items
        Provide either parse_item_strings OR requested_items, will try to use
        requested_items if provided.

    Arguments:
        version {string} -- Version of Minecraft Java Edition
        have_already {dict} -- Map of what items you already have created
                                key is the item you have, value the amount
        recipe_path {dict} -- The chosen recipe path you want to follow
        requested_items {list} -- The items (already formatted) that you'd like crafted
        parse_item_strings {list} -- The strings you'd like converted to an item array

    Returns:
        [type] -- [description]
    """
    try:
        req_json = request.get_json(force=True)
        have_already = req_json.get("have_already", {})
        recipe_path = req_json.get("recipe_path", {})

        # We'll use requested_items by default, and fallback to parse_strings
        requested_items = req_json.get("items", [])
        parse_strings = req_json.get("parse_item_strings")
    except Exception:
        abort(SERVER_ERROR)

    try:
        all_crafting_data = calculator.data.get_all_crafting_data(
            version, force_create=app.debug
        )

        # If no requested items where provied, check if we have strings to parse
        # If so, do so
        if len(requested_items) == 0 and parse_strings is not None:
            parsed_items = calculator.utils.parse_items_from_string(
                parse_strings,
                all_items=all_crafting_data["items"],
                all_tags=all_crafting_data["tags"],
                all_recipes=all_crafting_data["recipes"],
                item_mappings=all_crafting_data["item_mappings"],
            )
            requested_items = parsed_items["items"]

        recipe_tree = calculator.calculator.create_recipe_tree(
            requested_items,
            all_recipes=all_crafting_data["recipes"],
            all_tags=all_crafting_data["tags"],
            supported_recipes=all_crafting_data["supported_recipes"],
        )

        shopping_list = calculator.calculator.create_shopping_list(
            recipe_tree, path=recipe_path, have_already=have_already
        )

        response = {
            "recipe_tree": recipe_tree,
            "shopping_list": shopping_list,
        }

        return jsonify(response)
    except Exception as e:
        logger.exception(e)
        abort(SERVER_ERROR)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")
