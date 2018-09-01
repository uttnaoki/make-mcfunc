from PIL import Image
import math

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

    for k, v in sorted(img_pixel_colors.items(),  key=lambda x: -x[1]):
        print(k, v)

    # ピクセル数の多い色順にピクセルを並べた画像を作成
    make_color_map(output_img_size, img_pixel_colors, 'color_map.png')

if __name__ == '__main__':
    main('pikachu.png')
