import bpy
import bmesh
from .common_calc import CommonCalc
calc = CommonCalc()

class CrossCutA(bpy.types.Operator):
    bl_idname = "object.cross_cut_a" # ID
    bl_label = "CrossCut" # メニューに追加されるラベル
    bl_description = "cross cut" # 関数の説明
    bl_options = {'REGISTER', 'UNDO'}  # 処理の属性

    def execute(self, context):
        crosscut(self, 'A')
        return {'FINISHED'}

class CrossCutB(bpy.types.Operator):
    bl_idname = "object.cross_cut_b" # ID
    bl_label = "CrossCut" # メニューに追加されるラベル
    bl_description = "cross cut" # 関数の説明
    bl_options = {'REGISTER', 'UNDO'}  # 処理の属性

    def execute(self, context):
        crosscut(self, 'B')
        return {'FINISHED'}

def crosscut(self, cutType):
    if len(bpy.context.selected_objects) == 0:
        self.report({'ERROR'}, "object is not selected!")
        return {'FINISHED'}

    editObj = bpy.context.selected_objects[0]

    if editObj.type != "MESH":
        self.report({'ERROR'}, "selected object is not mesh!")
        return {'FINISHED'}

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    # for pl in editObj.data.polygons:
    #     print(pl.index)
    mw = editObj.matrix_world
    bm = bmesh.from_edit_mesh(editObj.data)
    faceNormal = None
    for face in bm.faces:
        if face.select == True:
            targetEdge = []
            thicknessCount = 0
            for edge in face.edges:
                edgeLength = (mw @ (edge.verts[1].co) - mw @ (edge.verts[0].co)).length
                if calc.lcLength(edgeLength) == bpy.types.Scene.thickness:
                    thicknessCount += 1
                else:
                    targetEdge.append(edge)

            if thicknessCount == 2:
                bpy.ops.mesh.select_mode(type="EDGE")
                bpy.ops.mesh.select_all(action='DESELECT')
                targetEdge[0].select_set(True)
                targetEdge[1].select_set(True)
            else:
                self.report({'ERROR'}, "object is not match thinkness!!")
                return False
            # 後で面を引き出す分、先に引っ込めておく
            faceNormal = face.normal
            bpy.ops.transform.translate(value=(faceNormal * -bpy.types.Scene.thickness/ 10), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
            break

    bpy.ops.mesh.subdivide(number_cuts=(bpy.types.Scene.dividenum - 1))

    # 引き出す面を選択
    # bpy.ops.mesh.subdivideのクセを利用している仕様なので
    # bpy.ops.mesh.subdivideの仕様変更があると機能しなくなる可能性あり
    transrateFaces = []
    transrateFaceCount = 0
    for face in bm.faces:
        if face.select == True:
            if cutType == 'B':
                if transrateFaceCount == 0 or transrateFaceCount % 2 == 1:
                    transrateFaces.append(face)
            else:
                if transrateFaceCount != 0 and transrateFaceCount % 2 == 0:
                    transrateFaces.append(face)
            transrateFaceCount += 1

    bpy.ops.mesh.select_all(action='DESELECT')
    for face in transrateFaces:
        face.select_set(True)

    print(faceNormal)
    # 面をBoardの厚さ分引き出す
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(faceNormal * (bpy.types.Scene.thickness / 10))})
    bpy.ops.mesh.select_mode(type="FACE")

    self.report({'INFO'}, "Cross Cuts finished")

    return True