# lambda/index.py
import json
import os
import re  # 正規表現モジュールをインポート
import requests
from botocore.exceptions import ClientError

# FastAPIのURL（公開URL）をここに設定！
FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://32c3-34-124-163-121.ngrok-free.app")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Cognitoユーザー情報（あれば使えるが、なくてもいい）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']

        print("Sending message to FastAPI server:", message)

        # FastAPIサーバーにリクエストを送る
        fastapi_response = requests.post(
            FASTAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"prompt": message}
        )
        fastapi_response.raise_for_status()
        result = fastapi_response.json()

        print("FastAPI server response:", json.dumps(result))

        # 成功レスポンスをLambdaの戻り値に使う
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": result,  # FastAPIから返ってきた結果をそのまま
            })
        }

    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }