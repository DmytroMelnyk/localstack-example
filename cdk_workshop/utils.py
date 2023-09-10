import pathlib
import platform
from enum import Enum

from aws_cdk import BundlingOptions, DockerImage
from aws_cdk.aws_ecr_assets import Platform
from aws_cdk.aws_lambda import Code


class CodeType(Enum):
    Docker = 1
    DockerBuild = 2
    BuildInDocker = 3


def get_lambda_code(type: CodeType, entry: str, index: str):
    match type:
        case CodeType.BuildInDocker:
            # equialent to aws_lambda_python_alpha.PythonFunction
            return Code.from_asset(
                path=entry,
                bundling=BundlingOptions(
                    # https://gallery.ecr.aws/sam?architectures=ARM+64&operatingSystems=Linux
                    image=DockerImage.from_registry(
                        "public.ecr.aws/sam/build-python3.9:latest-arm64"
                        if platform.machine().lower() in ["arm64", "aarch64"]
                        else "public.ecr.aws/sam/build-python3.9:latest"
                    ),
                    command=["bash", "./build.sh"],
                    environment={
                        "PIP_NO_CACHE_DIR": "TRUE",
                        "PIP_DISABLE_PIP_VERSION_CHECK": "TRUE",
                        "LAMBDA_ROOT_PATH": f"{pathlib.Path(index).parent}",
                    },
                ),
            )
        case CodeType.DockerBuild:
            return Code.from_docker_build(
                file="Dockerfile",
                path=entry,
                image_path="/var/task/lambda",  # LAMBDA_TASK_ROOT from public.ecr.aws/lambda/python images
                build_args={"LAMBDA_ROOT_PATH": f"{pathlib.Path(index).parent}"},
            )
        case CodeType.Docker:
            # equialent to aws_lambda.DockerImageFunction
            return Code.from_asset_image(
                directory=entry,
                file="Dockerfile",
                platform=Platform.LINUX_ARM64,
                working_directory="/",
                build_args={"LAMBDA_ROOT_PATH": f"{pathlib.Path(index).parent}"},
                cmd=[f"lambda/{index.removesuffix('.py')}.handler"],
            )
