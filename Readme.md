# Welcome to your CDK Python project with LocalStack!

For better cdklocal experience you should set `DEFAULT_REGION` env variable. In that case you won't need to provide `--region` parameter to `awslocal` commands. You should use this variable when deploying your stack. It's worth to mention that you could have `$(aws configure get region)` already set, but it's not used with `awslocal`. You can also use `aws ... --endpoint-url http://localhost:4566` commands instead of `awslocal`. In any case, pay attention to the region you use.

Domain `localhost.localstack.cloud` resolves to `127.0.0.1`.

1. Open in VSCode as container
1. Bootstrap with: `cdklocal bootstrap`
1. Deploy with: `cdklocal deploy`
1. Perform few calls with curl: `curl https://$(awslocal apigateway get-rest-apis --query "items[?name=='hello'].{id:id}" --output text).execute-api.localhost.localstack.cloud:4566/prod/path`

### DynamoDb
1. Get created db with: `awslocal dynamodb list-tables`
1. Get data from db with: `awslocal dynamodb scan --table-name [TABLE_NAME]`

### get lambda zip
```
LAMBDA_URL=$(awslocal lambda get-function --function-name trigger-handler --query 'Code.Location' --output text)
curl -o trigger-handler.zip $LAMBDA_URL
mkdir lambda && unzip trigger-handler.zip -d lambda
```

### get layer zip
```
LAYER_URL=$(awslocal lambda get-layer-version --layer-name base-layer --version-number 1 --query Content.Location --output text)
curl -o base-layer.zip $LAYER_URL
mkdir layer && unzip base-layer.zip -d layer
```

### Logs
1. Get all log groups: `awslocal logs describe-log-groups`
1. Get logs: `awslocal logs tail [logGroupName] [--follow arg]`

### Alarms:
1. `aws cloudwatch set-alarm-state --alarm-name cdk-workshop-DeploymentAlarmTimeout18140A5C-10VQZUQYSJXS6 --state-reason 'my reason' --state-value OK`
1. `aws cloudwatch set-alarm-state --alarm-name cdk-workshop-DeploymentAlarmTimeout18140A5C-10VQZUQYSJXS6 --state-reason 'my reason' --state-value ALARM`

 `aws lambda list-functions | jq '.Functions[].FunctionName'`
 Get logical ID of HelloHandler
 `cat $(find ./cdk.out/cdk-workshop.template.json) | jq -r '.Resources | to_entries[] | select((.key | contains("Hello")) and (.value.Type | contains("Function"))) | .key'`