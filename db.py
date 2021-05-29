import boto3
import time
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

t1 = time.time()

table = dynamodb.Table('User')

with table.batch_writer() as batch:
	batch.put_item(
		Item={
			'id': '1',
			'name': 'Hao1'
		}
	)
	batch.put_item(
		Item={
			'id': '2',
			'name': 'Hao2'
		}
	)
	batch.put_item(
		Item={
			'id': '3',
			'name': 'Hao1'
		}
	)

response = table.query(
    KeyConditionExpression=Attr('name').exits()
)
items = response['Items']
print(items)

print(table.creation_date_time)
print(time.time() - t1)
