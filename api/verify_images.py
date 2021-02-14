import json
import glob
import cookbook

for version in ['1.15', '1.16']:
    items = set(cookbook.data.fetch_all_items(version, force_create=True))
    images = set([f.split('/')[-1].split('.png')[0] for f in glob.glob(f'../app/src/assets/minecraft/{version}/32x32/*.png')])

    all_items_without_images = items - images
    all_images_without_items = images - items

    print('=====', version, '=====')
    print('all_items_without_images =>', all_items_without_images)
    assert len(all_items_without_images) == 0
    print('all_images_without_items =>', all_images_without_items)
    assert len(all_images_without_items) == 0
    print('\n')
