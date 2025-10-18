"""Lambda function infrastructure module"""

import json
import pulumi
import pulumi_aws as aws

def create_lambda_function(
    name: str,
    handler: str,
    runtime: str,
    code_path: str,
    environment_variables: dict = None,
    table_arn: pulumi.Output = None,
    memory_size: int = 256,
    timeout: int = 30
) -> aws.lambda_.Function:
    """
    Create a Lambda function with appropriate IAM role and permissions
    
    Args:
        name: Name of the Lambda function
        handler: Handler path (e.g., 'index.handler')
        runtime: Runtime (e.g., 'python3.11')
        code_path: Path to Lambda code directory
        environment_variables: Environment variables dict
        table_arn: DynamoDB table ARN for permissions
        memory_size: Memory size in MB
        timeout: Timeout in seconds
        
    Returns:
        Lambda function resource
    """
    
    # Create IAM role for Lambda
    lambda_role = aws.iam.Role(
        f"{name}-role",
        assume_role_policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                }
            }]
        }),
        tags={"Name": f"{name}-role"}
    )
    
    # Attach basic Lambda execution policy
    aws.iam.RolePolicyAttachment(
        f"{name}-basic-execution",
        role=lambda_role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )
    
    # Create policy for DynamoDB access if table ARN provided
    if table_arn:
        dynamodb_policy = aws.iam.Policy(
            f"{name}-dynamodb-policy",
            policy=table_arn.apply(lambda arn: json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:Query",
                        "dynamodb:Scan"
                    ],
                    "Resource": arn
                }]
            }))
        )
        
        aws.iam.RolePolicyAttachment(
            f"{name}-dynamodb-attachment",
            role=lambda_role.name,
            policy_arn=dynamodb_policy.arn
        )
    
    # Create Lambda function
    lambda_function = aws.lambda_.Function(
        name,
        role=lambda_role.arn,
        runtime=runtime,
        handler=handler,
        code=pulumi.FileArchive(code_path),
        memory_size=memory_size,
        timeout=timeout,
        environment={
            "variables": environment_variables or {}
        },
        tags={"Name": name}
    )
    
    return lambda_function