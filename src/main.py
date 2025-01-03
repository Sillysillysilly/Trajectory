import bpy
import numpy as np
import bmesh

# 获取模型对象
obj = bpy.context.object
print(obj)



# obj_filePath = "data/object/任务1-左前门模型.obj"
# imported_object = bpy.ops.import_scene.obj(filepath=obj_filePath)
obj_object = bpy.context.selected_objects[0]
print('Imported obj name: ', obj_object.name)


# 确保物体是网格对象
if obj.type != 'MESH':
    print("请选中一个网格对象！")
    exit()

# 切换到对象模式
bpy.ops.object.mode_set(mode='OBJECT')

# 获取物体的数据
mesh = obj.data

# 创建一个BMesh对象，用于操作网格
bm = bmesh.new()
bm.from_mesh(mesh)

print("bmesh成功")