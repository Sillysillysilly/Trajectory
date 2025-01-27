# Trajectory
该仓库旨在提供自动化流程的车辆表面喷涂轨迹生成算法
利用该仓库可以获得：
* 一组车辆表面的喷涂轨迹（json格式）
* 车辆表面轨迹生成的可视化（blender中）

## Prerequisite
* 基于python3.11开发
* 3D模型处理使用blender 4.1
* 测试仅在64位win11机器上进行

## Environment
源码使用以下python模块：
* bpy==4.3.0
* mathutils==3.3.0
* numpy==1.25.0

提供了requirement.txt便于快捷导入

## How to run
本仓库未提供导入obj模块功能，所以需要以python脚本的形式在blender中运行，具体运行步骤如下：
### 第零步（可选）：fork本项目
### 第一步：下载代码
方法1：将所需的分支，fork到你自己的账号下，然后clone你自己仓库。
方法2：使用以下命令手动clone指定分支：
```
git clone --single-branch --branch [分支名] git@github.com:Sillysillysilly/Trajectory.git
```
方法3：在本仓库手动下载指定分支的zip源码包后解压。

### 第二步：导入模型
* 首先打开blender（以4.1版本为例），点击菜单栏中的文件>>导入>>Wavefront(.obj)，选择需要导入的模型。或直接布局界面右键>>导入>>Wavefront(.obj)。
![step1](https://res.cloudinary.com/doc7dzcn4/image/upload/v1736054851/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20250105132702_mdmato.png)
* 导入模型后在布局界面可以看到已导入的模型
![step2](https://res.cloudinary.com/doc7dzcn4/image/upload/v1736054852/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20250105132711_tlcxfw.png)

### 第三步：运行脚本

* 菜单栏切换至脚本视图，选择文本>>打开>>选择./src/main.py
* 选中需要生成轨迹的模型，点击运行脚本即可
![step3](https://res.cloudinary.com/doc7dzcn4/image/upload/v1736056442/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20250105135341_whxvip.png)

## Additional Notes
### 效果预览
以特斯拉Model Y 前盖/左前翼子板/左前门 为例，生成效果如下（叠枪间距设置为80mm）：
![step4](https://res.cloudinary.com/doc7dzcn4/image/upload/v1736056660/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20250105135726_hrwfvm.png)

### 参数调整说明
* main.py中overlap_spacing参数用于调整叠枪距离（例如80or100）
* main.py中plane_normal参数用于调整切割平面，该参数直接决定了生成轨迹的方向（例如横竖）
* 仓库不提供根据文件夹导入obj功能，请手动导入并选择对象

## TODO
* 简单起见仅绘制了车辆表面的轨迹点，实际的喷涂轨迹有一部分可能需要延长，延长的思路写在思路说明中
* 轨迹尚未连接，因为连接线实际处于车辆表面外所以并未生成，需要连接的话首先将轨迹延长后，根据轨迹列表的编号，偶数项反转后连接即可
* 轨迹尚未平滑，而且在车门把手以及摄像头突起位置会出现异常凹凸，后期平滑即可，同时可以使用三次样条插值来使其均匀并二阶连续可导
* 后期如果需要更高精细化的话，可以根据喷枪喷漆扇面实际覆盖以及当前喷漆点法向量展开圆形覆盖范围设计相应的损失函数，借鉴SVM的思路逐步进行轨迹微调
