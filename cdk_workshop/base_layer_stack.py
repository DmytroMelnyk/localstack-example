import platform

from aws_cdk import (
    DockerImage,
    Stack,
)
from aws_cdk import (
    aws_lambda as _lambda,
)
from aws_cdk import (
    aws_lambda_python_alpha as _plambda,
)
from constructs import Construct


class BaseLayerStack(Stack):
    base_layer: _plambda.PythonLayerVersion

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # this layer contains requirements.txt
        self.base_layer = _plambda.PythonLayerVersion(
            self,
            "BaseLayer",
            layer_version_name="base-layer",
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            bundling=_plambda.BundlingOptions(
                # https://gallery.ecr.aws/sam?architectures=ARM+64&operatingSystems=Linux
                image=DockerImage.from_registry(
                    "public.ecr.aws/sam/build-python3.9:latest-arm64"
                    if platform.machine().lower() in ["arm64", "aarch64"]
                    else "public.ecr.aws/sam/build-python3.9:latest"
                )
            ),
            compatible_architectures=[
                _lambda.Architecture.ARM_64
                if platform.machine().lower() in ["arm64", "aarch64"]
                else _lambda.Architecture.X86_64,
            ],
            entry="src/common",
        )
