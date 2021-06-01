import boto3
import time
import json

from http.server import HTTPServer, BaseHTTPRequestHandler
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

t1 = time.time()

table = dynamodb.Table('User')


def writeItems(size):
	with table.batch_writer() as batch:
		for i in range(size):
			batch.put_item(
				Item={
					'id': str(i),
					'name': 'Hao1'
				}
			)
	return True

def readItems(size):
	response = table.scan(
		FilterExpression=Attr('name').exists(),
		Limit =size
	)
	items = response['Items']
	return json.dumps(items)



# aws dynamodb --endpoint-url http://localhost:8000 create-table \
# 	--table-name user \
# 	--attribute-definitions AttributeName=id,AttributeType=N \
# 	--key-schema AttributeName=id,KeyType=HASH \
# 	--provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5


# aws dynamodb --endpoint-url http://localhost:8000 create-table \
# 	--table-name user \
# 	--attribute-definitions AttributeName=id,AttributeType=N \
# 	--key-schema AttributeName=id,KeyType=HASH \
# 	--provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		amount = int(self.path[1:])
		resp = None
		status = 200
		try:
			resp = readItems(amount)
		except:
			status = 500
			resp = None;
		self.send_response(status)
		self.end_headers()
		if resp != None:
			self.wfile.write(bytes(resp, 'utf-8'))
		else:
			self.wfile.write(bytes("true", 'utf-8'))

	def do_POST(self):
		amount = int(self.path[1:])
		resp = None
		status = 200
		try:
			resp = writeItems(amount)
		except:
			status = 500
			resp = None;
		self.send_response(status)
		self.end_headers()
		print("-----------------------------")
		print(resp)
		print("-----------------------------")
		if resp != None:
			self.wfile.write(bytes(resp, 'utf-8'))
		else:
			self.wfile.write(bytes("true", 'utf-8'))


writeItems(200)
httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()