import time
import json
import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Importa la función que hace el despliegue
from .custom_pulumi_automation import deploy_infrastructure

class QueueConsumer:
    """
    Consumidor de mensajes desde AWS SQS.
    """
    def __init__(self, queue_url, wait_time=10):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url
        self.wait_time = wait_time

        logging.info(f"Inicializando QueueConsumer para la cola: {queue_url}")

    def start(self):
        logging.info("Iniciando el proceso de consumo de la cola SQS...")
        while True:
            try:
                # Intentamos recibir mensajes de la cola
                logging.info("Esperando mensajes...")
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=1,  # Procesa un mensaje a la vez
                    WaitTimeSeconds=self.wait_time
                )

                if 'Messages' in response:
                    for msg in response['Messages']:
                        try:
                            # Log del mensaje recibido
                            logging.info(f"Mensaje recibido: {msg['Body']}")

                            # Parseamos el mensaje como JSON
                            body = json.loads(msg['Body'])
                            logging.info(f"Procesando payload: {body}")

                            # Despliegue con Pulumi
                            deploy_infrastructure(body)

                            # Eliminamos el mensaje de la cola
                            logging.info("Eliminando el mensaje de la cola...")
                            self.sqs.delete_message(
                                QueueUrl=self.queue_url,
                                ReceiptHandle=msg['ReceiptHandle']
                            )
                            logging.info("Mensaje procesado y eliminado con éxito.")
                        except json.JSONDecodeError as e:
                            logging.error(f"Error al decodificar el mensaje JSON: {e}")
                        except Exception as e:
                            logging.error(f"Error procesando el mensaje: {e}")
                else:
                    logging.info("No hay mensajes en la cola. Esperando más...")
            except (BotoCoreError, ClientError) as e:
                logging.error(f"Error al conectar con SQS: {e}")
            except Exception as e:
                logging.error(f"Error inesperado: {e}")

            time.sleep(5)
