import logging
from pulumi import automation as auto
# Ajusta la ruta de import según tu estructura real
from .resources.cluster import ContainerCluster, IAMUser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_pulumi_program(payload):
    """
    Función que devuelve otra función (un 'program') que Pulumi ejecuta para crear infraestructura.
    """
    def pulumi_program():
        logging.info("Iniciando la creación del programa Pulumi...")

        team_name = payload.get('TeamName', 'default-team')
        env = payload.get('env', 'default-env')
        stack_name = f"{team_name}-{env}-cluster"

        logging.info(f"Creando ECS Cluster y VPC para el stack: {stack_name}")
        # Crea VPC + ECS Cluster
        cluster = ContainerCluster(stack_name)

        # Si se solicitó crear un usuario IAM
        if payload.get("create_iam_user", False):
            logging.info(f"Creación de usuario IAM solicitada para el stack: {stack_name}")
            iam_user = IAMUser(f"{stack_name}-iam-user")

            # Ejemplo de uso de .apply() para loguear el nombre creado
            iam_user.user_name.apply(lambda name: logging.info(f"Usuario IAM creado: {name}"))

        logging.info("Infraestructura creada con éxito.")

    return pulumi_program

def deploy_infrastructure(payload):
    """
    Llama a Pulumi Automation API para hacer 'up' del stack según el payload.
    """
    logging.info("Preparando el despliegue de infraestructura...")

    project_name = "dynamic-pulumi-cluster"
    team_name = payload.get('TeamName', 'default-team')
    env = payload.get('env', 'default-env')
    aws_region = payload.get("awsRegion", "us-east-1")
    stack_name = f"{team_name}-{env}-cluster"

    # "Normalizar" el payload que pasaremos al pulumi_program
    payload = {
        **payload,
        "TeamName": team_name,
        "env": env,
        "awsRegion": aws_region
    }

    try:
        logging.info(f"Creando o seleccionando stack: {stack_name}")
        # Crea o selecciona el stack local
        stack = auto.create_or_select_stack(
            stack_name=stack_name,
            project_name=project_name,
            program=create_pulumi_program(payload)
        )

        # Configurar región AWS en la stack
        logging.info(f"Configurando región de AWS: {aws_region}")
        stack.set_config("aws:region", auto.ConfigValue(value=aws_region))

        # Hacer 'up'
        logging.info("Iniciando despliegue...")
        up_result = stack.up(on_output=print)  # Si quieres ver logs en la consola
        logging.info(f"Despliegue completado con éxito. Outputs: {up_result.outputs}")

    except Exception as e:
        logging.error(f"Error durante el despliegue: {e}")
        raise
