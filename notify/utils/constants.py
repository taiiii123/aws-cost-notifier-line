import json

# ステータスコードとメッセージの定数
STATUS_CODE_400 = 400
STATUS_CODE_500 = 500
STATUS_CODE_200 = 200

# エラーメッセージの定数
ERROR_PARSING_SNS_MESSAGE = "Error parsing SNS message"
ERROR_DECODING_JSON = "Error decoding JSON from SNS message"
ERROR_MISSING_DATA = "Missing required data (BudgetName or NewThreshold)"
ERROR_SENDING_MESSAGE = "Error sending message"

# 成功メッセージの定数
SUCCESS_MESSAGE = "Notification sent to LINE!"

def create_error_response(status_code, message):
    return {
        'statusCode': status_code,
        'body': json.dumps(message)
    }

def create_success_response():
    return {
        'statusCode': STATUS_CODE_200,
        'body': json.dumps(SUCCESS_MESSAGE)
    }


LINE = "-" * 40
