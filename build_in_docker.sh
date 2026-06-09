#!/usr/bin/env bash
# Собирает APK в контейнере ubuntu:22.04, повторяя окружение GitHub Actions.
# ВАЖНО: сама сборка идёт на НАТИВНОЙ ФС контейнера (/build_native), а не на
# примонтированной Windows-папке /app — иначе drvfs не сохраняет +x и
# hostpython падает с "python: Permission denied" на generate-posix-vars.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "== [1/5] apt зависимости =="
apt-get update -qq
apt-get install -y -qq \
  build-essential git zip unzip rsync \
  openjdk-17-jdk \
  python3 python3-dev python3-pip python3-venv \
  autoconf libtool pkg-config \
  zlib1g-dev libncurses5 libncursesw5 \
  libffi-dev libssl-dev cmake ccache >/dev/null

echo "== [2/5] python / buildozer =="
python3 --version
pip3 install --upgrade pip -q
pip3 install -q buildozer "cython==0.29.34"

echo "== [3/5] синхронизирую исходники на нативную ФС (том /build_native) =="
mkdir -p /build_native
# .buildozer проекта НЕ трогаем — он лежит в томе и кэширует сборку между запусками
rsync -a --exclude='.buildozer' --exclude='bin' --exclude='.git' --exclude='__pycache__' /app/ /build_native/
cd /build_native
sed -i 's/\r$//' build_in_docker.sh 2>/dev/null || true

echo "== прокси для git/p4a (контейнер ходит в инет через хост: AmneziaWG) =="
# apt и pip уже отработали напрямую — проксируем только git-клоны зависимостей SDL,
# которые упираются в ТСПУ-сброс TLS до github.com.
export HTTP_PROXY="http://host.docker.internal:8899"
export HTTPS_PROXY="http://host.docker.internal:8899"
export http_proxy="$HTTP_PROXY"
export https_proxy="$HTTPS_PROXY"
git config --global http.proxy "$HTTP_PROXY"
git config --global https.proxy "$HTTPS_PROXY"
# на всякий: github через https стабильнее с http/1.1 и большим буфером
git config --global http.version HTTP/1.1
git config --global http.postBuffer 524288000

echo "== [4/5] сборка APK (нативная ext4) =="
# yes | buildozer под set -o pipefail валит скрипт кодом 141 (SIGPIPE от yes,
# когда buildozer завершился раньше). Берём реальный код buildozer из PIPESTATUS.
set +e
yes | buildozer android debug
BUILD_RC=${PIPESTATUS[1]}
set -e
echo "buildozer завершился с кодом: $BUILD_RC"

echo "== [5/5] копирую APK обратно в /app/bin =="
mkdir -p /app/bin
if cp -v /build_native/bin/*.apk /app/bin/ 2>/dev/null; then
  echo "APK скопирован в /app/bin"
  ls -la /app/bin/*.apk
else
  echo "APK не найден в /build_native/bin (buildozer rc=$BUILD_RC)"
  exit "${BUILD_RC:-1}"
fi
