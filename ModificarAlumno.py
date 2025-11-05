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
        alumno_datos = event['body']['alumno_datos']
    except Exception:
        return {'statusCode': 400, 'response': {'message': 'Faltan tenant_id, alumno_id o alumno_datos'}}

    table = boto3.resource('dynamodb').Table('t_alumnos')
    try:
        resp = table.update_item(
            Key={'tenant_id': tenant_id, 'alumno_id': alumno_id},
            UpdateExpression="SET alumno_datos = :d",
            ExpressionAttributeValues={':d': alumno_datos},
            ConditionExpression="attribute_exists(tenant_id) AND attribute_exists(alumno_id)",
            ReturnValues="ALL_NEW"
        )
    except ClientError as e:
        code = e.response.get('Error', {}).get('Code', '')
        if code == 'ConditionalCheckFailedException':
            return {'statusCode': 404, 'response': {'message': 'Alumno no encontrado'}}
        return {'statusCode': 500, 'response': {'message': 'Error DynamoDB', 'error': str(e)}}

    return {'statusCode': 200, 'response': {'attributes': resp.get('Attributes', {})}}
