import os
import shutil
import time

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
cut_size = 512
out_path = '../dataset'
used_bands = ['B10', 'B20', 'B30', 'B40', 'B50', 'B70']


def create_subimages_folders(location, instance_id, img_size):
    for x in range(0, img_size[0] - cut_size - 1, cut_size):
        for y in range(0, img_size[1] - cut_size - 1, cut_size):
            path = '{}/{}/{}/{}'.format(out_path, location, instance_id, '{},{}'.format(x, y))
            os.mkdir(path)


def cut_image(image, location, instance_id, image_name):
    for x in range(0, image.size[0] - cut_size - 1, cut_size):
        for y in range(0, image.size[1] - cut_size - 1, cut_size):
            cropped = image.crop((x, y, x + cut_size, y + cut_size))
            path = '{}/{}/{}/{}/{}'.format(out_path, location, instance_id, '{},{}'.format(x, y), image_name)
            cropped.save(path)


def cut_images(location, instance_id, bands_images):
    for band_file in bands_images:
        path = 'data/{}/{}/{}'.format(location, instance_id, band_file)
        image = Image.open(path)
        cut_image(image, location, instance_id, band_file)


def cut_mask(location, instance_id, mask_file):
    path = 'data/{}/{}/{}'.format(location, instance_id, mask_file)
    mask = Image.open(path)
    create_subimages_folders(location, instance_id, mask.size)
    new_mask = Image.new(mask.mode, mask.size)
    iter_mask = mask.load()
    iter_new_mask = new_mask.load()
    for x in range(mask.size[0]):
        for y in range(mask.size[1]):
            iter_new_mask[x, y] = 0 if iter_mask[x, y] <= 128 else 255

    cut_image(new_mask, location, instance_id, mask_file)


def main():
    _time = time.time()

    shutil.rmtree(out_path, ignore_errors=True)
    os.mkdir(out_path)
    for location in [d for d in os.listdir('data') if os.path.isdir('data/' + d)]:
        print('Processing: ' + location, end='... ')
        os.mkdir('{}/{}'.format(out_path, location))
        location_dir = os.path.join('data', location)

        for instance_id in [d for d in os.listdir(location_dir) if os.path.isdir(location_dir + '/' + d)]:
            os.mkdir('{}/{}/{}'.format(out_path, location, instance_id))
            instance_dir = os.path.join(location_dir, instance_id)

            bands_files = []
            mask_file = None

            for file in os.listdir(instance_dir):
                if file[-7:-4] in used_bands:
                    bands_files.append(file)
                elif 'mask' in file and (file.endswith('.tif') or file.endswith('.TIF')):
                    mask_file = file

            cut_mask(location, instance_id, mask_file)
            cut_images(location, instance_id, bands_files)

        print("Processed.")
    _time = time.time() - _time
    _time = int(_time * 100) / 100

    print("Execution Time: " + str(_time) + " s")


if __name__ == "__main__":
    main()
