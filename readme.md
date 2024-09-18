
## blenderのダウンロード
```bash
wget https://mirror.freedif.org/blender/release/Blender4.2/blender-4.2.1-linux-x64.tar.xz
```

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
TAG="v0.0"

docker build -t ${REPO_NAME} . || exit 1

# イメージプッシュ
docker tag ${REPO_NAME} "${ECR_URL}/${REPO_NAME}:${TAG}"
aws ecr get-login-password --region "${REGION}" | docker login --username AWS --password-stdin "${ECR_URL}"
docker push "${ECR_URL}/${REPO_NAME}:${TAG}"
```
