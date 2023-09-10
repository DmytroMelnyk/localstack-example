FROM public.ecr.aws/lambda/python:3.10

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # this 2 are need to keep in sync docker build 
    # and lambda as docker
    PIP_TARGET=$LAMBDA_TASK_ROOT/lambda \
    PYTHONPATH=$LAMBDA_TASK_ROOT/lambda 

WORKDIR $LAMBDA_TASK_ROOT/lambda 
COPY common/requirements.txt common/
RUN pip install -r common/requirements.txt

ARG LAMBDA_ROOT_PATH
# requirements for certain function may exist or not. 
# use glob pattern: https://en.wikipedia.org/wiki/Glob_(programming)
COPY $LAMBDA_ROOT_PATH/requirements.tx[t] $LAMBDA_ROOT_PATH/
RUN if [ -f "$LAMBDA_ROOT_PATH/requirements.txt" ]; then pip install -r $LAMBDA_ROOT_PATH/requirements.txt --upgrade; fi

COPY common/ common
COPY $LAMBDA_ROOT_PATH/ $LAMBDA_ROOT_PATH

WORKDIR $LAMBDA_TASK_ROOT