REPO_ROOT=tintoyddr.azurecr.io/glider-gun
REPO_BASE=${REPO_ROOT}/base

VAULT2ENV_VERSION=v0.0.2

IMAGE_TAG_UBUNTU_XENIAL=${REPO_BASE}/ubuntu:xenial

## Build

build: build.ubuntu

build.ubuntu: build.ubuntu-xenial

build.ubuntu-xenial:
	docker build -t ${IMAGE_TAG_UBUNTU_XENIAL} --build-arg VAULT2ENV_VERSION=${VAULT2ENV_VERSION} -f ubuntu-xenial.Dockerfile .

## Push

push: push.ubuntu

push.ubuntu: push.ubuntu-xenial

push.ubuntu-xenial:
	docker push ${IMAGE_TAG_UBUNTU_XENIAL}
