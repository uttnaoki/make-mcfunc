from PIL import Image
import math
import numpy as np
import mcblock

funcdir_path = 'functions'

# カラーコード文字列をRGBのタプルに変換する．
def cc2rgb (colorcode):
    r = int(colorcode[1:3], 16)
    g = int(colorcode[3:5], 16)
    b = int(colorcode[5:7], 16)
    return (r,g,b)

def resize_img (filename, size_tuple):
    # 既存ファイルを readモードで読み込み
    img = Image.open(filename, 'r')

    # リサイズ。サイズは幅と高さをtupleで指定
    return img.resize(size_tuple)

def reduce_img_color (base_img, rgb_set, filename):
    # rgbの距離(norm)を計算するためにnumpyの配列に変換
    rgb_set = np.array(rgb_set)
    rgb_set_len = len(rgb_set)

    # usable_rgb の中から最も this_rgb に近いものを返す
    def get_nearest_rgb_from_usable (this_rgb, usable_rgb):
        this_rgb = np.array(this_rgb)
        norm_set = [np.linalg.norm(this_rgb - rgb_set[i]) for i in range(rgb_set_len)]
        min_index = np.argmin(norm_set)
        return tuple(usable_rgb[min_index]), min_index

    # 指定されたピクセル(座標)の色を usable_rgb の色に修正する
    def mod_one_pixel (x, y):
        r,g,b = base_img.getpixel((x, y))
        modified_rgb, index = get_nearest_rgb_from_usable([r,g,b], rgb_set)
        base_img.putpixel((x, y), modified_rgb)
        return index

    # 画像の幅と高さを取得
    width, height = base_img.size
    # 画像の各ピクセルの色を usable_rgb の色に修正し，修正後のRGBを取得
    used_rgb_indexes = [mod_one_pixel(x, y) for y in range(height) for x in range(width)]
    # 修正後の画像を保存
    base_img.save(filename)

    return used_rgb_indexes

def get_command (block_name, index, canvas_size, transform):
    x = index%canvas_size[0] + transform['x']
    y = -(index//canvas_size[1]) + transform['y']
    return 'setblock ~{0} ~{1} ~ {2}'.format(x, y, block_name)

def get_command_set (block_names, selected_block_indexes, canvas_size):
    transform = {
        'x': -(canvas_size[0]//2),
        'y': canvas_size[1]+3
    }
    return [get_command(block_names[selected_block_indexes[i]], i, canvas_size, transform) for i in range(len(selected_block_indexes))]

def main (source_img_name):
    # 羊毛ブロックの名前(ID)を抽出
    wool_names = [name for name in mcblock.wool_colorcode]
    # 羊毛ブロックのRGBを抽出
    usable_rgb_set = [cc2rgb(cc) for cc in mcblock.wool_colorcode.values()]

    # 出力画像のサイズ
    output_img_size = (100, 100)

    # 入力画像をリサイズ
    resized_img = resize_img(source_img_name, output_img_size)
    # RGBに変換
    rgb_img = resized_img.convert('RGB')

    # usable_rgb_set で表現した画像を保存し，使われたRGBとそのindexを取得．
    used_rgb_indexes = reduce_img_color(rgb_img, usable_rgb_set, 'wool_mode.png')

    command_set = get_command_set(wool_names, used_rgb_indexes, output_img_size)
    funcfile_path = '{0}/draw_pikachu.mcfunction'.format(funcdir_path)
    with open(funcfile_path, 'w', encoding='utf-8') as f:
        [f.write('{0}\n'.format(c)) for c in command_set]

if __name__ == '__main__':
    main('pikachu.png')
