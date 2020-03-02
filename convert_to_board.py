import bpy
import bmesh
from .common_calc import CommonCalc
calc = CommonCalc()

class BoxConvertToBoard(bpy.types.Operator):
    bl_idname = "object.box_convert" # ID
    bl_label = "Box convet to board" # メニューに追加されるラベル
    bl_description = "Box convet to board" # 関数の説明
    bl_options = {'REGISTER', 'UNDO'}  # 処理の属性

    def execute(self, context):
        if len(bpy.context.selected_objects) == 0:
            self.report({'ERROR'}, "object is not selected!")
            return {'FINISHED'}

        editObj = bpy.context.selected_objects[0]
        editObj.rotation_euler[0] = 0
        editObj.rotation_euler[1] = 0
        editObj.rotation_euler[2] = 0   #回転している状態をなくす
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.mesh.select_all(action='DESELECT')
        bm = bmesh.from_edit_mesh(editObj.data)
        for face in bm.faces:
            faceNormal = face.normal
            if calc.checkNormalBox(faceNormal):
                # 面を元のオブジェクトから分離して別オブジェクトに
                face.select_set(True)
                bpy.ops.mesh.separate(type='SELECTED')
            else:
                self.report({'ERROR'}, "invalid object!")
                return {'FINISHED'}

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        boxFaces = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')

        for boxFace in boxFaces:
            boxFace.select_set(True)
            
            for face in boxFace.data.polygons:
                faceNormal = face.normal
                # 厚さ分内側に面を移動
                bpy.ops.transform.translate(value=(faceNormal * -bpy.types.Scene.thickness/ 10), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_mode(type="FACE")
                bpy.ops.mesh.select_all(action='SELECT')
                # 厚さ分外側に面を押し出し
                bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(faceNormal * (bpy.types.Scene.thickness / 10))})
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            boxFace.select_set(False)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # 面全てを分離したので元のオブジェクトを削除
        bpy.data.objects[editObj.name].select_set(True)
        bpy.ops.object.delete(use_global=False)

        self.report({'INFO'}, "Box conveting finished")
        return {'FINISHED'}
