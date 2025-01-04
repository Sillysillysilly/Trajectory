import bpy
import numpy as np
import bmesh
import mathutils


# 计算平面与三角形的交点
def intersect_plane_triangle(plane_origin, plane_normal, v1, v2, v3):
    # 平面的点和法向量
    p0 = plane_origin
    n = plane_normal

    # 三角形的三个顶点
    triangle = [v1, v2, v3]

    # 使用mathutils库的函数进行平面与三角形的交点计算
    intersections = []
    for i in range(3):
        v1 = triangle[i]
        v2 = triangle[(i + 1) % 3]

        # 计算交点
        result = mathutils.geometry.intersect_line_plane(v1, v2, p0, n)
        if result and is_point_on_segment(result,v1,v2):
            intersections.append(result)
            #print(result)

    return intersections

#计算平面与多边形的交点
def intersect_plane_duo(plane_origin, plane_normal,verts_set):
    p0 = plane_origin
    n = plane_normal
    #verts_set.reverse()
    duo=len(verts_set)
    #print(duo)
    # 使用mathutils库的函数进行平面与三角形的交点计算
    intersections = []
    for i in range(duo):
        v1 = verts_set[i]
        v2 = verts_set[(i + 1) % duo]

        # 计算交点
        result = mathutils.geometry.intersect_line_plane(v1, v2, p0, n)
        if result and is_point_on_segment(result,v1,v2):
            intersections.append(result)
            #print(result)

    return intersections

def is_point_on_segment(P, A, B):
    # 计算向量AB和AP的叉积，判断是否共线
    AB = B - A
    AP = P - A
    cross_product = AB.cross(AP)

    # 如果叉积为零，说明共线
    if cross_product.length < 1e-6:  # 防止浮动误差
        return False

    # 检查点P是否在A和B之间
    if min(A.x, B.x) <= P.x <= max(A.x, B.x) and \
       min(A.y, B.y) <= P.y <= max(A.y, B.y) and \
       min(A.z, B.z) <= P.z <= max(A.z, B.z):
        return True
    return False

def nearest_neighbor_sort(points):
    remaining_points = list(range(len(points)))  # 记录所有点的索引
    sorted_points = [remaining_points.pop(0)]  # 从第一个点开始
    while remaining_points:
        last_point = sorted_points[-1]
        next_point = min(remaining_points, key=lambda point: distance(points[last_point], points[point]))
        sorted_points.append(next_point)
        remaining_points.remove(next_point)
    return [points[i] for i in sorted_points]



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
        # 由于网格不一定为三角形，所以更新函数，计算平面与多边形的交点
        intersection = intersect_plane_duo(plane_origin, plane_normal, v1, v2, v3)
        if intersection:
            intersection_points.append(intersection)

# 如果有交点，创建一条曲线
if intersection_points:
    # 创建一个新的曲线对象
    curve_data = bpy.data.curves.new('IntersectionCurve', type='CURVE')
    curve_data.dimensions = '3D'
    
    #排序点
    intersection_points=nearest_neighbor_sort(intersection_points)

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
