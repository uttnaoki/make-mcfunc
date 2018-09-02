from PIL import Image
import math
import numpy as np

def resize_img (filename, size_tuple):
    # 既存ファイルを readモードで読み込み
    img = Image.open(filename, 'r')

    # リサイズ。サイズは幅と高さをtupleで指定
    return img.resize(size_tuple)

def count_pixel_colors (img):
    # 集計結果を格納する辞書配列
    img_pixel_colors = {}

    # 指定された座標のピクセルの RGB を取得し，そのRGBのカウンターをインクリメント
    def increment_color_counter (x, y):
        # (x,y)座標のピクセルの rgb を取得
        r,g,b = img.getpixel((x,y))
        # rgbを辞書配列のキーに使うために文字列化 (ex. 238-211-114)
        rgb = '-'.join([str(n) for n in [r,g,b]])
        # 取得した rgb が key になければ 値0 で追加
        img_pixel_colors.setdefault(rgb, 0)
        # 取得した rgb のカウンターをインクリメント
        img_pixel_colors[rgb] += 1

    # 画像の幅と高さを取得
    width, height = img.size
    # 画像に使われている色の数を集計し，辞書配列で img_pixel_colors に格納
    [increment_color_counter(x, y) for x in range(width) for y in range(height)]

    return img_pixel_colors

# ピクセル数の多い色順にピクセルを並べた画像を作成
def make_color_map (img_size, rgb_set, filename):
    img = Image.new('RGB', img_size)
    x=0
    y=0
    for rgb, count in sorted(rgb_set.items(),  key=lambda x: -x[1]):
        while count > 0:
            rgb_tuple = tuple([int(v) for v in rgb.split('-')])
            img.putpixel((x, y), rgb_tuple)
            x+=1
            if x == img_size[0]:
                x=0
                y+=1
            count-=1
    img.save(filename)

def make_less_color_img (base_img, rgb_set, filename):
    # rgbの距離(norm)を計算するためにnumpyの配列に変換
    rgb_set = np.array(rgb_set)
    rgb_set_len = len(rgb_set)

    # usable_rgb の中から最も this_rgb に近いものを返す
    def get_nearest_rgb_from_usable (this_rgb, usable_rgb):
        this_rgb = np.array(this_rgb)
        norm_set = [np.linalg.norm(this_rgb - rgb_set[i]) for i in range(rgb_set_len)]
        min_index = np.argmin(norm_set)
        return tuple(usable_rgb[min_index])

    # 指定されたピクセル(座標)の色を usable_rgb の色に修正する
    def mod_one_pixel (x, y):
        r,g,b = base_img.getpixel((x, y))
        base_img.putpixel((x, y), get_nearest_rgb_from_usable([r,g,b], rgb_set))

    # 画像の幅と高さを取得
    width, height = base_img.size
    # 画像の各ピクセルの色を usable_rgb の色に修正する
    [mod_one_pixel(x, y) for x in range(width) for y in range(height)]
    # 修正後の画像を保存
    base_img.save(filename)

def main (source_img_name):
    # 出力画像のサイズ
    output_img_size = (100, 100)

    # 画像をリサイズすることでモザイク画像を取得
    mosaic_img = resize_img(source_img_name, output_img_size)
    # 取得したモザイク画像を保存
    mosaic_img.save('mosaic_img.png', 'PNG', quality=100, optimize=True)

    # RGBに変換
    rgb_img = mosaic_img.convert('RGB')

    # 使われている色の種類を取得し，それらのピクセル数をカウント
    img_pixel_colors = count_pixel_colors(rgb_img)

    # for k, v in sorted(img_pixel_colors.items(),  key=lambda x: -x[1]):
    #     print(k, v)

    # ピクセル数の多い色順にピクセルを並べた画像を作成
    make_color_map(output_img_size, img_pixel_colors, 'color_map.png')

    def get_frequent_color (rgb_count):
        sorted_rgb_count = sorted(rgb_count.items(), key=lambda x: -x[1])
        return [list(map(int, rgb[0].split('-'))) for rgb in sorted_rgb_count]

    # リサイズ後の画像に使われている色の数を出力
    print('color_num: {0}'.format(len(img_pixel_colors)))

    # less_color.png で用いる色の数を定義
    usable_rgb_num = 30
    # 使用面積(頻度)の大きい色から usable_rgb_num の数分取ってくる
    usable_rgb_set = get_frequent_color(img_pixel_colors)[:usable_rgb_num]
    # usable_rgb_set の色だけで元画像(モザイク)を表現し，保存
    make_less_color_img(rgb_img, usable_rgb_set, 'less_color.png')

if __name__ == '__main__':
    main('pikachu.png')
