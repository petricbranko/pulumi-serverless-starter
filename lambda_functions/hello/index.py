"""
Sample Lambda function handler
"""

import json
import os
import boto3
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name) if table_name else None

def handler(event, context):
    """
    Lambda function handler for API Gateway requests
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    
    # Log the event
    print(f"Received event: {json.dumps(event)}")
    
    # Extract request details
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    query_params = event.get('queryStringParameters') or {}
    
    # Handle different routes
    if path == '/' and http_method == 'GET':
        return handle_root(query_params)
    elif path.startswith('/items') and http_method == 'GET':
        return handle_get_items()
    elif path.startswith('/items') and http_method == 'POST':
        body = json.loads(event.get('body', '{}'))
        return handle_create_item(body)
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Not found'})
        }

def handle_root(query_params):
    """Handle root endpoint"""
    name = query_params.get('name', 'World')
    
    response = {
        'message': f'Hello, {name}!',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': os.environ.get('ENVIRONMENT', 'unknown')
    }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response)
    }

def handle_get_items():
    """Get all items from DynamoDB"""
    if not table:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Table not configured'})
        }
    
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'items': items})
        }
    except Exception as e:
        print(f"Error scanning table: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

def handle_create_item(body):
    """Create item in DynamoDB"""
    if not table:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Table not configured'})
        }
    
    try:
        item_id = body.get('id')
        if not item_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing required field: id'})
            }
        
        item = {
            'id': item_id,
            'data': body.get('data', {}),
            'created_at': datetime.utcnow().isoformat()
        }
        
        table.put_item(Item=item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'item': item})
        }
    except Exception as e:
        print(f"Error creating item: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }