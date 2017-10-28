#!/usr/bin/env python
# -*- coding: utf-8 -*-

import roslib
roslib.load_manifest('dish_report')
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge, CvBridgeError

class dish_reporter:
    def __init__(self):
        # self.image_pub = rospy.Publisher("dish_report",String)
        self.bridge = CvBridge()
        # [note]デバッグ用に普通のカメラを使う場合に使用する
        # self.image_sub = rospy.Subscriber( "/cv_camera/image_raw", Image, self.callback )
        # [note]圧縮画像トピックを購読する
        self.image_sub = rospy.Subscriber( "/compressed_picam/compressed", CompressedImage, self.callback )
        # イメージサイズの定義
        self.image_width = 640
        self.image_height = 480
        # 円形検出しやすくするためのガウシアンフィルタ係数
        self.image_gsigma = 33
        # 検出した円形領域の拡縮用変数 
        self.check_cutback = 0
        # 白とみなす明るさのしきい値(照明やお皿の色、カメラ性能によって調整が必要)
        self.white_threshold = 100

    def avgColor(self, pa, pb, pc, pd ):
        # 画素a,b,c,dを平均した中央色を求める(あえて書いてみた)
        b = int( round( ((int(pa[0])+int(pb[0])) /2.0)+((int(pc[0])+int(pd[0])) /2.0) /2.0 ) )
        g = int( round( ((int(pa[1])+int(pb[1])) /2.0)+((int(pc[1])+int(pd[1])) /2.0) /2.0 ) )
        r = int( round( ((int(pa[2])+int(pb[2])) /2.0)+((int(pc[2])+int(pd[2])) /2.0) /2.0 ) )
        return ([b, g, r])

    def callback(self,data):
        # Subscribeしている画像トピックが更新されると呼び出される
        try:
            # Convert image [ROS -> OpenCV]
            # [note]デバッグ用に普通のカメラを使う場合に使用する
            # cv_image = self.bridge.imgmsg_to_cv2( data, "bgr8" )
            # [note]受信した圧縮画像をbgr8形式に展開する
            cv_image = self.bridge.compressed_imgmsg_to_cv2( data, "bgr8" )
        except CvBridgeError as e:
            print(e)

        # 受信した画像から円形（お皿）の座標を検出する
        color_img = cv2.resize( cv_image, (self.image_width, self.image_height) )
        mono_img  = cv2.cvtColor( color_img, cv2.COLOR_RGB2GRAY )
        mono_img  = cv2.GaussianBlur(mono_img, (self.image_gsigma, self.image_gsigma), 0)
        circles = cv2.HoughCircles(mono_img, cv2.HOUGH_GRADIENT,
                                    dp=1,         minDist=10, 
                                    param1=10,    param2=85,
                                    minRadius=50, maxRadius=300)
        # 画面表示用の画像を代入
        res_img = color_img.copy()
        dish_count = 0
        # 画像に一つ以上の円形領域が検出された場合
        if circles is not None and len(circles) > 0:
            # 円形を検出した座標の色を全て確認する
            for i in circles[0,:]:
                # 色チェック用に円形の領域を切り出す
                radius = int(i[2] - self.check_cutback)
                if radius < 5:
                    radius = 5
                top    = int(i[1] - radius)
                if top < 0:
                    top = 0
                left   = int(i[0] - radius)
                if left < 0:
                    left = 0
                circle_img = color_img[ left : left+(radius*2), top : top+(radius*2) ]
                check_img = circle_img.copy()
                # 6x6の画像に圧縮してチェックの処理効率を上げる
                try:
                    check_img = cv2.resize( check_img, (6,6), interpolation = cv2.INTER_AREA )
                except e:
                    print(e)
                # 円形領域の中心の平均色を作成する
                pa = check_img[2,2]
                pb = check_img[3,2]
                pc = check_img[2,3]
                pd = check_img[3,3]
                dish_color = self.avgColor( pa, pb, pc, pd )
                # 中心のRGBレベルがほぼ同じで十分明るいか（つまり白色であるか）を確認
                if (max(dish_color) - min(dish_color)) < 5 and min(dish_color) > self.white_threshold:
                    # 空っぽのお皿（白色の円形）を検出したので検出場所に印をつける
                    cv2.circle( res_img,(i[0],i[1]),i[2],(0,0,255),3)
                    dish_count = dish_count+1
                    # デバッグ用
                    # cv2.imshow( "debug window", check_img )
        if dish_count > 0:
            # お皿が検出できた場合
            cv2.imshow( "Dish reporter", res_img )
        else:
            # お皿が検出できなかった場合
            cv2.imshow( "Dish reporter", color_img )
        cv2.waitKey(3)

# メイン処理
def main(args):
    ic = dish_reporter()
    rospy.init_node('dish_report', anonymous=True)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Bye Bye!!")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)

