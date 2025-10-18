"""Lambda function auto-discovery and configuration module"""

import os
import json
import pulumi
from typing import Dict, List, Optional
from infrastructure.lambda_function import create_lambda_function


def discover_lambda_functions(functions_directory: str) -> List[str]:
    """
    Discover Lambda functions by scanning the functions directory.

    Args:
        functions_directory: Path to directory containing Lambda function subdirectories

    Returns:
        List of function names (subdirectory names)
    """
    if not os.path.exists(functions_directory):
        pulumi.log.warn(f"Lambda functions directory not found: {functions_directory}")
        return []

    function_names = []
    for item in os.listdir(functions_directory):
        item_path = os.path.join(functions_directory, item)
        # Check if it's a directory and not a hidden or special directory
        if os.path.isdir(item_path) and not item.startswith('.') and not item.startswith('__'):
            function_names.append(item)

    return sorted(function_names)


def load_function_config(function_name: str, functions_directory: str) -> Optional[Dict]:
    """
    Load function-specific configuration from function.json if it exists.

    Args:
        function_name: Name of the function
        functions_directory: Path to functions directory

    Returns:
        Dictionary with function config or None
    """
    config_path = os.path.join(functions_directory, function_name, "function.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            pulumi.log.warn(f"Failed to load config for {function_name}: {e}")
    return None


def create_lambda_functions(
    functions_directory: str,
    default_runtime: str,
    default_handler: str,
    default_memory_size: int,
    default_timeout: int,
    table_arn: Optional[pulumi.Output] = None,
    table_name: Optional[pulumi.Output] = None,
    stack_name: str = "dev"
) -> Dict:
    """
    Create Lambda functions from discovered directories.

    Args:
        functions_directory: Path to Lambda functions directory
        default_runtime: Default runtime
        default_handler: Default handler
        default_memory_size: Default memory size
        default_timeout: Default timeout
        table_arn: Optional DynamoDB table ARN for permissions
        table_name: Optional DynamoDB table name for environment variable
        stack_name: Stack name for environment variable

    Returns:
        Dictionary mapping function names to Lambda function resources
    """
    discovered_functions = discover_lambda_functions(functions_directory)

    if not discovered_functions:
        pulumi.log.warn(f"No Lambda functions discovered in {functions_directory}")
        return {}

    pulumi.log.info(f"Discovered Lambda functions: {', '.join(discovered_functions)}")

    lambda_functions = {}

    for func_name in discovered_functions:
        # Load function-specific config
        func_config = load_function_config(func_name, functions_directory) or {}

        # Determine function settings (function.json overrides defaults)
        runtime = func_config.get("runtime", default_runtime)
        handler = func_config.get("handler", default_handler)
        memory_size = func_config.get("memorySize", default_memory_size)
        timeout = func_config.get("timeout", default_timeout)

        # Build environment variables
        env_vars = func_config.get("environment", {})
        if table_name:
            env_vars["TABLE_NAME"] = table_name
        env_vars["ENVIRONMENT"] = stack_name

        # Add custom environment variables from config
        custom_env = func_config.get("environmentVariables", {})
        env_vars.update(custom_env)

        # Create Lambda function
        code_path = os.path.join(functions_directory, func_name)

        lambda_function = create_lambda_function(
            name=func_name,
            handler=handler,
            runtime=runtime,
            code_path=code_path,
            memory_size=memory_size,
            timeout=timeout,
            environment_variables=env_vars,
            table_arn=table_arn
        )

        lambda_functions[func_name] = lambda_function
        pulumi.log.info(f"Created Lambda function: {func_name}")

    return lambda_functions
