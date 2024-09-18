import os
import bpy  # type: ignore
from mathutils import Vector  # type: ignore
from typing import NamedTuple


class RenderCfg(NamedTuple):
    obj_path: str
    dst_path: str
    template_blend_path: str
    outputSize: int


def import_geo_file(file_path: str):  # type: ignore
    ext = os.path.splitext(file_path)[1]
    assert ext in [".obj", ".OBJ"], f"Unsupported file type: {ext}"
    bpy.ops.wm.obj_import(filepath=file_path)  # type: ignore


def render_main(cfg: RenderCfg):
    bpy.ops.wm.open_mainfile(filepath=cfg.template_blend_path)  # type: ignore

    bpy.context.scene.render.resolution_x = cfg.outputSize  # type: ignore
    bpy.context.scene.render.resolution_y = cfg.outputSize  # type: ignore

    # シーンのカメラを設定
    camera = bpy.data.objects["Camera"]  # type: ignore
    bpy.context.scene.camera = camera  # type: ignore
    bpy.context.scene.frame_start = 1  # type: ignore
    bpy.context.scene.frame_end = 1  # type: ignore

    # レンダリングサンプリングに設定
    bpy.data.scenes["Scene"].eevee.taa_render_samples = 1  # type: ignore

    # レンダリング出力先を設定
    bpy.context.scene.render.filepath = cfg.dst_path  # type: ignore
    ext = os.path.splitext(cfg.dst_path)[1]

    # 出力をマルチレイヤーEXRに設定
    if ext.lower() == ".exr":
        bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'  # type: ignore
    elif ext.lower() == ".png":
        bpy.context.scene.render.image_settings.file_format = 'PNG'  # type: ignore
    elif ext.lower() == ".jpg":
        bpy.context.scene.render.image_settings.file_format = 'JPEG'  # type: ignore
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    import_geo_file(cfg.obj_path)

    # アニメーションをレンダリング
    bpy.ops.render.render(animation=False, write_still=True)  # type: ignore


if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--obj_path', type=str, required=True)
    parser.add_argument('--dst_path', type=str, required=True)
    parser.add_argument('--template_blend_path', type=str, required=True)
    parser.add_argument('--outputSize', type=int, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])

    cfg = RenderCfg(
        obj_path=args.obj_path,
        dst_path=args.dst_path,
        template_blend_path=args.template_blend_path,
        outputSize=args.outputSize
    )

    render_main(cfg)
