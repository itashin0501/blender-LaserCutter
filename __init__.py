bl_info = {
    "name" : "Laser Cutter",
    "author" : "itamoto",
    "description" : "Tool for making laser cutter object",
    "blender" : (2, 82, 0),
    "version" : (0, 0, 1),
    "location" : "Panel > LaserCutter",
    "warning": "There are only certain laser cutter settings.",
    "wiki_url" : "https://github.com/itashin0501/blender-LaserCutter",
    "support": "TESTING",
    "category" : "3D View"
}

import bpy
from .output_svg import LC_OT_SVG
from .clean_mesh import CleanMesh
from .cross_cut import CrossCutA, CrossCutB
from .convert_to_board import BoxConvertToBoard

from bpy.props import IntProperty, FloatProperty, StringProperty
from bpy.props import EnumProperty, FloatVectorProperty

class OpenBrowser(bpy.types.Operator):
    bl_idname = "open.browser"
    bl_label = "OK"

    filepath = bpy.props.StringProperty(subtype="DIR_PATH") 

    def execute(self, context):
        display = self.filepath  
        bpy.types.Scene.savedirectory = self.filepath
        print(display) #Prints to console  
        return {'FINISHED'}

    def invoke(self, context, event):
    
        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}  

class LC_PT_PanelMenu(bpy.types.Panel):
    bl_category = "LaserCutter"         # メニュータブのラベル
    bl_label = "LaserCutter Setting"    # メニュー開いた上部のラベル
    bl_space_type = 'VIEW_3D'           # メニューを表示するエリア
    bl_region_type = 'UI'               # メニューを表示するリージョン
    bl_context = "objectmode"           # パネルを表示するコンテキスト
    
    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return True
        else:
            return False

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        self.layout.label(text="", icon='IPO_CONSTANT')

    # メニューの描画処理
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Board")
        layout.prop(scene, "thicknessBoardF", text="thickness(mm)")

        layout.label(text="Select output directory")
        layout.operator(OpenBrowser.bl_idname)
        if bpy.types.Scene.savedirectory == "":
            layout.label(text="please select!")
        else:
            layout.label(text=bpy.types.Scene.savedirectory)

        # レーザーカッター用のSVGファイル出力までの処理を実行するボタン
        layout.separator()
        layout.operator(LC_OT_SVG.bl_idname, text="OUTPUT SVG")

        # 立体を板を張り合わせたオブジェクトに変換するボタン
        layout.separator()
        layout.operator(BoxConvertToBoard.bl_idname, text="CONVERT BOARD")

        # 消したオブジェクトのMESHだけ残ってしまったものを削除する
        layout.separator()
        layout.operator(CleanMesh.bl_idname, text="CLEAN")

class LC_PT_PanelMenuEd(bpy.types.Panel):
    bl_category = "LaserCutter"         # メニュータブのラベル
    bl_label = "LaserCutter Setting"    # メニュー開いた上部のラベル
    bl_space_type = 'VIEW_3D'           # メニューを表示するエリア
    bl_region_type = 'UI'               # メニューを表示するリージョン

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            return True
        else:
            return False

    # メニューの描画処理
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Board")
        layout.prop(scene, "thicknessBoardF", text="thickness(mm)")
        layout.prop(scene, "divideNum", text="divideNum")
        layout.operator(CrossCutA.bl_idname, text="CROSS CUT 凸")
        layout.operator(CrossCutB.bl_idname, text="CROSS CUT 凹")

classes = [
    LC_OT_SVG,
    BoxConvertToBoard,
    CleanMesh,
    CrossCutA,
    CrossCutB,
    OpenBrowser,
    LC_PT_PanelMenu,
    LC_PT_PanelMenuEd
]

# プロパティの初期化
def init_props():
    scene = bpy.types.Scene

    scene.thickness = 2
    scene.savedirectory = ""
    scene.dividenum = 3

    scene.thicknessBoardF = bpy.props.FloatProperty(
        name="thicknessBoardF",
        description="thicknessOfBoard Property",
        min=0.1,
        max=50,
        step=50,
        get=get_thickness,
        set=set_thickness
    )

    scene.divideNum = bpy.props.IntProperty(
        name="divideNum",
        description="divideNum Property",
        min=3,
        max=9,
        step=2,
        get=get_dividenum,
        set=set_devidenum
    )

def get_thickness(self):
    return bpy.types.Scene.thickness

def set_thickness(self, value):
    bpy.types.Scene.thickness = value

def get_dividenum(self):
    return bpy.types.Scene.dividenum

def set_devidenum(self, value):
    bpy.types.Scene.dividenum = value

# プロパティを削除
def clear_props():
    scene = bpy.types.Scene
    del scene.thicknessBoardF
    del scene.savedirectory
    del scene.divideNum

# アドオン有効化時の処理
def register():
    init_props()

    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            print('register Error')
    print("Add-on:ON")

# アドオン無効化時の処理
def unregister():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            print('Error')
    clear_props()
    print("Add-on:OFF")

# メイン関数
if __name__ == "__main__":
    register()
