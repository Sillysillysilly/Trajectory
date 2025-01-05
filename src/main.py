import bpy
import numpy as np
import bmesh
import math
import mathutils
import json
import os


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

# 计算两点之间的欧几里得距离
def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

# 排序点：选择一个起点，找到离起点最近的点，继续重复直到所有点排序完毕
def sort_points_by_distance(points):
    sorted_points = [points[0]]  # 选择第一个点作为起始点
    remaining_points = points[1:]  # 其余的点

    while remaining_points:
        last_point = sorted_points[-1]  # 当前已排序的最后一个点
        # 计算当前点到每个剩余点的距离
        distances = [distance(last_point, point) for point in remaining_points]
        # 找到距离最近的点
        closest_point = remaining_points[np.argmin(distances)]
        if(distance(points[0],closest_point)<distance(closest_point,last_point)):
            sorted_points.reverse()
        if(closest_point == last_point):
            remaining_points.remove(closest_point)  # 从剩余点中移除
            continue
        if(distance(closest_point,last_point)>500):
            remaining_points.remove(closest_point)  # 从剩余点中移除
            continue

        sorted_points.append(closest_point)  # 加入已排序点列表
        remaining_points.remove(closest_point)  # 从剩余点中移除

    return sorted_points

#生成平面和曲面的交线
def intersection_plane_surface(plane_origin, plane_normal, obj):
    # 确保物体是网格对象
    if obj.type != 'MESH':
        print("请选中一个网格对象！")
        return None

    # 获取物体的数据
    mesh = obj.data

    # 创建一个BMesh对象，用于操作网格
    bm = bmesh.new()
    bm.from_mesh(mesh)


    # 获取物体中的所有面
    faces = [f for f in bm.faces]

    # 定义平面（可以通过一个点和法向量定义）
    # plane_origin = mathutils.Vector((0, 0, 1010))  # 平面上的一个点
    # plane_normal = mathutils.Vector((0, 0, 1))  # 平面的法向量（假设平面是XY平面）

    # 计算交点
    intersection_points = []

    # 遍历网格的所有面（假设每个面是三角形）
    for face in faces:
        count_verts=len(face.verts)

        verts_set=[v.co for v in face.verts]
        verts_set.reverse()
        points = intersect_plane_duo(plane_origin, plane_normal, verts_set)
        if points:
            intersection_points.extend(points)
        # if len(face.verts) == 3:  # 确保面是三角形
        #     v1, v2, v3 = [v.co for v in face.verts]
        #     # 计算平面和三角形的交点
        #     points = intersect_plane_triangle(plane_origin, plane_normal, v1, v2, v3)
        #     if points:
        #         intersection_points.extend(points)

    return intersection_points

#根据交点表生成相应曲线
def generate_curve(curve_data, intersection_points):
#     # 如果有交点，创建一条曲线
#   if intersection_points:
    # 创建一个新的曲线对象
    # curve_data = bpy.data.curves.new('IntersectionCurve', type='CURVE')
    # curve_data.dimensions = '3D'
    
    #排序点
    intersection_points=sort_points_by_distance(intersection_points)
    #intersection_points=nearest_neighbor_sort(intersection_points)
    # 使用多段曲线生成交线
    polyline = curve_data.splines.new('POLY')
    polyline.points.add(count=len(intersection_points) - 1)
    
    for i, point in enumerate(intersection_points):
        polyline.points[i].co = (point.x, point.y, point.z, 1)  # 添加x, y, z坐标

    # return curve_data

#计算物体在某方向上的跨度
def Calculate_span(obj, plane_normal):
    # 将方向向量归一化（确保只是方向）
    direction_vector = np.array(plane_normal)
    direction_unit_vector = direction_vector / np.linalg.norm(direction_vector)

    # 计算每个点在该方向上的投影值
    projections = []
    
    # 确保物体是网格对象
    if obj.type != 'MESH':
        print("请选中一个网格对象！")
        return None

    # 获取物体的数据
    mesh = obj.data

    # 创建一个BMesh对象，用于操作网格
    bm = bmesh.new()
    bm.from_mesh(mesh)


    # 获取物体中的所有面
    faces = [f for f in bm.faces]
    verts_set=[]
    # 遍历网格的所有面（假设每个面是三角形）
    for face in faces:
        for v in face.verts:
            verts_set.append(v)
            point=np.array([v.co.x,v.co.y,v.co.z])
            projection = np.dot(point, direction_unit_vector)
            projections.append(projection)
    
    # 找到最负和最正的投影值以及对应的点
    min_projection_index = np.argmin(projections)  # 最负的点索引
    max_projection_index = np.argmax(projections)  # 最正的点索引

    span={}

    # 获取最负点和最正点的投影值（即在该方向上的距离）
    min_distance = projections[min_projection_index]
    max_distance = projections[max_projection_index]

    span["min_vert"] = np.array([verts_set[min_projection_index].co.x,verts_set[min_projection_index].co.y,verts_set[min_projection_index].co.z])  # 最负的点
    span["max_vert"] = np.array([verts_set[max_projection_index].co.x,verts_set[max_projection_index].co.y,verts_set[max_projection_index].co.z])  # 最正的点
    span["distance"] = max_distance-min_distance

    return span

