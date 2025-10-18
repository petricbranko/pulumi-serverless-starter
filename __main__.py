"""
Pulumi Serverless Starter Template
Deploys AWS Lambda, DynamoDB, API Gateway with optional custom domain
Supports auto-discovery of multiple Lambda functions and API Gateway mappings
"""

import pulumi
import pulumi_aws as aws
from infrastructure.lambda_function import create_lambda_function
from infrastructure.lambda_discovery import create_lambda_functions
from infrastructure.dynamodb import create_dynamodb_table
from infrastructure.api_gateway import create_api_gateway
from infrastructure.api_mappings import create_api_gateways_with_mappings
from infrastructure.domain import setup_custom_domain

# Get configuration
config = pulumi.Config()
stack_name = pulumi.get_stack()

# Project configuration
project_name = config.get("projectName") or "serverless-app"

# DynamoDB configuration
enable_dynamodb = config.get_bool("enableDynamoDB")
if enable_dynamodb is None:
    enable_dynamodb = True

dynamodb_table_name = config.get("dynamodbTableName") or "app-table"
dynamodb_hash_key = config.get("dynamodbHashKey") or "id"
dynamodb_billing_mode = config.get("dynamodbBillingMode") or "PAY_PER_REQUEST"
dynamodb_enable_pitr = config.get_bool("dynamodbEnablePITR")
if dynamodb_enable_pitr is None:
    dynamodb_enable_pitr = True
dynamodb_enable_encryption = config.get_bool("dynamodbEnableEncryption")
if dynamodb_enable_encryption is None:
    dynamodb_enable_encryption = True

# Lambda configuration
lambda_auto_discover = config.get_bool("lambdaAutoDiscover")
if lambda_auto_discover is None:
    lambda_auto_discover = True

lambda_functions_directory = config.get("lambdaFunctionsDirectory") or "./lambda_functions"
lambda_default_runtime = config.get("lambdaDefaultRuntime") or "python3.11"
lambda_default_handler = config.get("lambdaDefaultHandler") or "index.handler"
lambda_default_memory_size = config.get_int("lambdaDefaultMemorySize") or 256
lambda_default_timeout = config.get_int("lambdaDefaultTimeout") or 30

# API Gateway configuration
api_gateway_default_name = config.get("apiGatewayDefaultName") or "serverless-api"
api_gateway_mappings = config.get("apiGatewayMappings") or ""

# Custom domain configuration
enable_custom_domain = config.get_bool("enableCustomDomain") or False
domain_name = config.get("domainName") or ""
subdomain = config.get("subdomain") or "api"

# Create DynamoDB table (optional)
table = None
table_arn = None
table_name_output = None

if enable_dynamodb:
    table = create_dynamodb_table(
        name=dynamodb_table_name,
        hash_key=dynamodb_hash_key,
        attributes=[{"name": dynamodb_hash_key, "type": "S"}],
        billing_mode=dynamodb_billing_mode,
        point_in_time_recovery=dynamodb_enable_pitr,
        server_side_encryption=dynamodb_enable_encryption,
        tags={
            "Environment": stack_name,
            "Project": project_name
        }
    )
    table_arn = table.arn
    table_name_output = table.name
    pulumi.log.info(f"DynamoDB table created: {dynamodb_table_name}")

# Create Lambda functions (auto-discovery or manual)
lambda_functions = {}

if lambda_auto_discover:
    # Auto-discover and create Lambda functions
    lambda_functions = create_lambda_functions(
        functions_directory=lambda_functions_directory,
        default_runtime=lambda_default_runtime,
        default_handler=lambda_default_handler,
        default_memory_size=lambda_default_memory_size,
        default_timeout=lambda_default_timeout,
        table_arn=table_arn,
        table_name=table_name_output,
        stack_name=stack_name
    )

# Create API Gateways with mappings
apis = create_api_gateways_with_mappings(
    lambda_functions=lambda_functions,
    mappings_config=api_gateway_mappings,
    default_api_name=api_gateway_default_name,
    stage_name=stack_name
)

# Setup custom domain (optional) - only for default/first API
custom_domain_result = None
if enable_custom_domain and domain_name and apis:
    # Apply custom domain to the first/default API Gateway
    first_api_key = list(apis.keys())[0]
    first_api = apis[first_api_key]["api"]

    custom_domain_result = setup_custom_domain(
        domain_name=domain_name,
        subdomain=subdomain,
        api_gateway_stage=first_api,
        certificate_region="us-east-1"
    )
    pulumi.log.info(f"Custom domain configured for API: {first_api_key}")

# Export outputs
# Export Lambda functions
pulumi.export("lambdaFunctions", {
    name: {
        "name": func.name,
        "arn": func.arn
    } for name, func in lambda_functions.items()
})

# Export API Gateways
api_outputs = {}
for api_name, api_config in apis.items():
    api_outputs[api_name] = {
        "url": api_config["url"],
        "functions": api_config["functions"]
    }
pulumi.export("apiGateways", api_outputs)

# Export DynamoDB table info (if created)
if enable_dynamodb and table:
    pulumi.export("dynamoDbTableName", table.name)
    pulumi.export("dynamoDbTableArn", table.arn)

# Export custom domain info (if configured)
if custom_domain_result:
    pulumi.export("customDomainName", custom_domain_result["domain_name"])
    pulumi.export("certificateArn", custom_domain_result["certificate_arn"])

# Export summary
pulumi.export("summary", {
    "projectName": project_name,
    "environment": stack_name,
    "lambdaFunctionsCount": len(lambda_functions),
    "apiGatewaysCount": len(apis),
    "dynamoDbEnabled": enable_dynamodb
})