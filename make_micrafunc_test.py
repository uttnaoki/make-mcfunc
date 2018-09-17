import os
import micrablock_name as block_name

funcdir_path = 'functions'

funcfile_path = '{0}/func50.mcfunction'.format(funcdir_path)

canvas_width = 50
canvas_height = 50
block_num = len(block_name.wool)
transform = {
    'x': -(canvas_width//2),
    'y': canvas_height+3
}

def get_block_name (x, y):
    return block_name.wool[(canvas_width*y + x)%block_num]

def get_command (x, y):
    tx = x + transform['x']
    ty = -y + transform['y']
    return 'setblock ~{0} ~{1} ~ {2}'.format(tx, ty, get_block_name(x, y))

commands = [get_command(x, y) for y in range(canvas_height) for x in range(canvas_width)]


with open(funcfile_path, 'w', encoding='utf-8') as f:
    [f.write('{0}\n'.format(c)) for c in commands]
