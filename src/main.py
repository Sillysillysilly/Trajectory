import bpy
import numpy as np
import bmesh
import mathutils


# 计算平面与三角形交点
def intersect_plane_triangle(plane_origin, plane_normal, v1, v2, v3):
    # 使用射线与三角形的交点计算
    # 平面方程: (P - plane_origin) · plane_normal = 0
    # 通过求解平面与三角形相交的线段，获取交点
    intersection = mathutils.geometry.intersect_line_tri(plane_origin, plane_origin + plane_normal, v1, v2, v3)
    return intersection

# 获取当前选中的物体
obj = bpy.context.object

# 确保物体是网格对象
if obj.type != 'MESH':
    print("请选中一个网格对象！")
    exit()

# 获取物体的数据
mesh = obj.data

# 创建一个BMesh对象，用于操作网格
bm = bmesh.new()
bm.from_mesh(mesh)

# 获取物体中的所有面
faces = [f for f in bm.faces]

# 定义平面（通过一个点和法向量定义）
plane_origin = mathutils.Vector((0, 0, 400))  # 平面上的一个点
plane_normal = mathutils.Vector((0, 0, 1))  # 平面的法向量

# 存储交点
intersection_points = []

# 遍历网格的所有面（假设每个面是三角形）
for face in faces:
    if len(face.verts) == 3:  # 确保面是三角形
        v1, v2, v3 = [v.co for v in face.verts]
        # 计算平面与三角形的交点
        intersection = intersect_plane_triangle(plane_origin, plane_normal, v1, v2, v3)
        if intersection:
            intersection_points.append(intersection)

# 如果有交点，创建一条曲线
if intersection_points:
    # 创建一个新的曲线对象
    curve_data = bpy.data.curves.new('IntersectionCurve', type='CURVE')
    curve_data.dimensions = '3D'
    
    # 使用多段曲线生成交线
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(count=len(intersection_points) - 1)
    
    for i, point in enumerate(intersection_points):
        polyline.points[i].co = (point.x, point.y, point.z, 1)  # 添加x, y, z坐标

    # 创建一个对象来容纳这些曲线
    curve_obj = bpy.data.objects.new("IntersectionCurve", curve_data)

    # 将该对象添加到场景中
    bpy.context.collection.objects.link(curve_obj)

    # 选中并激活新创建的对象
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)

    # 输出完成信息
    print("交线已生成！")
else:
    print("没有计算到交线！")
