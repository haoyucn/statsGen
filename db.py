import boto3
import time

dynamodb = boto3.resource('dynamodb')

t1 = time.time()

table = dynamodb.Table('User')

with table.batch_writer() as batch:
	batch.put_item(
		Item={
			'id': 1,
			'name': 'Hao1'
		}
	)
	batch.put_item(
		Item={
			'id': 2,
			'name': 'Hao2'
		}
	)
	batch.put_item(
		Item={
			'id': 3,
			'name': 'Hao1'
		}
	)

print(table.creation_date_time)
print(time.time() - t1)
