# Pulumi Serverless Starter Template

A production-ready serverless starter template using Pulumi and AWS. Deploys Lambda functions, DynamoDB tables, and API Gateway with optional custom domain support.

## Features

- **Auto-Discovery**: Automatically discovers and deploys all Lambda functions from the `lambda_functions` directory
- **Multiple API Gateways**: Support for mapping different Lambda functions to separate API Gateways
- **AWS Lambda**: Python-based serverless functions with IAM roles and permissions
- **DynamoDB** (Optional): NoSQL database with point-in-time recovery and encryption
- **API Gateway**: REST API with Lambda integration
- **Custom Domain** (Optional): Route53 and ACM certificate setup
- **Infrastructure as Code**: Clean, modular Pulumi code in Python
- **Fully Configurable**: All settings via YAML configuration - no code changes needed
- **Best Practices**: Security, monitoring, and deployment configurations

## Prerequisites

- Python 3.8+
- Pulumi CLI installed
- AWS CLI configured with appropriate credentials
- AWS account with permissions for Lambda, DynamoDB, API Gateway, Route53, and ACM

## Project Structure

```
pulumi-serverless-starter/
├── __main__.py                 # Main Pulumi program
├── Pulumi.yaml                 # Project configuration
├── Pulumi.dev.yaml            # Stack-specific config
├── requirements.txt            # Python dependencies
├── lambda_functions/
│   └── hello/
│       └── index.py           # Lambda function code
├── infrastructure/
│   ├── __init__.py
│   ├── lambda_function.py     # Lambda infrastructure
│   ├── dynamodb.py            # DynamoDB table
│   ├── api_gateway.py         # API Gateway
│   └── domain.py              # Custom domain setup
└── README.md
```

## Quick Start

### 1. Install Pulumi

```bash
curl -fsSL https://get.pulumi.com | sh
```

### 2. Clone or Create Project

```bash
mkdir pulumi-serverless-starter
cd pulumi-serverless-starter
```

### 3. Initialize Pulumi Project

```bash
# Create new Pulumi project
pulumi new aws-python --name serverless-starter

# Or if you already have the code, just install dependencies
pip install -r requirements.txt
```

### 4. Add Lambda Functions

Create your Lambda functions in the `lambda_functions` directory:

```bash
# The starter already includes a hello function
# Add more functions by creating new directories
mkdir -p lambda_functions/myfunction
```

Each directory will be auto-discovered and deployed as a Lambda function.

### 5. Configure Your Stack

All configuration can be set via the command line or by editing `Pulumi.dev.yaml` directly.

**Minimal configuration (uses all defaults):**

```bash
# Set your AWS region
pulumi config set aws:region us-east-1
```

**Custom configuration:**

```bash
# Set your AWS region
pulumi config set aws:region us-east-1

# Configure project name
pulumi config set projectName my-serverless-app

# Disable DynamoDB if not needed
pulumi config set enableDynamoDB false

# Map functions to different API Gateways
pulumi config set apiGatewayMappings "public-api:hello,world;admin-api:user"

# Enable custom domain (optional)
# pulumi config set enableCustomDomain true
# pulumi config set domainName yourdomain.com
# pulumi config set subdomain api
```

**Or edit `Pulumi.dev.yaml` directly** - see the Configuration Options section below for all available parameters.

### 6. Deploy

```bash
# Preview changes
pulumi preview

# Deploy the stack
pulumi up

# Select 'yes' to confirm deployment
```

### 7. Test Your APIs

After deployment, Pulumi will output your API URLs:

```bash
# View all API Gateway URLs
pulumi stack output apiGateways

# Test an API endpoint
# Get the URL from the output above, e.g.:
curl https://abc123.execute-api.us-east-1.amazonaws.com/dev

# Test with a specific function path
curl https://abc123.execute-api.us-east-1.amazonaws.com/dev/hello

# View all deployed Lambda functions
pulumi stack output lambdaFunctions
```

## Configuration Options

