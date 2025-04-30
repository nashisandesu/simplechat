# lambda/index.py
import json
import os
import urllib.request

# APIのURL
API_URL = os.environ.get("API_URL", "https://8d8c-34-143-153-8.ngrok-free.app/generate")

def lambda_handler(event, context):
    try:
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        print("Using API:", API_URL)

        # 外部API用のリクエストペイロード
        api_request_payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        data = json.dumps(api_request_payload).encode("utf-8")

        print("Calling external API with payload:", data)

        req = urllib.request.Request(
            API_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as resp:
            response_body = resp.read().decode("utf-8")
        api_response = json.loads(response_body)

        print("API response:", api_response)
        
        # アシスタントの応答を取得
        assistant_response = api_response['generated_text']
        conversation_history.append({
            "role": "user",
            "content": message
        })

        conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # 成功レスポンスの返却
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
                "response": assistant_response,
                "conversationHistory": conversation_history
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