def move_point_along_direction(point, direction_vector, distance):
    """
    计算一个点沿某个方向前进一定距离后的新位置。

    参数:
    - point: numpy 向量，表示原始点 (x, y, z)。
    - direction_vector: numpy 向量，表示方向向量 (dx, dy, dz)。
    - distance: 前进的距离 (float)。

    返回:
    - 新的位置 (numpy 向量)。
    """
    # 归一化方向向量
    unit_vector = direction_vector / np.linalg.norm(direction_vector)
    
    # 计算新的位置
    new_position = point + distance * unit_vector
    
    return new_position


        
#常规计算切割平面
#plane_normal即可确定沿着哪个坐标轴进行移动切割
def calculate_cutting_plane(obj, plane_normal, overlap_spacing):
    obj_span=Calculate_span(obj, plane_normal)
    cutting_num=math.floor(obj_span["distance"]/overlap_spacing)
    plane_set=[]
    point=obj_span["min_vert"]
    for i in range(cutting_num):
        plane={}
        plane["plane_normal"]=plane_normal
        plane["plane_origin"]=move_point_along_direction(point, plane_normal, overlap_spacing) 
        point=plane["plane_origin"]
        plane_set.append(plane)
        
        #print(point)

    return plane_set



#以下相当于main函数，脚本中我直接写过程了就
bpy.ops.object.mode_set(mode='OBJECT')
# 获取当前选中的物体
obj = bpy.context.object

#设置叠枪距离
overlap_spacing=100

#定义平面（可以通过一个点和法向量定义）
#todo：后续改成数组，存储一组平面
# plane_origin = mathutils.Vector((0, 0, 1010))  # 平面上的一个点
plane_normal = mathutils.Vector((1, 0, 0))  # 平面的法向量

plane_set=calculate_cutting_plane(obj, plane_normal, overlap_spacing)

traj_json_file={}
traj_json_file["traj_surface"]=[]

for plane in plane_set:
    print(plane["plane_origin"])
    # intersection_points = intersection_plane_surface(plane_origin, plane_normal, obj)
    intersection_points = intersection_plane_surface(plane["plane_origin"], plane["plane_normal"], obj)


    vertex_coords = [[v.x, v.y, v.z] for v in intersection_points]

    for point in vertex_coords:
        traj_surface_item={}
        traj_surface_item["p"]=point
        traj_surface_item["n"]=[
                -0.8454278109113345,
                0.041408269879582904,
                -0.5324820858237848
        ]
        traj_surface_item["speed"]=300
        traj_surface_item["index"]=0
        traj_surface_item["spray"]=False
        traj_surface_item["posture"]=[
                864.9001628166507,
                -1529.874297441074,
                1246.408448081015,
                -175.55336420121748,
                -57.717801285442256,
                95.25542482395923
        ]
        traj_surface_item["transition"]=False
        traj_surface_item["gun_posture"]="default"

        traj_json_file["traj_surface"].append(traj_surface_item)


    curve_data = bpy.data.curves.new('IntersectionCurve', type='CURVE')
    curve_data.dimensions = '3D'

    generate_curve(curve_data, intersection_points)
    # 创建一个对象来容纳这些曲线
    curve_obj = bpy.data.objects.new("IntersectionCurve", curve_data)

    # 将该对象添加到场景中
    bpy.context.collection.objects.link(curve_obj)

    # 选中并激活新创建的对象
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)

# 获取当前脚本所在目录
script_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.path.dirname(__file__)
# 定义目标文件夹和文件名
output_folder = os.path.join(script_dir, "saved_json")
os.makedirs(output_folder, exist_ok=True)  # 确保文件夹存在，如果不存在则创建
# 定义文件路径

filepath = os.path.join(output_folder, obj.name+"_"+str(overlap_spacing)+".json")
 # 将数据保存为JSON文件
with open(filepath, 'w') as json_file:
    json.dump(traj_json_file, json_file, indent=4)

#print(filepath)

