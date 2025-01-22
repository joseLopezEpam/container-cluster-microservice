import os
import logging
# Importamos de este mismo paquete la clase QueueConsumer
from .queue_consumer import QueueConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    logging.info("Iniciando MessageToInfra...")

    # Recuperar URL de la cola SQS desde variable de entorno y eliminar espacios o saltos de línea
    sqs_queue_url = os.getenv("SQS_QUEUE_URL", "").strip()
    if not sqs_queue_url:
        logging.error("La variable de entorno SQS_QUEUE_URL no está definida o está vacía.")
        raise ValueError("Debe definir la variable SQS_QUEUE_URL antes de ejecutar la aplicación.")

    if not sqs_queue_url.startswith("https://sqs."):
        logging.error(f"El valor de SQS_QUEUE_URL no es válido: {sqs_queue_url}")
        raise ValueError(f"SQS_QUEUE_URL no tiene un formato válido: {sqs_queue_url}")

    logging.info(f"Usando SQS Queue URL: {sqs_queue_url}")

    try:
        # Inicializamos el consumidor
        consumer = QueueConsumer(queue_url=sqs_queue_url)

        # Iniciamos el consumo de mensajes
        consumer.start()
    except Exception as e:
        logging.error(f"Ocurrió un error al iniciar el consumidor: {e}")
        raise

if __name__ == "__main__":
    main()
