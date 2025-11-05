import boto3
import json

def lambda_handler(event, context):
    if 'body' in event:
        body = json.loads(event['body'])
    else:
        body = event

    # Entrada (json)
    tenant_id = body['tenant_id']
    alumno_id = body['alumno_id']

    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'alumno_id': alumno_id
        }
    )

    # Salida (json)
    return {
        'statusCode': 200,
        'response': response
    }
