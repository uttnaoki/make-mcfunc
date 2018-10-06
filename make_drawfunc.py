from PIL import Image
import os
import math
import numpy as np
import mcblock

# 入力画像を配置するディレクトリ
source_img_dir = 'source_img'
# 処理の過程で作成される画像を出力するディレクトリ
output_img_dir = 'output_pngs'
# マイクラ用スクリプトを出力するディレクトリ
mcfunc_dir = 'functions'

# 出力画像のサイズ
output_img_longside = 100


# カラーコード文字列をRGBのタプルに変換する．
def cc2rgb (colorcode):
    r = int(colorcode[1:3], 16)
    g = int(colorcode[3:5], 16)
    b = int(colorcode[5:7], 16)
    return (r,g,b)

# 入力画像を指定のRGBセットで再描画する
def redraw (base_img, rgb_set, filename):
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
    # 画像の各ピクセルの色を usable_rgb の色に修正し，修正後のRGBのインデックスを取得
    used_rgb_indexes = [mod_one_pixel(x, y) for y in range(height) for x in range(width)]
    # 修正後の画像を保存
    base_img.save(filename)

    # 再描画に使ったRGBのインデックスを返却
    return used_rgb_indexes

# マイクラ上の特定の座標にブロックを設置するコマンドを取得
def get_command (block_name, index, canvas_size, transform):
    x = index%canvas_size[0] + transform['x']
    y = -(index//canvas_size[1]) + transform['y']
    return 'setblock ~{0} ~{1} ~ {2}'.format(x, y, block_name)

# 画像をマイクラ上で描画するためのコマンドセットを取得
def get_command_set (block_names, selected_block_indexes, canvas_size):
    transform = {
        'x': -(canvas_size[0]//2),
        'y': canvas_size[1]+3
    }
    return [get_command(block_names[selected_block_indexes[i]], i, canvas_size, transform) for i in range(len(selected_block_indexes))]

def main (source_img_path):
    # 入力画像をリサイズ
    img = Image.open(source_img_path, 'r')
    # 入力画像の長辺を取得
    source_img_longside = max(img.size)
    # 入力画像のリサイズ係数を取得
    resize_coef = source_img_longside / output_img_longside
    # リサイズ後のサイズを取得
    output_img_size = (math.ceil(img.size[0]/resize_coef), math.ceil(img.size[1]/resize_coef))
    # 入力画像をリサイズ
    resized_img = img.resize(output_img_size)
    # RGBに変換
    rgb_img = resized_img.convert('RGB')

    # 画像名を取得
    source_img_name = source_img_path.split('/')[-1]
    # 画像名の拡張子じゃない方を取得
    source_img_basename = source_img_name.split('.')[0]

    # 羊毛ブロックの名前(ID)を抽出
    wool_names = [name for name in mcblock.wool_colorcode]
    # 羊毛ブロックのRGBを抽出
    usable_rgb_set = [cc2rgb(cc) for cc in mcblock.wool_colorcode.values()]

    # usable_rgb_set で表現した画像を保存し，使われたRGBのindexを取得
    used_rgb_indexes = redraw(rgb_img, usable_rgb_set, '{0}/{1}_wool.png'.format(output_img_dir, source_img_basename))
    # 再描画後の画像をマイクラで描画するためのコマンドセットを取得
    command_set = get_command_set(wool_names, used_rgb_indexes, output_img_size)

    # 出力するマイクラ用スクリプトのパス名を取得
    mcfunc_path = '{0}/draw_{1}.mcfunction'.format(mcfunc_dir, source_img_basename)
    # マイクラ用スクリプトを出力
    with open(mcfunc_path, 'w', encoding='utf-8') as f:
        [f.write('{0}\n'.format(c)) for c in command_set]

if __name__ == '__main__':
    # 入力画像名を取得
    img_names = os.listdir(source_img_dir)
    # img_names = ['img.png']

    # 各入力画像に対して処理を実行
    for img_name in img_names:
        main('{0}/{1}'.format(source_img_dir, img_name))
