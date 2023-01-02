import json
import requests
import time
import os
from datetime import datetime
from .extractors.quBeyond_order_extractor import QuBeyondOrderExtractor



def timestampTodatetime(timestamp):
    delta_from_date = datetime.fromtimestamp(timestamp).strftime('%m%d%Y')
    delta_from_time = datetime.fromtimestamp(timestamp).strftime('%H%M')
    return delta_from_date, delta_from_time


def fetch_last_execution_time() -> tuple[str, str]:
    config_path = "last_runtime.txt"
    if "LAMBDA_TASK_ROOT" in os.environ.keys():
        config_path = os.environ['LAMBDA_TASK_ROOT'] + "/last_runtime.txt"
    try:
        with open("last_runtime.txt", "r+") as f:
            timestamp = json.loads(f.read())["last_execution_timestamp"] #MMDDYYYY
            return timestampTodatetime(timestamp)
    except:
        # default to returning 1 day ago
        timestamp = int((time.time() - 86400))
        return timestampTodatetime(timestamp)

def update_last_execution_time(config: dict, the_time: int):
    config_path = "last_runtime.txt"
    if "LAMBDA_TASK_ROOT" in os.environ.keys():
        config_path = os.environ['LAMBDA_TASK_ROOT'] + "/last_runtime.txt"
    run_time_dict = {"last_execution_timestamp": the_time}
    try:
        with open(config_path, "w+") as file:
            file.write(json.dumps(run_time_dict))
    except Exception as e:
        pass

def get_order_extraction_config() -> list:
    last_execution_date, last_execution_time = fetch_last_execution_time()
    return [{
        "Auth_URL": "https://auth.qubeyond.com/api/v3.5/token",
        "BaseUrl": "https://reporting-api.qubeyond.com/api/v3.5/export",
        "userName": "UserName",
        "password": "Password",
        "companyId": 365,
        "locationId": 317,
        "http_method": "GET",
        "auth_mode": "Bearer",
        "delta_from_date": last_execution_date,
        "delta_from_time": last_execution_time,
        "order_status": DEFAULT_ORDER_STATUS

    }]

def lambda_handler(event, context):
    
    http_method = event["httpMethod"]
    if (http_method != "POST"):
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Bad Request",
                "description": f"{http_method}: Method not implemented",
            })
        }

    extraction_configs = get_order_extraction_config()

    auth_payload = {
        "username": "UserName",
        "password": "Password"
    }

    auth_response = requests.post("https://api.example.com/user/signin", data=json.dumps(auth_payload))
    auth_json = json.loads(auth_response.text)
    token = auth_json["AuthenticationResult"]["IdToken"]

    # TODO: Refactor to use Threadpool Executor for concurrent processing per connector
    for config in extraction_configs:
        extractor = QuBeyondOrderExtractor(config)
        update_last_execution_time(config, int(time.time()))
        orders = extractor.get_default_orders() #TODO: By-default default orders will be transformed

        headers = {
            "Authorization": f"Bearer {token}"
        }

        payload = json.dumps(orders)
        x = requests.post('https://api.example.com/brand/1/store/1/order', headers=headers, data=payload)
        print(x.status_code)

    return {
        'statusCode': 200,
        'body': json.dumps("ok")
    }

