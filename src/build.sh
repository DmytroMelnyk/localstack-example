#!/bin/bash
OUT_DIR="asset-output" # the path is expected as a result of bundler's work

EXTRA_REQ=$(if [ -f "${LAMBDA_ROOT_PATH}/requirements.txt" ]; then echo "-r ${LAMBDA_ROOT_PATH}/requirements.txt"; fi)
pip install -r common/requirements.txt $EXTRA_REQ -t /$OUT_DIR

cp -au common /$OUT_DIR/common
cp -au $LAMBDA_ROOT_PATH /$OUT_DIR/$LAMBDA_ROOT_PATH
