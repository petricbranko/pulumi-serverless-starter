"""Custom domain with Route53 and ACM certificate module"""

import pulumi
import pulumi_aws as aws

def setup_custom_domain(
    domain_name: str,
    subdomain: str,
    api_gateway_stage,
    certificate_region: str = "us-east-1"
) -> dict:
    """
    Setup custom domain with ACM certificate and Route53
    
    Args:
        domain_name: Base domain name (e.g., 'example.com')
        subdomain: Subdomain prefix (e.g., 'api')
        api_gateway_stage: API Gateway result object from create_api_gateway
        certificate_region: AWS region for certificate (us-east-1 for edge-optimized)
        
    Returns:
        Dictionary with domain_name, certificate_arn, and other resources
    """
    
    full_domain_name = f"{subdomain}.{domain_name}"
    
    # Get hosted zone
    zone = aws.route53.get_zone(name=domain_name)
    
    # Create ACM certificate
    # Note: For edge-optimized API Gateway, certificate must be in us-east-1
    provider_config = {"region": certificate_region} if certificate_region else None
    provider_opts = pulumi.ResourceOptions(provider=aws.Provider(
        f"provider-{certificate_region}",
        region=certificate_region
    )) if provider_config else None
    
    certificate = aws.acm.Certificate(
        "api-certificate",
        domain_name=full_domain_name,
        validation_method="DNS",
        tags={"Name": full_domain_name},
        opts=provider_opts
    )
    
    # Create DNS validation record
    validation_record = aws.route53.Record(
        "cert-validation",
        zone_id=zone.zone_id,
        name=certificate.domain_validation_options[0].resource_record_name,
        type=certificate.domain_validation_options[0].resource_record_type,
        records=[certificate.domain_validation_options[0].resource_record_value],
        ttl=60
    )
    
    # Certificate validation
    certificate_validation = aws.acm.CertificateValidation(
        "cert-validation",
        certificate_arn=certificate.arn,
        validation_record_fqdns=[validation_record.fqdn],
        opts=provider_opts
    )
    
    # Create custom domain name for API Gateway
    custom_domain = aws.apigateway.DomainName(
        "api-domain",
        domain_name=full_domain_name,
        certificate_arn=certificate_validation.certificate_arn,
        security_policy="TLS_1_2"
    )
    
    # Map custom domain to API Gateway stage
    base_path_mapping = aws.apigateway.BasePathMapping(
        "api-mapping",
        domain_name=custom_domain.domain_name,
        rest_api=api_gateway_stage._api_obj.id,
        stage_name=api_gateway_stage.stage_name
    )
    
    # Create Route53 A record pointing to API Gateway
    dns_record = aws.route53.Record(
        "api-dns",
        zone_id=zone.zone_id,
        name=full_domain_name,
        type="A",
        aliases=[{
            "name": custom_domain.cloudfront_domain_name,
            "zone_id": custom_domain.cloudfront_zone_id,
            "evaluate_target_health": False
        }]
    )
    
    return {
        "domain_name": full_domain_name,
        "certificate_arn": certificate.arn,
        "custom_domain": custom_domain,
        "dns_record": dns_record
    }