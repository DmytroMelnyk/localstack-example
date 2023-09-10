#!/usr/bin/env python3

import os

import aws_cdk as cdk

from cdk_workshop.base_layer_stack import BaseLayerStack
from cdk_workshop.cdk_workshop_stack import CdkWorkshopStack

# debugging
# import debugpy
# debugpy.listen(("0.0.0.0", 5678))
# print("Waiting for debugger attach")
# debugpy.wait_for_client()
# debugpy.breakpoint()
app = cdk.App()
env = cdk.Environment(region=os.environ["DEFAULT_REGION"])
base_lambda_layer_stack: BaseLayerStack = BaseLayerStack(app, "base-layer", env=env)
CdkWorkshopStack(
    app, "cdk-workshop", base_lambda_layer=base_lambda_layer_stack.base_layer, env=env
)

app.synth()
