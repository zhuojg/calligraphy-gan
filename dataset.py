import tensorflow as tf
import os
import pathlib
import numpy as np
from config import config


class CalligraphyDataset:
    def _process_path(self, file_path):
        img = tf.io.read_file(file_path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.rgb_to_grayscale(img)
        img = tf.cast(img, dtype=tf.int32)
        img = tf.math.abs(img - 255)
        img = tf.cast(img, dtype=tf.uint8)
        img = tf.image.resize_with_pad(
            img, target_height=224, target_width=224)
        img = (img - 127.5) / 127.5

        character = tf.strings.split(file_path, os.sep)[-2]

        # character = self.characters[character.decode('utf-8')]
        # character = tf.one_hot(character, depth=config.class_dim)
        # character = tf.reshape(character, shape=[1, 1, config.class_dim])
        # character = tf.cast(character, dtype=tf.float32)

        return img, character

    def _get_embedding(self, character_csv):
        characters = {}

        with open(character_csv, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                characters[line.split(',')[0]] = int(line.split(',')[1])

        return characters

    def __init__(self, data_dir, character_csv, batch_size=1, repeat=True, shuffle=True, shuffle_buffer_size=32):
        self.characters = self._get_embedding(character_csv)

        data_dir = pathlib.Path(data_dir)
        list_ds = tf.data.Dataset.list_files(str(data_dir / '*/*.jpg'))

        self.length = len(list_ds)
        self.class_num = len(os.listdir(data_dir))
        print('Found %d images in %d classes.' % (self.length, self.class_num))

        labeled_ds = list_ds.map(self._process_path)

        dataset = labeled_ds

        if shuffle:
            dataset = dataset.shuffle(
                buffer_size=shuffle_buffer_size, reshuffle_each_iteration=True)

        if repeat:
            dataset = dataset.repeat()

        dataset = dataset.batch(batch_size=batch_size)

        self.dataset = dataset

        # self.dataset = dataset.as_numpy_iterator()

    def __len__(self):
        return self.length

    # def next(self):
    #     (img, characters) = self.dataset.next()

    #     characters = np.array(
    #         [self.characters[item.decode('utf-8')] for item in characters])

    #     return img, characters
