import requests
from twilio.rest import Client
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

api_endpopint = "https://www.alphavantage.co/query"

NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"

# STEP 1: Use https://www.alphavantage.co
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": os.environ.get("API_KEY")
}
response = requests.get(url=api_endpopint, params=params)
response.raise_for_status()

data = response.json()["Time Series (Daily)"]
# turn data from dict to list
data_list = [value for (key, value) in data.items()]

# get latest data
yesterday_data = data_list[0]
yesterday_closing_price = yesterday_data["4. close"]

# get latest data - 1
day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = day_before_yesterday_data["4. close"]

difference = float(yesterday_closing_price) - float(day_before_yesterday_closing_price)
up_down = None
if difference > 0:
    up_down = "📈"
else:
    up_down = "📉"
diff_percent = round((difference / float(yesterday_closing_price)) * 100)

## STEP 2: Use https://newsapi.org
if abs(diff_percent) > 5:
    news_params = {
        "apIKey": os.environ.get("NEWS_API_KEY"),
        "qInTitle": COMPANY_NAME,
    }

    response_news = requests.get(url=NEWS_API_ENDPOINT, params=news_params)
    response_news.raise_for_status()
    articles = response_news.json()["articles"]

    three_articles = articles[:3]

    ## STEP 3: Use https://www.twilio.com
    formatted_articles = [
        f"{STOCK}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for
        article in
        three_articles]
    client = Client(os.environ.get("TWILLIO_ACCOUNT_SID"), os.environ.get("TWILLIO_AUTH_TOKEN"))
    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=os.environ.get("TWILLIO_FROM_NUMBER"),
            to=os.environ.get("TWILLIO_TO_NUMBER")
        )
        print(message.status)
