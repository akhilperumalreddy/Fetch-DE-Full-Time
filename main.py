import json
import boto3
import psycopg2
import hashlib
import datetime

# read JSON data containing user login behavior from an AWS SQS Queue
def read_from_aws_sqs(queue_url):
    sqs_client = boto3.client('sqs', region_name='localhost', endpoint_url='http://localhost:4566',
                             aws_access_key_id='', aws_secret_access_key='')
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=100
    )
    messages = response.get('Messages', [])
    return messages

# delete processed messages from SQS queue
def delete_messages_from_sqs(queue_url, messages):
    sqs_client = boto3.client('sqs', region_name='localhost', endpoint_url='http://localhost:4566',
                             aws_access_key_id='', aws_secret_access_key='')
    for msg in messages:
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg['ReceiptHandle']
        )


# convert app version to int by preserving the dot information
def version_string_to_int(version_str):
    # Split the version string by dot ('.') separator
    parts = version_str.split('.')

    # Convert each part to an integer and represent the version in base 100
    # We use base 100 as the max value a part can take is 99 (verified from the whole data)
    version_int = 0
    for i, part in enumerate(parts):
        version_int += int(part) * (100 ** (len(parts) - i - 1))

    return version_int


# the fields `device_id` and `ip` should be masked
def pii_masking(data):
    for record in data:
            # Mask both device_id and ip using SHA-256 hash
            record['masked_device_id'] = hashlib.sha256(record['device_id'].encode()).hexdigest()
            record['masked_ip'] = hashlib.sha256(record['ip'].encode()).hexdigest()

            # Remove the original device_id and ip fields from the record
            record.pop('device_id')
            record.pop('ip')
    return data
    

# Step 3: Write to Postgres database
def write_to_postgres(data, db_credentials):
    conn = psycopg2.connect(**db_credentials)
    cursor = conn.cursor()
    for record in data:
        cursor.execute("""
            INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (
            record.get('user_id', 'default_user_id'),
            record.get('device_type', 'default_device_type'),
            record['masked_ip'],
            record['masked_device_id'],
            record.get('locale', 'default_locale'),
            record['app_version'],
            datetime.datetime.now()
        ))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # SQS Queue URL
    queue_url = "http://localhost:4566/000000000000/login-queue"

    # Postgres credentials
    db_credentials = {
        'database': 'postgres',
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432',
    }

    # Part 1: read JSON data containing user login behavior from an AWS SQS Queue
    json_data = read_from_aws_sqs(queue_url)
    data = [json.loads(msg['Body']) for msg in json_data]

    if len(data) == 0:
        print('No data from sqs')
        exit(1)

    # Fill null values with some default values
    for ele in data:
        if 'app_version' not in ele:
            ele['app_version'] = '0.0.0'
        if 'ip' not in ele:
            ele['ip'] = '0.0.0.0'
        if 'device_id' not in ele:
            ele['device_id'] = '0-0-0'        


    # Part 2: hide personal identifiable information (PII).
    masked_data = pii_masking(data)

    # Convert app_version to integer 
    for ele in data:
        ele['app_version'] = version_string_to_int(ele['app_version'])


    # Part 3: Write to Postgres
    write_to_postgres(masked_data, db_credentials)


    # Delete processed messages from SQS
    delete_messages_from_sqs(queue_url, json_data)

    
