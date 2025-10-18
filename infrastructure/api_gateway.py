"""API Gateway infrastructure module"""

import json
import pulumi
import pulumi_aws as aws

def create_api_gateway(
    name: str,
    lambda_function: aws.lambda_.Function,
    stage_name: str = "dev"
):
    """
    Create API Gateway REST API integrated with Lambda using native AWS resources
    
    Args:
        name: API Gateway name
        lambda_function: Lambda function to integrate
        stage_name: Stage name for deployment
        
    Returns:
        Dictionary with API Gateway resources and URL
    """
    
    # Create REST API
    api = aws.apigateway.RestApi(
        f"{name}-api",
        name=name,
        description=f"API Gateway for {name}",
        endpoint_configuration={
            "types": "REGIONAL"
        }
    )
    
    # Get the root resource
    root_resource = api.root_resource_id
    
    # Create a proxy resource to catch all paths
    proxy_resource = aws.apigateway.Resource(
        f"{name}-proxy-resource",
        rest_api=api.id,
        parent_id=root_resource,
        path_part="{proxy+}"
    )
    
    # Create method for root path (GET /)
    root_method = aws.apigateway.Method(
        f"{name}-root-method",
        rest_api=api.id,
        resource_id=root_resource,
        http_method="ANY",
        authorization="NONE"
    )
    
    # Create method for proxy path (ANY /{proxy+})
    proxy_method = aws.apigateway.Method(
        f"{name}-proxy-method",
        rest_api=api.id,
        resource_id=proxy_resource.id,
        http_method="ANY",
        authorization="NONE"
    )
    
    # Create Lambda integration for root
    root_integration = aws.apigateway.Integration(
        f"{name}-root-integration",
        rest_api=api.id,
        resource_id=root_resource,
        http_method=root_method.http_method,
        integration_http_method="POST",
        type="AWS_PROXY",
        uri=lambda_function.invoke_arn
    )
    
    # Create Lambda integration for proxy
    proxy_integration = aws.apigateway.Integration(
        f"{name}-proxy-integration",
        rest_api=api.id,
        resource_id=proxy_resource.id,
        http_method=proxy_method.http_method,
        integration_http_method="POST",
        type="AWS_PROXY",
        uri=lambda_function.invoke_arn
    )
    
    # Create deployment (depends on methods and integrations)
    deployment = aws.apigateway.Deployment(
        f"{name}-deployment",
        rest_api=api.id,
        opts=pulumi.ResourceOptions(
            depends_on=[
                root_method,
                proxy_method,
                root_integration,
                proxy_integration
            ]
        ),
        # Use triggers to force redeployment when methods change
        triggers={
            "redeployment": pulumi.Output.all(
                root_method.id,
                proxy_method.id
            ).apply(lambda ids: str(hash(tuple(ids))))
        }
    )
    
    # Create stage
    stage = aws.apigateway.Stage(
        f"{name}-stage",
        rest_api=api.id,
        deployment=deployment.id,
        stage_name=stage_name,
        description=f"{stage_name} stage"
    )
    
    # Grant API Gateway permission to invoke Lambda for root
    root_lambda_permission = aws.lambda_.Permission(
        f"{name}-root-lambda-permission",
        action="lambda:InvokeFunction",
        function=lambda_function.name,
        principal="apigateway.amazonaws.com",
        source_arn=pulumi.Output.all(api.execution_arn, stage_name).apply(
            lambda args: f"{args[0]}/*/*/*"
        )
    )
    
    # Grant API Gateway permission to invoke Lambda for proxy
    proxy_lambda_permission = aws.lambda_.Permission(
        f"{name}-proxy-lambda-permission",
        action="lambda:InvokeFunction",
        function=lambda_function.name,
        principal="apigateway.amazonaws.com",
        source_arn=pulumi.Output.all(api.execution_arn, stage_name).apply(
            lambda args: f"{args[0]}/*/*/*"
        )
    )
    
    # Construct the API URL
    api_url = pulumi.Output.all(api.id, stage.stage_name).apply(
        lambda args: f"https://{args[0]}.execute-api.{aws.get_region().name}/{args[1]}"
    )
    
    # Return a custom object with the necessary attributes
    class APIGatewayResult:
        def __init__(self, rest_api, stage, url):
            self.rest_api = rest_api.id
            self.stage_name = stage.stage_name
            self.url = url
            self.stage = stage
            self._stage_obj = stage
            self._api_obj = rest_api
    
    return APIGatewayResult(api, stage, api_url)