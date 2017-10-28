ROSで始めるホビーロボット#06 サンプルコード   
「画像からお皿に何か載っているか判定する」   
====

## Description
「ROSではじめるホビーロボット#06」で紹介した画像認識のサンプルコードです。   
ROSのトピックから受け取った画像を使って中心が白色の円形を見つけます。   

## Requirement
特にコンパイルは必要ありません。   
何らかのカメラノードを立ち上げて、画像を受け取れる状態にして下さい。   
画像の判定結果をウインドウ表示するため、CUIではなくデスクトップ環境で実行して下さい。   
dish_report.pyに実行権限がついていない場合は下記のように実行権限を付与して下さい。   

(catkin_workspace)/src/dish_report/scripts $ chmod +x dish_report.py   

## Usage
下記のように実行して下さい。   
$ rosrun dish_report dish_report.py   