All configuration is defined in `Pulumi.yaml` with type-safe schema and defaults. Edit `Pulumi.<stack>.yaml` to customize your deployment:

### Available Configuration Parameters

#### AWS Configuration
- `aws:region` - AWS region for deployment (default: us-east-1)

#### Project Configuration
- `projectName` - Prefix for all resource names (default: serverless-app)

#### DynamoDB Configuration (Optional)
- `enableDynamoDB` - Enable DynamoDB table creation (default: true)
- `dynamodbTableName` - DynamoDB table name (default: app-table)
- `dynamodbHashKey` - Hash key/partition key (default: id)
- `dynamodbBillingMode` - Billing mode: PAY_PER_REQUEST or PROVISIONED (default: PAY_PER_REQUEST)
- `dynamodbEnablePITR` - Enable point-in-time recovery (default: true)
- `dynamodbEnableEncryption` - Enable server-side encryption (default: true)

#### Lambda Configuration (Auto-Discovery)
- `lambdaAutoDiscover` - Auto-discover Lambda functions from directory (default: true)
- `lambdaFunctionsDirectory` - Directory containing Lambda functions (default: ./lambda_functions)
- `lambdaDefaultRuntime` - Default Lambda runtime (default: python3.11)
- `lambdaDefaultHandler` - Default handler path (default: index.handler)
- `lambdaDefaultMemorySize` - Default memory size in MB (default: 256)
- `lambdaDefaultTimeout` - Default timeout in seconds (default: 30)

#### API Gateway Configuration
- `apiGatewayDefaultName` - Default API Gateway name (default: serverless-api)
- `apiGatewayMappings` - Map functions to different API Gateways (default: "")

#### Custom Domain Configuration (Optional)
- `enableCustomDomain` - Enable custom domain (default: false)
- `domainName` - Base domain name (e.g., example.com)
- `subdomain` - Subdomain prefix (default: api)

### Example Configurations

#### Basic Configuration (Single API Gateway, Auto-Discovery)

```yaml
config:
  aws:region: us-east-1
  serverless-starter:projectName: my-app
  serverless-starter:enableDynamoDB: true
  serverless-starter:lambda:autoDiscover: true
  serverless-starter:apiGateway:defaultName: my-api
```

#### Multiple API Gateways with Mappings

```yaml
config:
  aws:region: us-east-1
  serverless-starter:projectName: my-app

  # Map different functions to different API Gateways
  serverless-starter:apiGatewayMappings: "app1-api:hello,world;app2-api:user,auth"
```

#### Without DynamoDB

```yaml
config:
  aws:region: us-east-1
  serverless-starter:projectName: my-app
  serverless-starter:enableDynamoDB: false
```

#### Advanced Configuration

```yaml
config:
  # AWS Configuration
  aws:region: us-east-1

  # Project Configuration
  serverless-starter:projectName: my-app

  # DynamoDB Configuration
  serverless-starter:enableDynamoDB: true
  serverless-starter:dynamodbTableName: users-table
  serverless-starter:dynamodbHashKey: userId
  serverless-starter:dynamodbBillingMode: PAY_PER_REQUEST

  # Lambda Configuration (Auto-Discovery)
  serverless-starter:lambdaAutoDiscover: true
  serverless-starter:lambdaFunctionsDirectory: ./lambda_functions
  serverless-starter:lambdaDefaultRuntime: python3.11
  serverless-starter:lambdaDefaultMemorySize: 512
  serverless-starter:lambdaDefaultTimeout: 60

  # API Gateway Configuration
  serverless-starter:apiGatewayDefaultName: my-api
  serverless-starter:apiGatewayMappings: "public-api:hello;internal-api:admin,user"

  # Custom Domain (Optional)
  serverless-starter:enableCustomDomain: true
  serverless-starter:domainName: example.com
  serverless-starter:subdomain: api
```

## Lambda Auto-Discovery

The starter template automatically discovers and deploys all Lambda functions in the `lambda_functions` directory.

