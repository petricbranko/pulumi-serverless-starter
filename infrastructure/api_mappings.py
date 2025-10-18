"""API Gateway mapping configuration module"""

import pulumi
from typing import Dict, List
from infrastructure.api_gateway import create_api_gateway


def parse_api_mappings(mappings_config: str) -> Dict[str, List[str]]:
    """
    Parse API Gateway mappings from configuration string.

    Format: "api-name:func1,func2,func3;another-api:func4,func5"

    Args:
        mappings_config: Mapping configuration string

    Returns:
        Dictionary mapping API Gateway names to lists of function names
    """
    if not mappings_config:
        return {}

    mappings = {}
    api_groups = mappings_config.split(';')

    for group in api_groups:
        group = group.strip()
        if not group or ':' not in group:
            continue

        api_name, functions = group.split(':', 1)
        api_name = api_name.strip()
        function_list = [f.strip() for f in functions.split(',') if f.strip()]

        if api_name and function_list:
            mappings[api_name] = function_list

    return mappings


def create_api_gateways_with_mappings(
    lambda_functions: Dict,
    mappings_config: str,
    default_api_name: str,
    stage_name: str
) -> Dict:
    """
    Create API Gateways based on mappings configuration.

    Args:
        lambda_functions: Dictionary of Lambda function resources
        mappings_config: Mapping configuration string
        default_api_name: Default API Gateway name if no mappings specified
        stage_name: Stage name for deployment

    Returns:
        Dictionary with API Gateway configurations
    """
    # Parse mappings
    mappings = parse_api_mappings(mappings_config)

    # If no mappings, create single API Gateway for all functions
    if not mappings:
        if not lambda_functions:
            pulumi.log.warn("No Lambda functions available to map to API Gateway")
            return {}

        # Use the first Lambda function for the default single-function setup
        first_function = list(lambda_functions.values())[0]

        api = create_api_gateway(
            name=default_api_name,
            lambda_function=first_function,
            stage_name=stage_name
        )

        return {
            "default": {
                "api": api,
                "functions": list(lambda_functions.keys()),
                "url": api.url
            }
        }

    # Create API Gateway for each mapping
    apis = {}

    for api_name, function_names in mappings.items():
        # Validate that all mapped functions exist
        missing_functions = [fn for fn in function_names if fn not in lambda_functions]
        if missing_functions:
            pulumi.log.warn(
                f"API Gateway '{api_name}': Functions not found: {', '.join(missing_functions)}"
            )
            continue

        # Use the first function as the primary integration
        # (In a real-world scenario, you might want to create separate routes for each)
        primary_function_name = function_names[0]
        primary_function = lambda_functions[primary_function_name]

        api = create_api_gateway(
            name=api_name,
            lambda_function=primary_function,
            stage_name=stage_name
        )

        apis[api_name] = {
            "api": api,
            "functions": function_names,
            "url": api.url,
            "primary_function": primary_function_name
        }

        pulumi.log.info(
            f"Created API Gateway '{api_name}' with functions: {', '.join(function_names)}"
        )

    # Check for unmapped functions
    all_mapped_functions = set()
    for function_names in mappings.values():
        all_mapped_functions.update(function_names)

    unmapped_functions = set(lambda_functions.keys()) - all_mapped_functions
    if unmapped_functions:
        pulumi.log.warn(
            f"Functions not mapped to any API Gateway: {', '.join(unmapped_functions)}"
        )

    return apis
