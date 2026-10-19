#!/usr/bin/env python3

import os

path = './src/pacman/app/images/bg-frames'
dir_list = sorted(os.listdir(path))

for i, file in enumerate(dir_list):
    # print(file[file.find('_') + 1:file.find('.')])
    print(f'{i}: {file} | Is correct order? {int(file[6:9]) == i}')
    os.rename(f'{path}/{file}', f'{path}/frame_{i}.gif')
