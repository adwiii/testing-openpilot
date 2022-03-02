#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
cd $DIR

# expose X to the container
xhost +local:root


docker pull ghcr.io/commaai/openpilot-sim@sha256:35ff99c6004869d97d05a90fa77668f732596d74886f9a5c5fe5003233536b2f

OPENPILOT_DIR="/openpilot"
if ! [[ -z "$MOUNT_OPENPILOT" ]]
then
  echo "Mounting openpilot"
  OPENPILOT_DIR="$(dirname $(dirname $DIR))"
  EXTRA_ARGS="-v $OPENPILOT_DIR:$OPENPILOT_DIR -e PYTHONPATH=$OPENPILOT_DIR:$PYTHONPATH"
fi

docker run --net=host\
  --name openpilot_client \
  --init \
  --rm \
  -it \
  --gpus all \
  --device=/dev/dri:/dev/dri \
  --device=/dev/input:/dev/input \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $TEST_DIRECTORY:/test_directory \
  --shm-size 1G \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -w "$OPENPILOT_DIR/tools/sim" \
  $EXTRA_ARGS \
  ghcr.io/commaai/openpilot-sim:latest \
  /bin/bash -c "./tmux_script.sh $*"
