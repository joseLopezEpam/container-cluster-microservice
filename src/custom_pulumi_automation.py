import logging
from pulumi import automation as auto
from resources.cluster import ContainerCluster, IAMUser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_pulumi_program(payload):
    """
    Creates a Pulumi program based on the given payload.
    """
    def pulumi_program():
        logging.info("Iniciando la creación del programa Pulumi...")

        # Safeguard payload access with defaults
        team_name = payload.get('TeamName', 'default-team')
        env = payload.get('env', 'default-env')
        stack_name = f"{team_name}-{env}-cluster"
        logging.info(f"Creando ECS Cluster y VPC para el stack: {stack_name}")

        # Create ECS Cluster and VPC
        cluster = ContainerCluster(stack_name)

        # Optionally create an IAM User
        if payload.get("create_iam_user", False):
            logging.info(f"Creación de usuario IAM solicitada para el stack: {stack_name}")
            iam_user = IAMUser(f"{stack_name}-iam-user")
            iam_user.user_name.apply(lambda name: logging.info(f"Usuario IAM creado: {name}"))

        logging.info("Infraestructura creada con éxito.")

    return pulumi_program

def deploy_infrastructure(payload):
    """
    Deploys the infrastructure using Pulumi Automation API.
    """
    logging.info("Preparando el despliegue de infraestructura...")

    # Set default values for missing keys
    project_name = "dynamic-pulumi-cluster"
    team_name = payload.get('TeamName', 'default-team')
    env = payload.get('env', 'default-env')
    aws_region = payload.get("awsRegion", "us-east-1")
    stack_name = f"{team_name}-{env}-cluster"

    # Add defaults to the payload for Pulumi program
    payload = {
        **payload,
        "TeamName": team_name,
        "env": env,
        "awsRegion": aws_region
    }

    try:
        logging.info(f"Creando o seleccionando stack: {stack_name}")

        # Create or select the Pulumi stack
        stack = auto.create_or_select_stack(
            stack_name=stack_name,
            project_name=project_name,
            program=create_pulumi_program(payload)  # Pass the updated payload
        )

        # Configure the AWS region
        logging.info(f"Configurando región de AWS: {aws_region}")
        stack.set_config("aws:region", auto.ConfigValue(value=aws_region))

        # Execute the deployment
        logging.info("Iniciando despliegue...")
        up_result = stack.up()
        logging.info(f"Despliegue completado con éxito. Outputs: {up_result.outputs}")

    except Exception as e:
        logging.error(f"Error durante el despliegue: {e}")
        raise  # Re-raise the exception to provide feedback on failure

if __name__ == "__main__":
    # Example payload
    payload = {
        "ProjectName": "test-project2",
        "TeamName": "prueba",
        "env": "dev",
        "awsRegion": "us-east-1",
        "Services": ["container_cluster"],
        "create_iam_user": True
    }

    # Deploy infrastructure using the example payload
    deploy_infrastructure(payload)
