import os
from uuid import uuid4
import shutil
from typing import Any

import boto3
from invoke_blender_rendering import invoke_blender_rendering


def download(bucket_name: str, key: str, file_path: str):
    s3 = boto3.client("s3")
    dst_dir = os.path.dirname(file_path)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    s3.download_file(bucket_name, key, file_path)


def upload(bucket_name: str, key: str, file_path: str):
    s3 = boto3.client("s3")
    s3.upload_file(file_path, bucket_name, key)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, str]:
    # イベントの内容を取得
    bucket_name = event.get('bucket_name')
    assert isinstance(bucket_name, str)

    obj_key = event.get('obj_key')
    assert isinstance(obj_key, str)

    mtl_key = event.get('mtl_key')
    assert isinstance(mtl_key, str)

    texture_key = event.get('texture_key')
    assert isinstance(texture_key, str)

    upload_dst_key = event.get('upload_dst_key')
    assert isinstance(upload_dst_key, str)

    img_size = event.get('img_size', 512)
    assert isinstance(img_size, int) or isinstance(img_size, float)
    img_size: int = int(img_size)

    # 作業ディレクトリを作成
    tmp_path = f'/tmp/{uuid4()}'
    src_path = f'{tmp_path}/src'
    dst_path = f'{tmp_path}/dst'

    os.makedirs(tmp_path)
    os.makedirs(src_path)
    os.makedirs(dst_path)

    # エラーが起きてもtmpディレクトリを削除したいのでtry-finallyで囲む
    try:
        local_obj_path = f'{src_path}/{os.path.basename(obj_key)}'
        local_mtl_path = f'{src_path}/{os.path.basename(mtl_key)}'
        local_texture_path = f'{src_path}/{os.path.basename(texture_key)}'
        local_dst_path = f'{dst_path}/{os.path.basename(upload_dst_key)}'

        # データをダウンロード
        download(bucket_name, obj_key, local_obj_path)
        download(bucket_name, mtl_key, local_mtl_path)
        download(bucket_name, texture_key, local_texture_path)

        # メインの処理
        invoke_blender_rendering(
            local_obj_path,
            local_dst_path,
            img_size
        )

        # アップロードとローカルファイルの削除
        upload(bucket_name, upload_dst_key, local_dst_path)

    finally:
        # 保存したファイルをそのままにするとリクエストが重なった時にリクエストが失敗するので削除する
        shutil.rmtree(tmp_path)

    return {
        'bucket_name': bucket_name,
        'result_image_key': upload_dst_key,
    }
