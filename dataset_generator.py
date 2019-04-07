import os
import shutil
import time
import re

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
cut_size = 512
data_path = 'landsat8_sample'
out_path = '../dataset'
used_bands = ['1', '2', '3', '4', '5', '6', '7', '9', '10', '11', 'QA']


def cut_image(image, location, instance_id, image_name, points):
    for x, y in points:
        cropped = image.crop((x, y, x + cut_size, y + cut_size))
        path = '{}/{}/{}/{}/{}'.format(out_path, location, instance_id, '{},{}'.format(x, y), image_name)
        cropped.save(path)


def cut_images(location, instance_id, bands_images, points):
    for band_file in bands_images:
        path = '{}/{}/{}/{}'.format(data_path, location, instance_id, band_file)
        image = Image.open(path)
        cut_image(image, location, instance_id, band_file, points)


def get_valid_subimage_points(location, instance_id, mask_file):
    points = []

    path = '{}/{}/{}/{}'.format(data_path, location, instance_id, mask_file)
    mask = Image.open(path)
    iter_mask = mask.load()
    for x in range(0, mask.size[0] - cut_size - 1, cut_size):
        for y in range(0, mask.size[1] - cut_size - 1, cut_size):
            if iter_mask[x, y] != 0 and iter_mask[x + cut_size, y] != 0 and iter_mask[x, y + cut_size] != 0 and iter_mask[x + cut_size, y + cut_size] != 0:
                points.append((x, y))
                os.mkdir('{}/{}/{}/{},{}'.format(out_path, location, instance_id, x, y))

    return points


def cut_mask(location, instance_id, mask_file, points):
    path = '{}/{}/{}/{}'.format(data_path, location, instance_id, mask_file)
    mask = Image.open(path)
    new_mask = Image.new(mask.mode, mask.size)
    iter_mask = mask.load()
    iter_new_mask = new_mask.load()
    for x in range(mask.size[0]):
        for y in range(mask.size[1]):
            # iter_new_mask[x, y] = 0 if iter_mask[x, y] <= 128 else 255
            iter_new_mask[x, y] = iter_mask[x, y]

    cut_image(new_mask, location, instance_id, mask_file, points)


def main():
    _time = time.time()

    shutil.rmtree(out_path, ignore_errors=True)
    os.mkdir(out_path)
    for location in [d for d in os.listdir(data_path) if os.path.isdir('{}/{}'.format(data_path, d))]:
        print('Processing: ' + location, end='... ')
        os.mkdir('{}/{}'.format(out_path, location))
        location_dir = os.path.join(data_path, location)

        for instance_id in [d for d in os.listdir(location_dir) if os.path.isdir(location_dir + '/' + d)]:
            os.mkdir('{}/{}/{}'.format(out_path, location, instance_id))
            instance_dir = os.path.join(location_dir, instance_id)

            bands_files = []
            mask_file = None

            for file in os.listdir(instance_dir):
                rex = re.search(r"(?<=_B)\d{1,2}|(QA)(?=\.TIF)", file)
                if rex and rex.group() in used_bands:
                    bands_files.append(file)
                elif file.endswith('_fixedmask.tif'):
                    mask_file = file
            points = get_valid_subimage_points(location, instance_id, mask_file)
            cut_mask(location, instance_id, mask_file, points)
            cut_images(location, instance_id, bands_files, points)

        print("Processed.")
    _time = time.time() - _time
    _time = int(_time * 100) / 100

    print("Execution Time: " + str(_time) + " s")


if __name__ == "__main__":
    main()
