# Welcome to your CDK Python project with LocalStack!

1. Open in VSCode as container
1. Bootstrap with: cdklocal bootstrap
1. Deploy with: cdklocal deploy
1. After deploy you should get url with your lambda. Something like: https://ndbdjp72uz.execute-api.localhost.localstack.cloud:4566/prod/
1. Add FQDN to your /etc/hosts with: echo "127.0.0.1 [FQDN]" | sudo tee -a /etc/hosts
1. Perform few calls with curl: curl https://ndbdjp72uz.execute-api.localhost.localstack.cloud:4566/prod/path
1. Get created db with: aws dynamodb list-tables --endpoint-url http://localhost:4566
1. Get data from db with: aws dynamodb scan --table-name [TABLE_NAME] --endpoint-url http://localhost:4566
