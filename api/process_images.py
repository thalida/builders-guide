from pathlib import Path
import os
import sys
import shutil

def fix_image_name(s):
    s = s.lower().replace(' ', '_')

    while '__' in s:
        s = s.replace('__', '_')

    while '_.' in s:
        s = s.replace('_.', '.')

    return s


def rename_item(filename, version):
    item = filename.split('.png')[0]
    map = {}
    map[version] = {}

    map[1.15] = {
        'arrow_of_fire_resistance': 'tipped_arrow',
        'banner_pattern_2': 'creeper_banner_pattern',
        'banner_pattern_3': 'skull_banner_pattern',
        'banner_pattern_4': 'mojang_banner_pattern',
        'banner_pattern_5': 'globe_banner_pattern',
        'banner_pattern_6': 'piglin_banner_pattern',
        'banner_pattern': 'flower_banner_pattern',
        'block_of_coal': 'coal_block',
        'block_of_diamond': 'diamond_block',
        'block_of_emerald': 'emerald_block',
        'block_of_gold': 'gold_block',
        'block_of_iron': 'iron_block',
        'block_of_quartz': 'quartz_block',
        'block_of_redstone': 'redstone_block',
        'book_and_quill': 'writable_book',
        'bucket_of_cod': 'cod_bucket',
        'bucket_of_pufferfish': 'pufferfish_bucket',
        'bucket_of_salmon': 'salmon_bucket',
        'bucket_of_tropical_fish': 'tropical_fish_bucket',
        'clay_2': 'clay_ball',
        'dragon_s_breath': 'dragon_breath',
        'empty_map': 'map',
        'eye_of_ender': 'ender_eye',
        'hay_bale': 'hay_block',
        'lapis_lazuli_block': 'lapis_block',
        'lapis_lazuli_ore': 'lapis_ore',
        'leather_cap': 'leather_helmet',
        'leather_pants': 'leather_leggings',
        'leather_tunic': 'leather_chestplate',
        'minecart_with_chest': 'chest_minecart',
        'minecart_with_furnace': 'furnace_minecart',
        'minecart_with_hopper': 'hopper_minecart',
        'minecart_with_tnt': 'tnt_minecart',
        'music_disc_10': 'music_disc_strad',
        'music_disc_11': 'music_disc_wait',
        'music_disc_12': 'music_disc_ward',
        'music_disc_14': 'music_disc_pigstep',
        'music_disc_2': 'music_disc_13',
        'music_disc_3': 'music_disc_blocks',
        'music_disc_4': 'music_disc_cat',
        'music_disc_5': 'music_disc_chirp',
        'music_disc_6': 'music_disc_far',
        'music_disc_7': 'music_disc_mall',
        'music_disc_8': 'music_disc_mellohi',
        'music_disc_9': 'music_disc_stal',
        'music_disc': 'music_disc_11',
        'nether_quartz': 'quartz',
        'rabbit_s_foot': 'rabbit_foot',
        'raw_beef': 'beef',
        'raw_chicken': 'chicken',
        'raw_cod': 'cod',
        'raw_mutton': 'mutton',
        'raw_porkchop': 'porkchop',
        'raw_rabbit': 'rabbit',
        'raw_salmon': 'salmon',
        'redstone_comparator': 'comparator',
        'redstone_dust': 'redstone',
        'redstone_repeater': 'repeater',
        'slimeball': 'slime_ball',
        'steak': 'cooked_beef',
        'turtle_shell': 'turtle_helmet',
        'vines': 'vine',
    }

    map[1.16] = map[1.15].copy()
    map[1.16]['banner_pattern_1'] = 'creeper_banner_pattern'
    map[1.16]['banner_pattern_2'] = 'skull_banner_pattern'
    map[1.16]['banner_pattern_3'] = 'mojang_banner_pattern'
    map[1.16]['banner_pattern_4'] = 'globe_banner_pattern'
    map[1.16]['banner_pattern_5'] = 'piglin_banner_pattern'
    map[1.16]['banner_pattern'] = 'flower_banner_pattern'
    map[1.16]['block_of_netherite'] = 'netherite_block'
    map[1.16]['smooth_quartz_block'] = 'smooth_quartz'
    del map[1.16]['banner_pattern_6']

    map[1.16]['music_disc'] = 'music_disc_13'
    map[1.16]['music_disc_1'] = 'music_disc_cat'
    map[1.16]['music_disc_2'] = 'music_disc_blocks'
    map[1.16]['music_disc_3'] = 'music_disc_chirp'
    map[1.16]['music_disc_4'] = 'music_disc_far'
    map[1.16]['music_disc_5'] = 'music_disc_mall'
    map[1.16]['music_disc_6'] = 'music_disc_mellohi'
    map[1.16]['music_disc_7'] = 'music_disc_stal'
    map[1.16]['music_disc_8'] = 'music_disc_strad'
    map[1.16]['music_disc_9'] = 'music_disc_ward'
    map[1.16]['music_disc_11'] = 'music_disc_wait'
    map[1.16]['music_disc_10'] = 'music_disc_11'
    map[1.16]['music_disc_12'] = 'music_disc_pigstep'
    del map[1.16]['music_disc_14']

    if item in map[version]:
        return map[version][item] + '.png'

    return filename


def process_images(version):
    version = float(version)
    pathlist = Path(f'../app/src/assets/minecraft/{version}').glob('**/*.png')
    remove_items = {
        '_potion',
        '_spawn_egg',
        'arrow_of_',
        'bottle_o_enchanting',
        'enchanted_book_',
        'potion_of_',
        'water_bottle',
    }
    copy_images = {
        1.18: {
            'music_disc_wait': 'music_disc_otherside',
        }
    }
    for path in pathlist:
        filename = str(path).split('/')[-1]
        new_filename = fix_image_name(filename)
        new_filename = rename_item(new_filename, version)

        should_remove_item = any(search in new_filename for search in remove_items)
        if should_remove_item:
            print(f'Removing {new_filename}')
            os.remove(path)
            continue

        new_path = Path('/'.join(str(path).split('/')[:-1]) + '/' + new_filename)
        if path == new_path:
            print(f'Skipping, file exists {new_path}')
            continue

        print(f'Renaming {path} to {new_path}')
        os.rename(path, new_path)

    if version in copy_images:
        print(f'Copying images for {version}')
        for item in copy_images[version]:
            for resolution in ['32x32', '64x64', '128x128']:
                old_path = Path(f'../app/src/assets/minecraft/{version}/{resolution}/{item}.png')
                new_path = Path(f'../app/src/assets/minecraft/{version}/{resolution}/{copy_images[version][item]}.png')
                if old_path.exists():
                    print(f'Copying {old_path} to {new_path}')
                    shutil.copy(old_path, new_path)

game_version = sys.argv[1]
print(f'Processing images for {game_version}...')
process_images(game_version)
