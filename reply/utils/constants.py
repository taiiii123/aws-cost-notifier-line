# リターン値の設定
OK_JSON = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {},
    "body": ""
}
ERROR_JSON = {
    "isBase64Encoded": False,
    "statusCode": 500,
    "headers": {},
    "body": "Error"
}

# Cost Explorer 用のリージョン
AWS_REGION = "us-east-1"

# メッセージキーワード
MESSAGE_KEYWORDS = (
    "コスト確認",
    "コスト",
    "cost",
    "料金確認",
    "料金"
)

LINE = "-" * 40
