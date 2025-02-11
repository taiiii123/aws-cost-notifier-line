import json
import requests
import logging
import os
import sys

from utils.constants import *

# LINE APIのエンドポイント
URL = os.getenv("LINE_URL", None)
# チャンネルアクセストークン
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
# 送信先ID
LINE_USER_ID = os.getenv("LINE_USER_ID", None)

# ログの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数が無いならエラー
if URL is None:
    logger.error('Specify LINE_URL as environment variable.')
    sys.exit(1)
if LINE_ACCESS_TOKEN is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if LINE_USER_ID is None:
    logger.error('Specify LINE_USER_ID as environment variable.')
    sys.exit(1)

def send_line_message(message):
    """LINEにメッセージを送信"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        response = requests.post(URL, headers=headers, json=data)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外をスロー
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to LINE: {e}")
        raise  # 例外を再スロー

def lambda_handler(event, context):
    """SNSからの通知を受け取り、LINEに転送"""
    try:
        logger.info(f"event: {event}")
        sns_message = event['Records'][0]['Sns']['Message']
        budget_alert = json.loads(sns_message)
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing SNS message: {e}")
        return create_error_response(STATUS_CODE_400, ERROR_PARSING_SNS_MESSAGE)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from SNS message: {e}")
        return create_error_response(STATUS_CODE_400, ERROR_DECODING_JSON)

    budget_name = budget_alert.get('BudgetName', '不明な予算')
    budget_amount = budget_alert.get('BudgetAmount', '不明')  # 予算の設定額
    actual_cost = budget_alert.get('ActualCost', '不明')  # 実際のコスト

    if not budget_name or not budget_amount or not actual_cost:
        logger.error("Missing required data (BudgetName, BudgetAmount, or ActualCost).")
        return create_error_response(STATUS_CODE_400, ERROR_MISSING_DATA)

    message = (
        f"🚨 AWSコストアラート 🚨\n"
        f"{LINE}\n"
        f"📌予算名: {budget_name}\n"
        f"📌予算設定額: {budget_amount} USD\n"  # 予算額の表示
        f"📌現在のコスト: {actual_cost} USD"  # 実際のコストの表示
    )

    try:
        send_line_message(message)
    except Exception as e:
        logger.error(f"Error sending message to LINE: {e}")
        return create_error_response(STATUS_CODE_500, ERROR_SENDING_MESSAGE)

    return create_success_response()  # 成功時のレスポンス
