from PIL import Image
import PIL.ImageOps
import pytesseract
import cv2
import os
import sys
import hashlib

import torus


os.system("adb push inp      /data/local/tmp/inp");
os.system("adb shell chmod +x /data/local/tmp/inp");

#os.system("adb shell /data/local/tmp/inp tap 500 1520");
#os.system("adb shell /data/local/tmp/inp swipe 140 750 140 1540 0.1");
#sys.exit()

def get_digit(nu):
    h = hashlib.md5(nu.tobytes()).hexdigest()
    if h in get_digit.dict:
        d = get_digit.dict[h]
    else:
        # print(pytesseract.image_to_string(nu,
        #     config='--dpi 300 --psm 13 --tessdata-dir ./tess -l digits') ,pytesseract.image_to_string(nu,
        #         config='--dpi 300 --psm 13 --tessdata-dir ./tess -l digits').isdigit())
        temp=pytesseract.image_to_string(nu,
            config='--dpi 300 --psm 13 --tessdata-dir ./tess -l digits')
        temp=temp[0:1]
        # print(temp,temp.isdigit())
        if (temp.isdigit()):

            d = int(pytesseract.image_to_string(nu,
                config='--dpi 300 --psm 13 --tessdata-dir ./tess -l digits'))
            get_digit.dict[h] = d
            # print("hash miss! " + str(len(get_digit.dict)))
        else:
            return -1
    return d
get_digit.dict = {}

while True:

    os.system("adb exec-out screencap -p > scr.png")

    i = cv2.imread('scr.png')
    i = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)
    #threshold = 127 # to be determined
    #_, i_binarized = cv2.threshold(i, threshold, 255, cv2.THRESH_BINARY)
    #i = Image.fromarray(i_binarized)
    i = Image.fromarray(i)
    i = PIL.ImageOps.invert(i)
    # print(i)
    x0 = 66
    y0 = 850
    x1 = 1018
    y1 = 1804
    dx = (x1 - x0) / 6
    dy = (y1 - y0) / 6
    dd = 40

    M = [ [ 0 for x in range(6) ] for y in range(6) ]

    for x in range(0, 6):
        for y in range(0, 6):
            nu = i.crop((x0 + x * dx + dd, y0 + y * dy + dd, x0 + (x + 1) * dx - dd, y0 + (y + 1) * dy - dd))
            # nu.save("%d-%d.png" % (x,y))

            M[y][x] = get_digit(nu)

    print(M)

    # check that all numbers are present
    Mall = [item for sublist in M for item in sublist]
    Mall.sort()

    all_good = True
    for k in range(0, 36):
        if Mall[k] != k + 1:
            print("\n\n\nERROR\n\n\n")
            all_good = False

    if all_good:
        steps = torus.f(M)
        zip_steps = []
        zip_steps_num = []
        for st in range(len(steps)):
            if st > 0 and steps[st] == zip_steps[-1]:
                zip_steps_num[-1] = zip_steps_num[-1] + 1
            else:
                zip_steps.append(steps[st])
                zip_steps_num.append(1)

        #print(steps)
        #print(zip_steps)
        #print(zip_steps_num)
        print("executing %d swipes" % len(zip_steps))


        commands =""
        # commands = "cd /data/local/tmp/;\n"
        for st in range(len(zip_steps)):
            s = zip_steps[st]
            n = zip_steps_num[st]
            di = s[0]
            rc = int(s[1:])
            if di == "R":
                XX0 = x0 + dd
                YY0 = y0 + rc * dy + dd
                XX1 = XX0 + n * dx
                YY1 = YY0
            if di == "L":
                XX0 = x0 + 5 * dx + dd
                YY0 = y0 + rc * dy + dd
                XX1 = XX0 - n * dx
                YY1 = YY0
            if di == "U":
                XX0 = x0 + rc * dx + dd
                YY0 = y0 + 5 * dy + dd
                XX1 = XX0
                YY1 = YY0 - n * dy
            if di == "D":
                XX0 = x0 + rc * dx + dd
                YY0 = y0 + dd
                XX1 = XX0
                YY1 = YY0 + n * dy
            commands += "input swipe %d %d %d %d 150;" % (XX0, YY0, XX1, YY1)

        commands="adb shell \"" + commands + "\""
        # print(commands)
        os.system(commands);
        print("done\n")
        #sys.exit();

        os.system("timeout /t 1");
        # commands = "cd /data/local/tmp/;\n"
        # # Great! Claim * Stars
        commands = "input tap 527 1973;";
        commands += "sleep 1;";
        # # Play Torus Puzzle
        commands += "input tap 533 1691;";
        commands += "sleep 1;";
        # # Hard - * Stars   ---- using slow input so phone stays awake (?)
        commands += "input tap 532 1400;";
        commands += "sleep  1;";
        os.system("adb shell \"" + commands + "\"");

    else: # not all_good
        sys.exit();
