# builder's guide

# TODO

- [x] add support for minecraft versions
- [x] remove unsupported recipe types for recipe lists
- [x] require the right amount of ingredients for what's required
- [x] require the right amount of ingredients for what's required
- [x] store remaining per history
- [x] add better support for recursive ingredients for nested tags in tags
- [x] find images for all items (thanks xtream1101)
- [x] convert into proper api
  - [x] partially proper need to make it better
- [x] add comments and better documentation
- [x] figure out what to do about groups of items ("carpet", "stained glass")
- [x] add tests
  - [ ] add better tests
- [ ] setup vue frontend
- [ ] add image data
- [ ] design the site
- [ ] netlify hosting! / self-hosting(?)

# Don't Look

requested_items = [
{"name": "torch"},
[{"name": "coal"}, {"name": "charcoal"}, {"tag": "planks"}],
]

requested_items = [{"tag": "planks"}]
requested_items = [
{"name": "torch", "amount_required": 1},
{"name": "light_blue_concrete_powder", "amount_required": 2},
{"name": "red_bed", "amount_required": 3},
{"name": "blue_dye", "amount_required": 4},
{"name": "purple_stained_glass_pane", "amount_required": 5},
]

requested_items = [
{"name": "observer", "amount_required": 8},
{"name": "redstone", "amount_required": 3},
{"name": "comparator", "amount_required": 2},
{"name": "hopper", "amount_required": 5},
]

requested_items = [
{"name": item_name}
for item_name in all_crafting_data["supported_craftable_items"]
]

30 Torches
5 glass panes

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
