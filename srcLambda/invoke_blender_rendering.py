import subprocess
import os


def invoke_blender_rendering(
        obj_path: str,
        dst_path: str,
        img_size: int
):
    cmd = get_cmd(
        obj_path,
        dst_path,
        img_size
    )

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Failed to render: {result.returncode}")
    else:
        print("Rendered successfully")

def get_cmd(
    obj_path: str,
    dst_path: str,
    img_size: int
) -> list[str]:
    blender_path = os.getenv("BLENDER_PATH", "/usr/local/blender/blender")
    assert os.path.exists(blender_path), f"BLENDER_PATH does not exist: {blender_path}"

    script_path = os.getenv("BLENDER_SCRIPT_PATH", "/app/srcBlender/render.py")
    assert os.path.exists(script_path), f"BLENDER_SCRIPT_PATH does not exist: {script_path}"

    template_blend_path = os.getenv("BLENDER_TEMPLATE_PATH", "/app/srcBlender/template.blend")
    assert os.path.exists(template_blend_path), f"BLENDER_TEMPLATE_PATH does not exist: {template_blend_path}"

    return [
        blender_path,
        "--background",
        "--python", script_path,
        "--",
        "--obj_path", obj_path,
        "--dst_path", dst_path,
        "--template_blend_path", template_blend_path,
        "--outputSize", img_size
    ]
