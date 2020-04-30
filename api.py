import os
from flask import Flask, jsonify

import calculator.utils
import calculator.data
import calculator.calculator

os.environ["TZ"] = "UTC"
app = Flask(__name__)


@app.route("/api/<version>/items", methods=["GET"])
def api_get_items(version):
    return calculator.data.fetch_all_items(version, force_create=app.debug)


@app.route("/api/<version>/recipes", methods=["GET"])
def api_get_recipes(version):
    return calculator.data.fetch_all_recipes(version, force_create=app.debug)


@app.route("/api/<version>/tags", methods=["GET"])
def api_get_tags(version):
    return calculator.data.fetch_all_tags(version, force_create=app.debug)


@app.route("/api/<version>/item_mappings", methods=["GET"])
def api_get_item_mappings(version):
    return calculator.data.fetch_item_mappings(version, force_create=app.debug)


@app.route("/api/<version>/all_crafting_data", methods=["GET"])
def api_get_supported_recipes(version):
    return calculator.data.get_all_crafting_data(version, force_create=app.debug)


@app.route("/api/<version>/parse_items_from_string", methods=["GET"])
def api_parse_items_from_string(version):
    all_crafting_data = calculator.data.get_all_crafting_data(
        version, force_create=app.debug
    )
    input_strs = [
        "Observer: 334",
        "Redstone Dust: 287",
        "Piston: 240",
        "Stained Glass: 171",
        "Sticky Piston: 153",
        "Hopper: 130",
        "Glazed Terracotta: 110",
        "Honey Block: 100",
        "Redstone Repeater: 85",
        "Slime Block: 79",
        "Note Block: 76",
        "Birch Fence Gate: 62",
        "Water Bucket: 56",
        "Dropper: 53",
        "Block of Redstone: 50",
        "Powered Rail: 42",
        "Redstone Torch: 26",
        "Redstone Comparator: 24",
        "Chest: 22",
        "Iron Trapdoor: 16",
        "Carpet: 15",
        "Dispenser: 7",
        "Stone Button: 7",
        "Sand: 4",
        "Obsidian: 3",
        "White Shulker Box: 3",
        "Lever: 2",
        "Redstone Lamp: 2",
        "Cauldron: 1",
        "Dirt: 1",
        "Flower Pot: 1",
        "Spruce Sapling: 1",
        "White Wool: 1",
    ]
    return calculator.utils.parse_items_from_string(input_strs, all_crafting_data)


@app.route("/api/<version>/calculate_resources", methods=["GET"])
def api_calculate_resources(version):
    all_crafting_data = calculator.data.get_all_crafting_data(
        version, force_create=app.debug
    )
    have_already = {
        "oak_log": 5,
    }
    path = {
        0: {
            "name": "torch",
            "recipe": "torch",
            "ingredients": {
                0: {
                    "name": "charcoal",
                    "recipe": "charcoal",
                    "ingredients": {0: {"name": "dark_oak_log"}},
                },
                1: {
                    "name": "stick",
                    "recipe": "stick",
                    "ingredients": {
                        0: {
                            "name": "dark_oak_planks",
                            "recipe": "dark_oak_planks",
                            "ingredients": {0: {"name": "dark_oak_log"}},
                        }
                    },
                },
            },
        },
        3: {"name": "orange_carpet",},
    }

    all_crafting_data = calculator.data.get_all_crafting_data(
        version, force_create=app.debug
    )
    input_strs = [
        "Observer: 334",
        "Redstone Dust: 287",
        "Piston: 240",
        "Stained Glass: 171",
        "Sticky Piston: 153",
        "Hopper: 130",
        "Glazed Terracotta: 110",
        "Honey Block: 100",
        "Redstone Repeater: 85",
        "Slime Block: 79",
        "Note Block: 76",
        "Birch Fence Gate: 62",
        "Water Bucket: 56",
        "Dropper: 53",
        "Block of Redstone: 50",
        "Powered Rail: 42",
        "Redstone Torch: 26",
        "Redstone Comparator: 24",
        "Chest: 22",
        "Iron Trapdoor: 16",
        "Carpet: 15",
        "Dispenser: 7",
        "Stone Button: 7",
        "Sand: 4",
        "Obsidian: 3",
        "White Shulker Box: 3",
        "Lever: 2",
        "Redstone Lamp: 2",
        "Cauldron: 1",
        "Dirt: 1",
        "Flower Pot: 1",
        "Spruce Sapling: 1",
        "White Wool: 1",
    ]
    parsed_items = calculator.utils.parse_items_from_string(
        input_strs, all_crafting_data
    )
    requested_items = parsed_items["items"]

    # requested_items = [
    #     {"name": "torch"},
    #     [{"name": "coal"}, {"name": "charcoal"}, {"tag": "planks"}],
    # ]
    # requested_items = [{"tag": "planks"}]
    # requested_items = [
    #     {"name": "torch", "amount_required": 1},
    #     {"name": "light_blue_concrete_powder", "amount_required": 2},
    #     {"name": "red_bed", "amount_required": 3},
    #     {"name": "blue_dye", "amount_required": 4},
    #     {"name": "purple_stained_glass_pane", "amount_required": 5},
    # ]
    # requested_items = [
    #     {"name": "observer", "amount_required": 8},
    #     {"name": "redstone", "amount_required": 3},
    #     {"name": "comparator", "amount_required": 2},
    #     {"name": "hopper", "amount_required": 5},
    # ]
    # requested_items = [
    #     {"name": item_name}
    #     for item_name in all_crafting_data["supported_craftable_items"]
    # ]
    recipe_tree = calculator.calculator.create_recipe_tree(
        all_crafting_data["recipes"],
        all_crafting_data["tags"],
        all_crafting_data["supported_recipes"],
        requested_items,
        parse_item=True,
    )

    shopping_list = calculator.calculator.create_shopping_list(
        recipe_tree, path=path, have_already=have_already
    )

    return jsonify({"recipe_tree": recipe_tree, "shopping_list": shopping_list,})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="5000")
