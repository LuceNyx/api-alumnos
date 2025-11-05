import json
import boto3
from botocore.exceptions import ClientError

def _ensure_body_is_dict(event):
    if 'body' in event and isinstance(event['body'], str):
        try:
            event['body'] = json.loads(event['body'])
        except Exception:
            event['body'] = {}
    return event

def lambda_handler(event, context):
    event = _ensure_body_is_dict(event)

    try:
        tenant_id = event['body']['tenant_id']
        alumno_id = event['body']['alumno_id']
    except Exception:
        return {'statusCode': 400, 'response': {'message': 'Faltan tenant_id o alumno_id'}}

    table = boto3.resource('dynamodb').Table('t_alumnos')
    try:
        resp = table.get_item(Key={'tenant_id': tenant_id, 'alumno_id': alumno_id})
    except ClientError as e:
        return {'statusCode': 500, 'response': {'message': 'Error DynamoDB', 'error': str(e)}}

    if 'Item' not in resp:
        return {'statusCode': 404, 'response': {'message': 'Alumno no encontrado'}}

    return {'statusCode': 200, 'response': {'item': resp['Item']}}
