import os
from dotenv import load_dotenv
load_dotenv ()
import pyupbit

def ai_trading():
  # 1. 업비트 차트 데이터(30일 일봉) 가져오기
  df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')

  # 2. AI에게 데이터 제공하고 판단 받기
  from openai import OpenAI
  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": "You are an expert in Bitcoin investing. Tell me whether to buy, sell, or hold at the moment based on the chart data provided. response in json format.\n\nResponse Example: \n{\"decision\": \"buy\", \"reason\": \"some  technical reason\"}\n{\"decision\": \"sell\", \"reason\": \"some  technical reason\"}\n{\"decision\": \"hold\", \"reason\": \"some  technical reason\"}\n"
          }
        ]
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": df.to_json()
          }
        ]
      },
      {
        "role": "assistant",
        "content": [
          {
            "type": "text",
            "text": "{\"decision\": \"hold\", \"reason\": \"The Bitcoin price data shows recent volatility with significant price increases, yet recent closing prices suggest potential stabilization. While there was a drop observed on the last date in the dataset, the overall upward trend suggests a hold strategy to monitor further trends in case of future gains.\"}"
          }
        ]
      }
    ],
    response_format={
      "type": "json_object"
    },
  )
  result = response.choices[0].message.content

  # 3. 판단에 따라 실제로 자동 매매 진행하기
  import json
  result = json.loads(result) # 결과를 딕셔너리 형식으로 바꿈

  # 업비트 로그인
  access = os.getenv("BITHUMB_ACCESS_KEY")  # 개인 업비트나 빗썸 ACCESS_KEY 삽입     
  secret = os.getenv("BITHUMB_SECRET_KEY")  # 개인 업비트나 빗썸 SECRET_KEY 삽입
  upbit = pyupbit.Upbit(access, secret)

  print("### AI Decision: ", result["decision"].upper(), "###")
  print(f"### Reason: {result['reason']} ###")

  if result['decision'] == 'buy': # 매수
    my_krw = upbit.get_balance("KRW") # 현재 가진 원화
    if my_krw*0.9995 > 5000:  
      print("### Buy Order Executed ###")
      print(upbit.buy_market_order("KRW-BTC", my_krw*0.9995)) # 수수료 때문에 * 0.9995해야 거래가 진행됨
    else:
      print("### Buy Order Failed: Insufficient KRW (less than 5000 KRW) ###")

  elif result['decision'] == 'sell': # 매도
    my_btc = upbit.get_balance("KRW-BTC")
    current_price = pyupbit.get_orderbook(ticker="KRW-BTC")['orderbook_units'][0]['ask_price']

    if my_btc*current_price > 5000:
      print("### Sell Order Executed ###")
      print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")))
    else:
      print("### Sell Order Failed: Insufficient BTC (less than 5000 KRW worth) ###")

  elif result['decision'] == 'hold': # hold
    print("### Hold Position ###")

while True:
  import time
  time.sleep(10) # 10초마다 함수 실행
  ai_trading()