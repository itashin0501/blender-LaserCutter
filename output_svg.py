
import bpy
import bmesh
import math
import svgwrite
from .common_calc import CommonCalc
calc = CommonCalc()

half_pi = 0.5 * math.pi

sumWidth = 0
sumHeight = 0
curY = 0
tMargin = 0.2

class LC_OT_SVG(bpy.types.Operator):
    bl_idname = "object.output_svg" # ID
    bl_label = "LaserCutterAddon" # メニューに追加されるラベル
    bl_description = "transform all object for Laser-Cutter svg exporting" # 関数の説明
    bl_options = {'REGISTER', 'UNDO'}  # 処理の属性

    # アドオンの処理
    def execute(self, context):
        saveSvgFilePath = bpy.types.Scene.savedirectory
        if saveSvgFilePath == '':
            self.report({'ERROR'}, "Not select save directory!")
            return {'FINISHED'}

        # TODO scene追加して元のオブジェクトを残す処理にしたい
        bpy.ops.scene.new(type='FULL_COPY')
        # bpy.context.scene.name = "LaserCut"

        thickness = context.scene.thicknessBoardF
        global sumWidth
        global maxHeight
        global curX
        sumWidth = 0
        maxHeight = 0
        curX = 0
        canvasPadding = 5 # (mm)
        svgRate = 37.766 #柏の葉レーザーカッター用の係数

        # bpy.ops.object.select_all(action='DESELECT')

        targetObjects = bpy.context.selected_objects
        for obj in targetObjects:
            print(obj.name)

        #オブジェクトを平面に収まるように回転させる
        for obj in targetObjects:
            if obj.type != "MESH":
                continue
            
            obj.select_set(True)
            bpy.ops.object.origin_set(bpy.context.copy(), type='ORIGIN_GEOMETRY') #原点を図形の重心に移動する
            obj.rotation_euler[0] = 0
            obj.rotation_euler[1] = 0
            obj.rotation_euler[2] = 0   #回転している状態をなくす

            #平面にオブジェクトを並べる
            if calc.lcLength(obj.dimensions[2]) != thickness:
                if calc.lcLength(obj.dimensions[0]) == thickness:
                    obj.rotation_euler[1] = half_pi
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                elif calc.lcLength(obj.dimensions[1]) == thickness:
                    obj.rotation_euler[0] = half_pi
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                else:
                    obj.hide_viewport = True
                    continue

            #横長のオブジェクトは回転して縦長に配置
            # bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            # if obj.dimensions[0] >= obj.dimensions[1]:
            #     obj.rotation_euler[2] = half_pi
            #     bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            sumWidth += calc.lcLength(obj.dimensions[0])
            maxHeight = max([maxHeight, calc.lcLength(obj.dimensions[1])])

            obj.select_set(False)

        # x軸方向で図形を重ならないように並べる
        for obj in targetObjects:
            if obj.type != "MESH" or obj.hide_viewport:
                continue

            obj.select_set(True)

            # 図形の重心を再設定して原点に移動
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
            obj.location[0] = 0
            obj.location[1] = 0
            obj.location[2] = 0

            # bm = bmesh.new()
            # bm.from_mesh(obj.data)
            # minX = 0
            # for v in bm.verts:
            #     if minX > v.co.x:
            #         minX = v.co.x
            # bpy.context.scene.cursor.location[0] = 0
            # bpy.context.scene.cursor.location[1] = 0
            # bpy.context.scene.cursor.location[2] = 0
            # bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            trx = calc.lcLength(obj.dimensions[0]) / 20
            curX += trx
            # obj.location[0] = curX
            obj.location[0] = calc.lcLength(obj.dimensions[0]) / 20 + (canvasPadding / svgRate * 2)
            obj.location[1] = calc.lcLength(obj.dimensions[1]) / 20 + (canvasPadding / svgRate * 2)
            obj.location[2] = 0
            curX += trx + tMargin

            obj.select_set(False)

        # bpy.context.scene.cursor_location = (0, 0, 0)
        bpy.context.scene.cursor.location[0] = 0
        bpy.context.scene.cursor.location[1] = 0
        bpy.context.scene.cursor.location[2] = 0

        # レーザーカッター用に２次元データに加工
        for obj in targetObjects:
            if obj.type != "MESH" or obj.hide_viewport:
                continue

            bm = bmesh.new()
            bm.from_mesh(obj.data)
            verts = []
            for vt in bm.verts:
                if vt.normal.z < 0:
                    verts.append(vt)

            bmesh.ops.delete(bm, geom=verts, context='VERTS')
            bm.to_mesh(obj.data)

            # ２つの面に接したEdgeを選択、削除する
            edgeCount = 0
            plEdges = []
            targetEdgeVerticesIndex = []
            for pl in obj.data.polygons:
                for edge in pl.edge_keys:
                    plEdges.append(edge)

            for ple1 in plEdges:
                for ple2 in plEdges:
                    if ple1 == ple2:
                        edgeCount += 1
                        if edgeCount == 2:
                            targetEdgeVerticesIndex.append(ple1)
                edgeCount = 0

            delEdges = []
            preEdgeIndex = 0
            for ed in bm.edges:
                for t in targetEdgeVerticesIndex:
                    if (t[0] == ed.verts[0].index and t[1] == ed.verts[1].index) or (t[0] == ed.verts[1].index and t[1] == ed.verts[0].index):
                        if ed.index == preEdgeIndex:
                            continue
                        delEdges.append(ed)
                        preEdgeIndex = ed.index
                        # print(ed.index)
            
            bmesh.ops.delete(bm,geom=delEdges,context="EDGES")

            bm.to_mesh(obj.data)

        # SVGファイルに図形をエクスポート
        # points = []

        # 出力するSVGファイルを開いておく(パーツごと)
        dwgAll = svgwrite.Drawing(saveSvgFilePath + 'all.svg', profile='tiny', size=(str(sumWidth + canvasPadding) + 'mm', str(maxHeight + canvasPadding) + 'mm'))
        for obj in targetObjects:
            if obj.type != "MESH" or obj.hide_viewport:
                obj.hide_viewport = False
                continue

            # 出力するSVGファイルを開いておく(パーツごと)
            dwg = svgwrite.Drawing(saveSvgFilePath + obj.name + '.svg', profile='tiny', size=(str(calc.lcLength(obj.dimensions[0]) + canvasPadding) + 'mm', str(calc.lcLength(obj.dimensions[1]) + canvasPadding) + 'mm'))

            mw = obj.matrix_world
            # 各オブジェクトの頂点の座標がオブジェクトローカルの座標になるので、0をオブジェクトの基準点にする
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False) 

            bm = bmesh.new()
            bm.from_mesh(obj.data)
            verts = []
            for ed in bm.edges:
                v1co = mw @ ed.verts[0].co
                v2co = mw @ ed.verts[1].co
                v1x = round(v1co.x * svgRate, 2)
                v1y = round(v1co.y * svgRate, 2)
                v2x = round(v2co.x * svgRate, 2)
                v2y = round(v2co.y * svgRate, 2)
                dwgAll.add(dwg.line((v1x, v1y), (v2x, v2y), stroke=svgwrite.rgb(255, 0, 0, '%'), stroke_width=0.32, fill='none'))
                dwg.add(dwg.line((v1x, v1y), (v2x, v2y), stroke=svgwrite.rgb(255, 0, 0, '%'), stroke_width=0.32, fill='none'))  #赤が切断と認識される

            bm.free()

            dwg.save()
        # dwgAll.save()

        bpy.ops.scene.delete()

        self.report({'INFO'}, "Svg output!!")
        return {'FINISHED'}