### Directory Structure

```
lambda_functions/
├── hello/
│   └── index.py
├── world/
│   └── index.py
└── user/
    └── index.py
```

Each subdirectory becomes a Lambda function with the directory name as the function name.

### Per-Function Configuration

Create a `function.json` file in any Lambda directory to override defaults:

```json
{
  "runtime": "python3.12",
  "handler": "app.handler",
  "memorySize": 512,
  "timeout": 60,
  "environmentVariables": {
    "CUSTOM_VAR": "value"
  }
}
```

### Disabling Auto-Discovery

To disable auto-discovery and manually configure Lambda functions:

```yaml
serverless-starter:lambdaAutoDiscover: false
```

## Multiple API Gateway Mappings

Map different Lambda functions to separate API Gateways using the `apiGatewayMappings` configuration.

### Mapping Format

```
"api-name1:function1,function2;api-name2:function3,function4"
```

### Examples

#### Single API Gateway (Default)

Leave mappings empty to deploy all functions to one API Gateway:

```yaml
serverless-starter:apiGatewayMappings: ""
```

#### Two Separate API Gateways

```yaml
serverless-starter:apiGatewayMappings: "public-api:hello,world;admin-api:user,auth"
```

This creates:
- `public-api` with functions: `hello`, `world`
- `admin-api` with functions: `user`, `auth`

#### Three API Gateways

```yaml
serverless-starter:apiGatewayMappings: "app1:func1,func2;app2:func3;app3:func4,func5,func6"
```

### Accessing API URLs

After deployment, view all API Gateway URLs:

```bash
pulumi stack output apiGateways
```

Output:
```json
{
  "public-api": {
    "url": "https://abc123.execute-api.us-east-1.amazonaws.com/dev",
    "functions": ["hello", "world"]
  },
  "admin-api": {
    "url": "https://def456.execute-api.us-east-1.amazonaws.com/dev",
    "functions": ["user", "auth"]
  }
}
```

## Disabling DynamoDB

To deploy without DynamoDB:

```bash
pulumi config set enableDynamoDB false
```

Or in `Pulumi.<stack>.yaml`:

```yaml
serverless-starter:enableDynamoDB: false
```

## Custom Domain Setup

To enable custom domain:

1. Ensure you have a hosted zone in Route53 for your domain
2. Enable custom domain in config:

```bash
pulumi config set enableCustomDomain true
pulumi config set domainName yourdomain.com
pulumi config set subdomain api
```

3. Deploy:

```bash
pulumi up
```

The certificate will be automatically created and validated via DNS. Your API will be available at `https://api.yourdomain.com`

## Managing Multiple Environments

Create different stacks for different environments with different configurations:

```bash
# Create production stack
pulumi stack init prod
pulumi config set aws:region us-east-1
pulumi config set projectName production-app
pulumi config set lambda:memorySize 1024
pulumi config set dynamodb:billingMode PROVISIONED

# Create staging stack
pulumi stack init staging
pulumi config set aws:region us-west-2
pulumi config set projectName staging-app
pulumi config set lambda:memorySize 512

# Create development stack (uses defaults from Pulumi.yaml)
pulumi stack init dev
pulumi config set aws:region us-east-1
pulumi config set projectName dev-app

# Switch between stacks
pulumi stack select dev
pulumi stack select staging
pulumi stack select prod
```

Each stack will have its own `Pulumi.<stack>.yaml` configuration file, allowing you to maintain different settings per environment.

## Updating Lambda Function

1. Modify code in `lambda_functions/hello/index.py`
2. Deploy changes:

```bash
pulumi up
```

Pulumi automatically detects changes and updates only affected resources.

## Outputs

After deployment, the following outputs are available:

```bash
# View all outputs
pulumi stack output

# View specific outputs
pulumi stack output apiGateways         # All API Gateway URLs and mappings
pulumi stack output lambdaFunctions     # All Lambda function names and ARNs
pulumi stack output dynamoDbTableName   # DynamoDB table name (if enabled)
pulumi stack output dynamoDbTableArn    # DynamoDB table ARN (if enabled)
pulumi stack output summary             # Deployment summary
```

