FROM ubuntu:22.04 AS blender-installer
RUN apt-get update
RUN apt-get install -y xz-utils

RUN mkdir /tmp/blender
WORKDIR /tmp/blender

# blenderのバイナリはいい感じに持ってきておいてください。
COPY blender-4.2.1-linux-x64.tar.xz /tmp/blender/
RUN tar -xvf "./blender-4.2.1-linux-x64.tar.xz"


FROM ubuntu:22.04 as runtime

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN apt-get update && apt-get upgrade -y

ENV LAMBDA_TASK_ROOT="/app"
ENV FUNCTION_DIR="${LAMBDA_TASK_ROOT}"
RUN mkdir -p ${LAMBDA_TASK_ROOT}
WORKDIR ${LAMBDA_TASK_ROOT}

ENV TZ=Asia/Tokyo

# blender依存関係のインストール
RUN apt-get install glibc-source -y
RUN apt-get install -y libsm6 libxext6
RUN apt-get install -y libx11-dev libxxf86vm-dev libxcursor-dev libxi-dev libxrandr-dev libxinerama-dev libegl-dev
RUN apt-get install -y libwayland-dev wayland-protocols libxkbcommon-dev libdbus-1-dev linux-libc-dev

# blender本体のインストール
ENV BLENDER_DIR="/usr/local/blender"
ENV BLENDER_PATH="${BLENDER_DIR}/blender"
ENV BLENDER_PYTHON_PATH="${BLENDER_DIR}/4.2/python/bin/python3.11"
COPY --from=blender-installer /tmp/blender/blender-4.2.1-linux-x64 ${BLENDER_DIR}
ENV PATH="${BLENDER_PATH}:${PATH}"

# pythonのセットアップ
RUN apt-get install -y python3.11
RUN apt-get install -y --fix-missing python3-pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --target ${LAMBDA_TASK_ROOT} awslambdaric
RUN python -m pip install boto3

# 実行ファイルのコピー
COPY srcLambda/invoke_blender_rendering.py ${LAMBDA_TASK_ROOT}/invoke_blender_rendering.py
COPY srcLambda/app.py ${LAMBDA_TASK_ROOT}/app.py
COPY srcBlender/render.py ${LAMBDA_TASK_ROOT}/render.py
COPY srcBlender/template.blend ${LAMBDA_TASK_ROOT}/template.blend
ENV BLENDER_TEMPLATE_PATH="${LAMBDA_TASK_ROOT}/template.blend"
ENV BLENDER_SCRIPT_PATH="${LAMBDA_TASK_ROOT}/render.py"

# 実行コマンドの設定
COPY srcLambda/entry_script.sh ${LAMBDA_TASK_ROOT}/entry_script.sh
RUN chmod +x ${LAMBDA_TASK_ROOT}/entry_script.sh
ENTRYPOINT [ "./entry_script.sh" ]
CMD [ "app.lambda_handler" ]

