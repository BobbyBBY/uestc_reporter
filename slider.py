import cv2
import base64
import numpy as np
import random
from datetime import datetime


def findSliderX(bigImg_base64, smallImg_base64):
    # print(len(smallImg_base64))
    # print(len(bigImg_base64))
    smallImg_base64 = smallImg_base64[22:]
    bigImg_base64 = bigImg_base64[22:]

    try:
        bigImg_bytes = base64.urlsafe_b64decode(
            bigImg_base64 + "=" * (4 - len(bigImg_base64) % 4)
        )
        smallImg_bytes = base64.urlsafe_b64decode(
            smallImg_base64 + "=" * (4 - len(smallImg_base64) % 4)
        )
        bigImg_array = np.fromstring(bigImg_bytes, np.uint8)
        smallImg_array = np.fromstring(smallImg_bytes, np.uint8)
        bigImg = cv2.imdecode(bigImg_array, cv2.IMREAD_COLOR)
        smallImg = cv2.imdecode(smallImg_array, cv2.IMREAD_COLOR)
        # cv2.imshow('bigImg', bigImg)
        # cv2.imshow('smallImg', smallImg)
    except Exception:
        pass

    # 分析小图片，找到纵坐标
    # img = cv2.imread('slider2-1.png', 0)
    img = smallImg
    blur = cv2.GaussianBlur(img, (3, 3), 0)  # 用高斯滤波处理原图像降噪
    canny = cv2.Canny(blur, 150, 200)  # canny算子边缘检测 170是最小阈值,200是最大阈值
    # print(len(canny))
    # print(len(canny[0]))
    # cv2.imshow('smallImg_canny', canny)
    YFromTop = 0
    for i in range(len(canny)):
        if (canny[i][5]) > 0:
            YFromTop = i
            break
    # print(YFromTop)

    # 分析大图片，找到横坐标
    # img = cv2.imread('slider2-2.png', 0)
    img = bigImg
    blur = cv2.GaussianBlur(img, (3, 3), 0)
    canny = cv2.Canny(blur, 150, 200)
    # print(len(canny))
    # print(len(canny[0]))
    # cv2.imshow('bigImg_canny', canny)
    XFromLeft = 0
    # 根据前面得到的纵坐标开始分析,向下浮动5个像素点
    XFromLeft = findLineEdge(canny, YFromTop, 0)
    if XFromLeft > 0:
        # 暂不启用
        pass
        # 向右约75个像素是缺口的右边沿
        # 向右70个像素，浮动10个像素点
        # for x_i in range(10):
        #     result = findLineEdge(canny, YFromTop, XFromLeft+70+x_i)
        #     if result > 0:
        #         break
        # else:
        #     print("未检测到边沿2 " +str(datetime.now()))
    else:
        print("未检测到边沿1 " + str(datetime.now()))
        XFromLeft = random.randint(20, len(canny[0]) - 20)

    # 已废弃
    # for y_i in range(5):
    #     for i in range(len(canny[0])):
    #         if(canny[YFromTop+y_i][i]) > 0:
    #             # 向下延伸10个像素，如果都是边缘则认为是缺口的左边沿
    #             for j in range(10):
    #                 if(canny[YFromTop+j+y_i][i] == 0):
    #                     break
    #             else:
    #                 # 向右约73个像素是缺口的右边沿
    #                 # 向右71个像素，向右浮动5个像素点
    #                 for x_i in range(5):
    #                     # 向下延伸10个像素，如果都是边缘则认为是缺口的右边沿
    #                     for j in range(10):
    #                         if(canny[YFromTop+j+y_i][i+x_i] == 0):
    #                             # 不是边沿
    #                             break
    #                     else:
    #                         # 是边沿
    #                         XFromLeft = i
    #                         break
    #                 else:
    #                     # 不是边沿
    #                     continue
    #                 # 是边沿
    #                 break
    #     else:
    #         # 不是边沿
    #         continue
    #     # 是边沿
    #     break
    # print(XFromLeft)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    XFromLeft_scale = XFromLeft / len(canny[0])
    return XFromLeft_scale


# 检测滑块纵向边沿
def findLineEdge(Img, y_base, x_base):
    XFromLeft = -1
    # 向下浮动5个像素点
    for y_i in range(5):
        # 横向，从左至右分析
        for i in range(x_base, len(Img[0])):
            if (Img[y_base + y_i][i]) > 0:
                # 向下延伸10个像素，如果都是边缘则认为是缺口的左边沿
                for j in range(10):
                    if Img[y_base + j + y_i][i] == 0:
                        # 不是边沿
                        break
                else:
                    # 是边沿
                    XFromLeft = i
                    break
        else:
            # 不是边沿
            continue
        # 是边沿
        break
    return XFromLeft