### Example Output

```json
{
  "apiGateways": {
    "public-api": {
      "functions": ["hello", "world"],
      "url": "https://abc123.execute-api.us-east-1.amazonaws.com/dev"
    },
    "admin-api": {
      "functions": ["user"],
      "url": "https://def456.execute-api.us-east-1.amazonaws.com/dev"
    }
  },
  "lambdaFunctions": {
    "hello": {
      "arn": "arn:aws:lambda:us-east-1:123456789:function:hello",
      "name": "hello"
    },
    "world": {
      "arn": "arn:aws:lambda:us-east-1:123456789:function:world",
      "name": "world"
    }
  },
  "summary": {
    "apiGatewaysCount": 2,
    "dynamoDbEnabled": true,
    "environment": "dev",
    "lambdaFunctionsCount": 3,
    "projectName": "my-app"
  }
}
```

## Cleanup

To destroy all resources:

```bash
pulumi destroy

# Confirm with 'yes'
```

## Common Commands

```bash
# View current stack
pulumi stack

# View stack outputs
pulumi stack output

# View stack history
pulumi stack history

# Export stack state
pulumi stack export --file stack.json

# View logs
pulumi logs --follow

# Refresh state
pulumi refresh
```

## Customization

### Changing Resource Configuration

All resources can be customized via configuration in `Pulumi.<stack>.yaml` without modifying code:

```yaml
# Example: Use a different runtime and increase Lambda resources
serverless-starter:lambda:runtime: python3.12
serverless-starter:lambda:memorySize: 1024
serverless-starter:lambda:timeout: 120

# Example: Change DynamoDB billing to provisioned
serverless-starter:dynamodb:billingMode: PROVISIONED
```

### Modifying DynamoDB Schema

To use a different hash key, update your configuration:

```bash
pulumi config set dynamodb:hashKey userId
```

For more complex schemas (range keys, GSIs), edit `__main__.py`:

```python
table = create_dynamodb_table(
    name=dynamodb_table_name,
    hash_key=dynamodb_hash_key,
    range_key="timestamp",  # Optional sort key
    attributes=[
        {"name": dynamodb_hash_key, "type": "S"},
        {"name": "timestamp", "type": "N"}
    ],
    billing_mode=dynamodb_billing_mode
)
```

### Adding Global Secondary Index

Edit the table creation in `__main__.py`:

```python
table = create_dynamodb_table(
    name=dynamodb_table_name,
    hash_key=dynamodb_hash_key,
    attributes=[
        {"name": dynamodb_hash_key, "type": "S"},
        {"name": "email", "type": "S"}
    ],
    global_secondary_indexes=[{
        "name": "EmailIndex",
        "hash_key": "email",
        "projection_type": "ALL"
    }],
    billing_mode=dynamodb_billing_mode
)
```

### Using Different Lambda Functions

To deploy a different Lambda function, update the configuration:

```bash
pulumi config set lambda:codePath ./lambda_functions/my-custom-function
pulumi config set lambda:handler app.handler
pulumi config set lambda:runtime nodejs20.x
```

## Security Best Practices

- Lambda functions have least-privilege IAM roles
- DynamoDB encryption at rest enabled
- Point-in-time recovery enabled for DynamoDB
- TLS 1.2 minimum for API Gateway custom domains
- Environment variables for configuration

## Troubleshooting

### Certificate Validation Taking Long

ACM certificate validation via DNS can take 5-30 minutes. Check Route53 for the validation CNAME record.

### Lambda Function Not Updating

Try forcing a refresh:

```bash
pulumi refresh
pulumi up --replace 'urn:pulumi:stack::project::aws:lambda/function:Function::hello-world'
```

### Permission Errors

Ensure your AWS credentials have sufficient permissions for all services used.

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.