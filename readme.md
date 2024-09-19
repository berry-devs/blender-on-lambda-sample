# 準備
## blenderのダウンロード
```bash
wget https://mirror.freedif.org/blender/release/Blender4.2/blender-4.2.1-linux-x64.tar.xz
```

# デプロイ
## イメージのビルドとプッシュ
```bash
# もしリポジトリがない場合は作成してください
REPO_NAME=blender-on-lambda-test
aws ecr describe-repositories --repository-names ${REPO_NAME} || aws ecr create-repository --repository-name ${REPO_NAME}
```

```bash
REGION=$(aws configure get region)
REPO_NAME=blender-on-lambda-test
ACCOUNTID=$(aws sts get-caller-identity --query Account --output text)
ECR_URL=${ACCOUNTID}.dkr.ecr.${REGION}.amazonaws.com
TAG="test"

docker build -t ${REPO_NAME} . || exit 1

# イメージプッシュ
docker tag ${REPO_NAME} "${ECR_URL}/${REPO_NAME}:${TAG}"
aws ecr get-login-password --region "${REGION}" | docker login --username AWS --password-stdin "${ECR_URL}"
docker push "${ECR_URL}/${REPO_NAME}:${TAG}"
```

## Lambda関数の作成
- レンダリングにそこそこスペックが必要なのでリソースは盛ってます。
- lambdaのCPUリソースはメモリによって決まるためメモリは最大値に設定しています。

```bash
aws lambda create-function \
    --function-name blender-on-lambda-test \
    --package-type Image \
    --code ImageUri=${ECR_URL}/${REPO_NAME}:${TAG} \
    --role <your_role_arn> \
    --timeout 180 \
    --memory-size 10240 \
    --region ${REGION}
```



## サンプルデータのアップロード
サンプルデータは[こちら](https://sketchfab.com/3d-models/lekking-ruffs-f5e8e5a459a14e2fb46f7d79f6ca7edc)よりお借りした物を編集して使用しています。(CC0 Public Domain)

```bash
aws s3 cp ./sampleData/ s3://<your_bucket_name>/  --recursive
```

## Lambda関数の実行
```bash
aws lambda invoke \
    --function-name blender-on-lambda-test \
    --payload file://testEvent.json \
    --cli-binary-format raw-in-base64-out \
    output.json
```

## 結果のダウンロード
```bash
aws s3 cp s3://<your_bucket_name>/test_result.png .
```
