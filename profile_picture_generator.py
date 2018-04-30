import png_lib
from random import randint



#https://stackoverflow.com/a/43235/7018899
def random_color(color_mask = None):
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    if color_mask:
        r = int((r + color_mask[0])/2)
        g = int((g + color_mask[0])/2)
        b = int((b + color_mask[0])/2)
    return (r, g, b)

def gen_profile_pic(width, height, color_mask=None, background=(0, 0, 0, 0), 
                    color_probability = 50):
    png_data = []
    color = (*random_color(color_mask), 255)
    mid_index = (width - 1)/2
    for i in range(height):
        png_data.append([])
        for j in range(width):
            if j < width/2:
                if randint(0, 99) < color_probability:
                    png_data[i].append(color)
                else:
                    png_data[i].append(background)
            else:
                png_data[i].append(png_data[i][int(2 * mid_index - j)])
    profile_pic = png_lib.png(data = png_data)
    #import pdb;pdb.set_trace()
    return profile_pic

def gen_filenames(quantity):
    from uuid import uuid4
    filenames = []
    for i in range(quantity):
        filenames.append("picgen_" + str(uuid4().hex) + ".png")
    return filenames

def main():
    from sys import argv
    from os import makedirs, path
    dir = "tmp_profile_pic"
    makedirs(dir, exist_ok = True)
    try:
        filenames = gen_filenames(int(argv[1]))
    except IndexError:
        filenames = gen_filenames(5)
    for filename in filenames:
        filename = path.join(dir, filename)
        profile_pic = gen_profile_pic(12, 12, (255, 255, 255), 
                                      (255, 255, 255, 255), 40)
        profile_pic.enlarge_pixel_data(16)
        profile_pic.smart_create(filename = filename)
    
    print("created %d png(s)" % len(filenames))


if __name__=="__main__":
    main()