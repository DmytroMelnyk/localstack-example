import platform

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_apigateway as apigw,
    custom_resources as cr,
    aws_iam as iam
)
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
)
from aws_cdk import (
    aws_codedeploy as codedeploy,
)
from aws_cdk import (
    aws_dynamodb as ddb,
)
from aws_cdk import (
    aws_lambda as _lambda,
)
from aws_cdk import (
    aws_lambda_python_alpha as _plambda,
)
from aws_cdk import (
    aws_sns as sns,
)
from aws_cdk import (
    aws_sns_subscriptions as subs,
)
from aws_cdk import (
    aws_sqs as sqs,
    aws_logs as logs,
)
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_lambda import Function, StartingPosition
from constructs import Construct

from .utils import CodeType, get_lambda_code

def create_batch_insert_object(tableName: str, items):
    itemsAsDynamoPutRequest = [{"PutRequest": {"Item": item}} for item in items]
    records = {"RequestItems": {}}
    records["RequestItems"][tableName] = itemsAsDynamoPutRequest
    return records


class CdkWorkshopStack(Stack):
    # lambda settings
    lambda_timeout = Duration.seconds(3)
    is_canary = False

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        base_lambda_layer: _plambda.PythonLayerVersion,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table: Table = ddb.Table(
            self,
            "Hits",
            table_name="hits-counter-table",
            partition_key={"name": "path", "type": ddb.AttributeType.STRING},
            stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=RemovalPolicy.DESTROY
        )

        queue = sqs.Queue(
            self,
            "CdkWorkshopQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(self, "CdkWorkshopTopic")

        topic.add_subscription(subs.SqsSubscription(queue))

        timeout = Duration.seconds(3)
        my_lambda = self.create_lambda(
            "HelloHandler",
            "hello-handler",
            "src",
            "hello/hello.py",
            timeout=timeout,
            env={
                "HITS_TABLE_NAME": table.table_name,
            },
        )
        table.grant_read_write_data(my_lambda)
        # self.insert_data_to_dynamodb(table)

        # ApiGatewayToLambda(self, "endpoint", existing_lambda_obj=my_lambda)
        apigw.LambdaRestApi(
            self,
            id="hello",
            handler=my_lambda
            if not self.is_canary
            else self.blueGreenDeployment(
                my_lambda, codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_5_MINUTES
            ),
        )

        logs.QueryDefinition(
            self,
            "ColdStart",
            query_definition_name="cold-start-query",
            query_string=logs.QueryString(parse="""filter @type = "REPORT"
              | stats count(@type) as countInvocations, 
                count(@initDuration) as countColdStarts, 
                (count(@initDuration)/count(@type))*100 as percentageColdStarts,
                max(@initDuration) as maxColdStartTime,
                avg(@initDuration) as avgColdStartTime,
                avg(@duration) as averageDuration,
                max(@duration) as maxDuration,
                min(@duration) as minDuration,
                avg(@maxMemoryUsed) as averageMemoryUsed,
                max(@memorySize) as memoryAllocated, 
                (avg(@maxMemoryUsed)/max(@memorySize))*100 as percentageMemoryUsed 
              by bin(1h) as timeFrame""")
        )

        api_lambda = self.create_lambda(
            "ApiHandler",
            "api-handler",
            "src",
            "api/api.py",
            timeout=timeout,
        )

        apigw.LambdaRestApi(
            self,
            id="api",
            handler=api_lambda
            if not self.is_canary
            else self.blueGreenDeployment(
                api_lambda,
                codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_5_MINUTES,
            ),
        )

        trigger_lambda: Function = self.create_lambda(
            "TriggerHandler",
            "trigger-handler",
            "src",
            "trigger/trigger.py",
            {
                "HITS_TABLE_NAME": table.table_name,
            },
        )

        table.grant_stream_read(trigger_lambda)

        trigger_lambda.add_event_source_mapping(
            "trigger_mapping",
            event_source_arn=table.table_stream_arn,
            max_batching_window=Duration.seconds(1),
            starting_position=StartingPosition.LATEST,
            batch_size=10,
            retry_attempts=5,
        )

    def insert_data_to_dynamodb(self, table: ddb.Table):
        initializeData = cr.AwsSdkCall(
            action="batchWriteItem",
            service="DynamoDB",
            physical_resource_id=cr.PhysicalResourceId.of(
                f"{table.table_name}-batch-write"
            ),
            parameters=create_batch_insert_object(
                table.table_name,
                [
                    {
                        "tenant_id": {"S": "73"},
                        "path": {"S": "//"},
                    },
                    {
                        "tenant_id": {"S": "73"},
                        "path": {"S": "///"},
                    },
                ],
            ),
        )
        
        cr.AwsCustomResource(
            self,
            "aws-custom",
            policy=cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=["dynamodb:BatchWriteItem"],
                        resources=[ table.table_arn ],
                    ),
                ]
            ),
            on_create=initializeData,
            on_update=initializeData,
        )

    def create_lambda(
        self,
        id: str,
        name: str,
        entry: str,
        index: str,
        env: dict[str, str] = {},
        timeout=Duration.seconds(3),
        lambda_type = CodeType.DockerBuild
    ) -> _lambda.Function:
        lambda_code = get_lambda_code(lambda_type, entry, index)
        return _lambda.Function(
            self,
            id,
            function_name=name,
            architecture=_lambda.Architecture.ARM_64
            if platform.machine().lower() in ["arm64", "aarch64"]
            else _lambda.Architecture.X86_64,
            runtime=_lambda.Runtime.FROM_IMAGE
            if lambda_type == CodeType.Docker
            else _lambda.Runtime.PYTHON_3_10,
            code=lambda_code,
            timeout=timeout,
            handler=_lambda.Handler.FROM_IMAGE
            if lambda_type == CodeType.Docker
            else f"{index.removesuffix('.py')}.handler",
            environment=env,
        )

    def blueGreenDeployment(
        self,
        function: _lambda.Function,
        deployment_config: codedeploy.LambdaDeploymentConfig,
    ) -> _lambda.Alias:
        new_version = function.current_version
        new_version.apply_removal_policy(RemovalPolicy.RETAIN)
        alias: _lambda.Alias = _lambda.Alias(
            self, "BlueGreenAlias", alias_name="live", version=new_version
        )

        lambda_alarm_errors = cloudwatch.Alarm(
            self,
            "DeploymentAlarmError",
            metric=alias.metric_errors(),
            threshold=1,
            alarm_description=f"{function.function_name} {new_version.version} blue green deployment failure alarm. Errors",
            evaluation_periods=1,
        )

        # looks like it's not needed
        # lambda_alarm_timeouts: cloudwatch.Alarm = cloudwatch.Alarm(
        #     self, 'DeploymentAlarmTimeout',
        #     metric=alias.metric_duration(statistic="max"),
        #     threshold=self.lambda_timeout.to_milliseconds(),
        #     alarm_description=f'{function.function_name} {new_version.version} blue green deployment failure alarm. Timeouts',
        #     evaluation_periods=1,
        # )

        deployment_config = (
            codedeploy.LambdaDeploymentConfig.CANARY_10_PERCENT_5_MINUTES
        )

        codedeploy.LambdaDeploymentGroup(
            self,
            "MyLambdaDeploymentGroup",
            alias=alias,
            deployment_config=deployment_config
            if deployment_config
            else codedeploy.LambdaDeploymentConfig.ALL_AT_ONCE,
            alarms=[lambda_alarm_errors],
        )

        return alias
