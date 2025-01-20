import pulumi
from pulumi import ComponentResource
from pulumi_aws import ec2, ecs, iam, secretsmanager

class ContainerCluster(ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__('custom:resource:ContainerCluster', name, {}, opts)
        
        self.vpc = ec2.Vpc(
            f"{name}-vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_support=True,
            enable_dns_hostnames=True
        )

        self.cluster = ecs.Cluster(f"{name}-cluster")

        self.register_outputs({
            "vpc_id": self.vpc.id,
            "cluster_arn": self.cluster.arn
        })


class IAMUser(ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__('custom:resource:IAMUser', name, {}, opts)
        
        user = iam.User(f"{name}-user", name=name)
        access_key = iam.AccessKey(f"{name}-access-key", user=user.name)

        secret = secretsmanager.Secret(
            f"{name}-secret",
            name=f"{name}-credentials",
            tags={
                "Name": f"{name}-credentials",
                "CreatedBy": "Pulumi"
            }
        )

        secretsmanager.SecretVersion(
            f"{name}-secret-version",
            secret_id=secret.id,
            secret_string=pulumi.Output.json_dumps({
                "AccessKeyId": access_key.id,
                "SecretAccessKey": access_key.secret
            })
        )

        self.user_name = user.name
        self.secret_arn = secret.arn

        self.register_outputs({
            "user_name": self.user_name,
            "secret_arn": self.secret_arn
        })
