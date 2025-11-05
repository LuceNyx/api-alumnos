import json
import boto3
from botocore.exceptions import ClientError

def _parse_event(event):
    """Soporta llamadas directas y vía API Gateway (lambda-proxy)."""
    if isinstance(event, dict) and 'body' in event:
        body = event['body']
        if event.get('isBase64Encoded'):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        return json.loads(body) if isinstance(body, str) else body
    return event if isinstance(event, dict) else {}

def lambda_handler(event, context):
    body = _parse_event(event)

    tenant_id = body.get('tenant_id')
    alumno_id = body.get('alumno_id')

    if not tenant_id or not alumno_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Faltan parámetros requeridos: tenant_id y alumno_id'
            })
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')

    try:
        # Condición: solo elimina si existe el alumno
        resp = table.delete_item(
            Key={
                'tenant_id': tenant_id,
                'alumno_id': alumno_id
            },
            ConditionExpression="attribute_exists(tenant_id) AND attribute_exists(alumno_id)",
            ReturnValues="ALL_OLD"
        )

        if 'Attributes' not in resp:
            # Si no hay atributos, no se encontró el alumno
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Alumno no encontrado',
                    'tenant_id': tenant_id,
                    'alumno_id': alumno_id
                })
            }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Alumno eliminado correctamente',
                'deleted_item': resp['Attributes']
            })
        }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'message': 'Alumno no encontrado para eliminar',
                    'tenant_id': tenant_id,
                    'alumno_id': alumno_id
                })
            }

        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Error al eliminar el alumno',
                'error': str(e)
            })
        }
