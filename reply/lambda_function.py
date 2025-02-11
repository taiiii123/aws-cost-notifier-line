import os
import sys
import logging
import boto3
import json

from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import datetime

from utils.constants import *

# ログの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# LINEBotのチャンネルアクセストークン
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# チャンネルアクセストークンがない場合、エラー終了
if not CHANNEL_ACCESS_TOKEN:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

# LINEBotのAPI
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
client = boto3.client("ce", region_name=AWS_REGION)

def get_cost_data():
    """AWSの使用料金を取得する"""
    today = datetime.today()
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"]
    )

    return response

def send_cost_message(reply_token, cost_data):
    """AWSコスト情報をLINEで送信する"""
    for result in cost_data["ResultsByTime"]:
        cost_amount = float(result['Total']['UnblendedCost']['Amount'])
        formatted_cost = f"{cost_amount:,.2f}"

        text = (
            "💰 AWS コスト確認 💰\n"
            f"{LINE}\n"
            "📅 料金集計期間\n"
            f"📌 {result['TimePeriod']['Start']} 〜 {result['TimePeriod']['End']}\n\n"
            "💸 AWSの使用料金\n"
            f"📌 {formatted_cost} USD\n\n"
        )
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

def lambda_handler(event, context):
    try:
        logger.info(f"event :{event}")
        body = json.loads(event['body'])
        events = body.get("events", [])

        if not events:
            logger.info("No events found")
            return ERROR_JSON

        # メッセージタイプが 'text' かどうかを確認
        if events[0].get('type') == 'message' and events[0].get('message', {}).get('type') == 'text':
            reply_token = events[0].get('replyToken')
            message_text = events[0].get('message', {}).get('text')

            # キーワードにマッチする場合にコストデータを送信
            if message_text in MESSAGE_KEYWORDS:
                logger.info("START_GET_COST_DATA")
                cost_data = get_cost_data()
                logger.info("END_GET_COST_DATA")
                logger.info("START_SEND_COST_MESSAGE")
                send_cost_message(reply_token, cost_data)
                logger.info("END_SEND_COST_MESSAGE")

    except Exception as e:
        logger.error(f"Error: {e}")
        return ERROR_JSON

    return OK_JSON
