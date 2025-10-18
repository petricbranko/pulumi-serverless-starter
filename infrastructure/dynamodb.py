"""DynamoDB infrastructure module"""

import pulumi
import pulumi_aws as aws

def create_dynamodb_table(
    name: str,
    hash_key: str,
    attributes: list,
    billing_mode: str = "PAY_PER_REQUEST",
    range_key: str = None,
    global_secondary_indexes: list = None,
    tags: dict = None,
    point_in_time_recovery: bool = True,
    server_side_encryption: bool = True
) -> aws.dynamodb.Table:
    """
    Create a DynamoDB table with best practices
    
    Args:
        name: Table name
        hash_key: Hash key (partition key) attribute name
        attributes: List of attribute definitions [{"name": "id", "type": "S"}]
        billing_mode: PAY_PER_REQUEST or PROVISIONED
        range_key: Optional range key (sort key) attribute name
        global_secondary_indexes: Optional GSI definitions
        tags: Resource tags
        point_in_time_recovery: Enable PITR
        server_side_encryption: Enable SSE
        
    Returns:
        DynamoDB table resource
    """
    
    # Build attribute list - in current pulumi-aws, attributes are simple dicts
    attribute_list = [
        {
            "name": attr["name"],
            "type": attr["type"]
        } for attr in attributes
    ]
    
    # Build arguments for table creation
    table_args = {
        "name": name,
        "attributes": attribute_list,
        "hash_key": hash_key,
        "billing_mode": billing_mode,
        "point_in_time_recovery": {
            "enabled": point_in_time_recovery
        },
        "server_side_encryption": {
            "enabled": server_side_encryption
        },
        "tags": tags or {}
    }
    
    # Add range key if provided
    if range_key:
        table_args["range_key"] = range_key
    
    # Add GSIs if provided
    if global_secondary_indexes:
        gsi_list = []
        for gsi in global_secondary_indexes:
            gsi_config = {
                "name": gsi["name"],
                "hash_key": gsi["hash_key"],
                "projection_type": gsi.get("projection_type", "ALL")
            }
            
            # Add range key if provided
            if gsi.get("range_key"):
                gsi_config["range_key"] = gsi["range_key"]
            
            # Add capacity if using PROVISIONED billing
            if billing_mode == "PROVISIONED":
                if gsi.get("read_capacity"):
                    gsi_config["read_capacity"] = gsi["read_capacity"]
                if gsi.get("write_capacity"):
                    gsi_config["write_capacity"] = gsi["write_capacity"]
            
            gsi_list.append(gsi_config)
        
        table_args["global_secondary_indexes"] = gsi_list
    
    # Create table
    table = aws.dynamodb.Table(
        name,
        **table_args
    )
    
    return table