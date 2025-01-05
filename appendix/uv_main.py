import bpy
import math
import mathutils
from mathutils import Vector

# 获取当前选中的对象（确保它是一个网格对象）
obj = bpy.context.object

if obj is None or obj.type != 'MESH':
    print("请先选择一个有效的网格对象！")
else:
    # 确保模型有UV图层
    if len(obj.data.uv_layers) == 0:
        print("模型没有UV图层，正在进行UV展开...")
        bpy.ops.object.mode_set(mode='EDIT')  # 进入编辑模式
        bpy.ops.mesh.select_all(action='SELECT')  # 选择所有面
        bpy.ops.uv.unwrap(method='ANGLE_BASED')  # 使用角度基展开法进行UV展开
        bpy.ops.object.mode_set(mode='OBJECT')  # 退出编辑模式

    # 获取当前活动的UV图层
    uv_layer = obj.data.uv_layers.active
    if uv_layer is None:
        print("没有活动的UV图层，无法继续！")
    else:
        uv_data = uv_layer.data
        print(uv_data)
        # 获取模型的顶点信息
        mesh = obj.data
        vertices = [v.co for v in obj.data.vertices]
        print(vertices)

        # 获取面和UV对应的顶点
        def get_3d_point_from_uv(uv):
            # 找到最接近的面，并获取对应的顶点
            for poly in mesh.polygons:
                uv_coords = [uv_data[loop_index].uv for loop_index in poly.loop_indices]
                if uv in uv_coords:
                    loop_index = uv_coords.index(uv)
                    loop = mesh.loops[poly.loop_indices[loop_index]]
                    vertex_index = loop.vertex_index
                    return vertices[vertex_index]
            return None

        # 生成喷涂轨迹（UV平面上的轨迹）
        def generate_uv_spray_trajectory(uv_data, spray_radius=0.08, step_distance=0.1):
            spray_trajectory = []
            uv_min = [float('inf'), float('inf')]
            uv_max = [-float('inf'), -float('inf')]

            # 获取UV的最小和最大值，确定UV空间的范围
            for uv in uv_data:
                uv_min = [min(uv_min[0], uv.uv[0]), min(uv_min[1], uv.uv[1])]
                uv_max = [max(uv_max[0], uv.uv[0]), max(uv_max[1], uv.uv[1])]
            print(uv_max,uv_min)

            uv_width = uv_max[0] - uv_min[0]
            uv_height = uv_max[1] - uv_min[1]

            # 在UV范围内生成一条喷涂轨迹
            num_sprays = int(uv_height / step_distance)
            for i in range(num_sprays):
                v = uv_min[1] + i * step_distance  # 沿着V轴平滑移动
                u_start = uv_min[0]
                u_end = uv_max[0]

                # 在UV范围内生成一条平行扫描路径
                spray_trajectory.append((u_start, v))
                spray_trajectory.append((u_end, v))

            
            return spray_trajectory

        # 生成UV平面上的喷涂轨迹
        spray_trajectory_uv = generate_uv_spray_trajectory(uv_data)
        print(spray_trajectory_uv)

        # 将UV轨迹映射回3D坐标
        def map_uv_to_3d(spray_trajectory_uv):
            spray_trajectory_3d = []
            for uv in spray_trajectory_uv:
                uv_point = Vector((uv[0], uv[1]))  # 创建UV坐标点
                point_3d = get_3d_point_from_uv(uv_point)  # 映射到3D
                if point_3d:
                    spray_trajectory_3d.append(point_3d)
            return spray_trajectory_3d

        # 生成喷涂轨迹
        spray_trajectory_3d = map_uv_to_3d(spray_trajectory_uv)
        print(spray_trajectory_3d)

        # 创建曲线对象
        def create_spray_trajectory_curve(spray_trajectory_3d):
            # 创建一个新的曲线对象
            curve_data = bpy.data.curves.new(name="SprayPath", type='CURVE')
            curve_data.dimensions = '3D'

            # 创建样条
            spline = curve_data.splines.new('POLY')
            spline.points.add(count=len(spray_trajectory_3d) - 1)

            # 设置每个轨迹点
            for i, point in enumerate(spray_trajectory_3d):
                spline.points[i].co = (point.x, point.y, point.z, 1)

            # 创建曲线对象
            curve_obj = bpy.data.objects.new("SprayPathObj", curve_data)
            bpy.context.collection.objects.link(curve_obj)

            return curve_obj

        # 创建并显示轨迹曲线
        create_spray_trajectory_curve(spray_trajectory_3d)
