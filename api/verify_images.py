import json
import glob
import cookbook

for version in [1.15, 1.16, 1.17, 1.18]:
    items = set(cookbook.data.fetch_all_items(version, force_create=True))
    img_path = f'../app/src/assets/minecraft/{version}/32x32/*.png'
    images = set([f.split('/')[-1].split('.png')[0] for f in glob.glob(img_path)])
    images -= set(cookbook.constants.EXCLUDED_ITEMS)

    all_items_without_images = items - images
    all_images_without_items = images - items

    print('=====', version, '=====')
    print('all_items_without_images =>', all_items_without_images)
    print('all_images_without_items =>', all_images_without_items)
    assert len(all_items_without_images) == 0
    assert len(all_images_without_items) == 0
    print('\n')
