import bpy

class CleanMesh(bpy.types.Operator):
    bl_idname = "object.clean_mesh" # ID
    bl_label = "CleanMesh" # メニューに追加されるラベル
    bl_description = "delete remain mash of deleted object" # 関数の説明
    bl_options = {'REGISTER', 'UNDO'}  # 処理の属性

    def execute(self, context):
        # オブジェクト名にメッシュ名をあわせる
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                obj.data.name = obj.name

        # オブジェクトの無いメッシュを削除
        for mesh in bpy.data.meshes:
            delFlag = True
            for obj in bpy.data.objects:
                if mesh.name == obj.name:
                    delFlag = False
                    break
            if delFlag:
                bpy.data.meshes.remove(mesh)
            
        self.report({'INFO'}, "clean mesh finished!")
        return {'FINISHED'}