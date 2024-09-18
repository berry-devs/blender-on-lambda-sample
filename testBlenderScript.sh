#!/bin/bash

BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
script_path=$(pwd)/srcBlender/render.py

${BLENDER_PATH} \
  --python ${script_path} \
  --background \
  -- \
  --obj_path $(pwd)/sampleData/sample_obj.obj \
  --dst_path $(pwd)/result.png \
  --template_blend_path $(pwd)/srcBlender/template.blend \
  --outputSize 512 \
