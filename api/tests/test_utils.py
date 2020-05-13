import os
import pytest

import cookbook.utils
import cookbook.data

file_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(file_dir, "../cookbook/data",)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("minecraft:item_frame", "item_frame"),
        ("custom:red_dye", "red_dye"),
        ("minecart", "minecart"),
        ("", ""),
    ],
)
def test__parse_item_name(test_input, expected):
    output = cookbook.utils.parse_item_name(test_input)
    assert output == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("#minecraft:item_frame", True),
        ("custom:red_dye", False),
        ("minecraft:minecart", False),
        ("", False),
    ],
)
def test__is_tag_name(test_input, expected):
    output = cookbook.utils.is_tag_name(test_input)
    assert output == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"type": "cookbook:naturally_occurring"}, True),
        ({"type": "minecraft:blasting"}, False),
        ({"type": "minecraft:campfire_cooking"}, False),
        ({"type": "minecraft:crafting_shaped"}, False),
        ({"type": "minecraft:crafting_shapeless"}, False),
        ({"type": "minecraft:smelting"}, False),
        ({"type": "minecraft:smoking"}, False),
        ({"type": "minecraft:stonecutting"}, False),
        ({"type": "minecraft:crafting_special_bookcloning"}, False),
        ({"type": "minecraft:crafting_special_firework_star_fade"}, False),
        ({"type": "minecraft:crafting_special_firework_rocket"}, False),
        ({"type": "minecraft:crafting_special_shulkerboxcoloring"}, False),
        ({"type": "minecraft:crafting_special_mapcloning"}, False),
        ({"type": "minecraft:crafting_special_repairitem"}, False),
        ({"type": "minecraft:crafting_special_bannerduplicate"}, False),
        ({"type": "minecraft:crafting_special_armordye"}, False),
        ({"type": "minecraft:crafting_special_tippedarrow"}, False),
        ({"type": "minecraft:crafting_special_firework_star"}, False),
        ({"type": "minecraft:crafting_special_mapextending"}, False),
        ({"type": "minecraft:crafting_special_shielddecoration"}, False),
        ({"type": "minecraft:crafting_special_suspiciousstew"}, False),
        ({"type": ""}, False),
    ],
)
def test__is_custom_recipe(test_input, expected):
    output = cookbook.utils.is_custom_recipe(test_input)
    assert output == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"type": "cookbook:naturally_occurring"}, True),
        ({"type": "minecraft:blasting"}, True),
        ({"type": "minecraft:campfire_cooking"}, True),
        ({"type": "minecraft:crafting_shaped"}, True),
        ({"type": "minecraft:crafting_shapeless"}, True),
        ({"type": "minecraft:smelting"}, True),
        ({"type": "minecraft:smoking"}, True),
        ({"type": "minecraft:stonecutting"}, True),
        ({"type": "minecraft:crafting_special_bookcloning"}, False),
        ({"type": "minecraft:crafting_special_firework_star_fade"}, False),
        ({"type": "minecraft:crafting_special_firework_rocket"}, False),
        ({"type": "minecraft:crafting_special_shulkerboxcoloring"}, False),
        ({"type": "minecraft:crafting_special_mapcloning"}, False),
        ({"type": "minecraft:crafting_special_repairitem"}, False),
        ({"type": "minecraft:crafting_special_bannerduplicate"}, False),
        ({"type": "minecraft:crafting_special_armordye"}, False),
        ({"type": "minecraft:crafting_special_tippedarrow"}, False),
        ({"type": "minecraft:crafting_special_firework_star"}, False),
        ({"type": "minecraft:crafting_special_mapextending"}, False),
        ({"type": "minecraft:crafting_special_shielddecoration"}, False),
        ({"type": "minecraft:crafting_special_suspiciousstew"}, False),
        ({"type": ""}, False),
    ],
)
def test__is_supported_recipe(test_input, expected):
    output = cookbook.utils.is_supported_recipe(test_input)
    assert output == expected


# @pytest.mark.parametrize(
#     "test_input,expected",
#     [
#         ("hopper minecart", "hopper_minecart"),
#         # ("torches", "torch"),
#         # ("redstone_dust", "redstone"),
#         # ("redstone-repeaters", "repeater"),
#         # ("Cyan Terracotta", "cyan_terracotta"),
#         # ("acacia trapdoors", "acacia_trapdoor"),
#         # ("", ""),
#     ],
# )
# def test__generate_correct_item_name(test_input, expected):
#     all_crafting_data = cookbook.data.get_all_crafting_data(
#         "1.15", force_create=False
#     )
#     print("here", data_dir)

#     output = cookbook.utils.generate_correct_item_name(
#         test_input,
#         all_crafting_data["item_mappings"],
#         all_crafting_data["items"],
#         all_crafting_data["tags"],
#         all_crafting_data["recipes"],
#     )
#     assert output == expected
