import configparser
import pandas as pd
import requests

### API 중계서버 연결
config = configparser.ConfigParser()
config.read('config.cfg', encoding='utf-8')
url = config.get('BROKER', 'BROKER_SERVER')

def wwma(values, n):
    """
     J. Welles Wilder's EMA 
    """
    return values.ewm(alpha=1/n, adjust=False).mean()

## calcutae ATR
## input : Dataframe(High, Low, Close)
## output : int(ATR)
def atr(stock_code, n, mul_value, res_opt):
    try:
        stock_code = stock_code[1:]
             
        URL = 'http://' + url + '/chart?code='+'A'+stock_code+'&n=' + str(n + 1)
        response = requests.get(URL)
        data = pd.read_json(response.text, orient='records')

        high = data['high']
        low = data['low']
        close = data['close']

        data['tr0'] = abs(high - low)
        data['tr1'] = abs(high - close.shift())
        data['tr2'] = abs(low - close.shift())
        data = data.dropna()
    
        tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        
        atr = round(wwma(tr, n))
        data = data.iloc[-1:]

        if res_opt == 'plus':
            result = data['close'] + round(atr * mul_value)

        elif res_opt == 'minus':
            result = data['close'] - round(atr * mul_value)

        return result

    except:
        return 0

## Range
def get_range(stock_code):
    stock_code = stock_code[1:]
    URL = 'http://' + url + '/chart?code=' +'A'+stock_code+'&n=1'

    response = requests.get(URL)
    raw_value = pd.read_json(response.text, orient='records')

    range = raw_value['high'][0] - raw_value['low'][0]
    buy_price = raw_value['close'][0] - round(range * 0.25)

    return buy_price

## 볼밴    
def bbands(stock_code, n, opt):
    stock_code = stock_code[1:]
    URL = 'http://' + url + '/chart?code=' + 'A' + stock_code + '&n=' + str(n + 1)

    response = requests.get(URL)
    raw_value = pd.read_json(response.text, orient='records').drop_duplicates()[::-1]
    value_len = len(raw_value.index)

    raw_value['UpperBand'] = raw_value['close'].rolling(value_len).mean() + raw_value['close'].rolling(value_len).std() * 1.5
    raw_value['LowerBand'] = raw_value['close'].rolling(value_len).mean() - raw_value['close'].rolling(value_len).std() * 1.5
    
    if opt == 'up':
        return raw_value['UpperBand'][-1]

    elif opt == 'down':
        return raw_value['LowerBand'][-1]
    
    else:
        return False

## 피벗
def pivot(stock_code):
    stock_code = stock_code[1:]
    URL = 'http://' + url + '/chart?code=' + 'A' + stock_code + '&n=1'

    response = requests.get(URL)
    res = pd.read_json(response.text, orient='records').drop_duplicates()
    
    halfline = (res['high'][0] + res['low'][0] + res['close'][0])/3

    return halfline 

## 이등분선
def halfline(stock_code):
    stock_code = stock_code[1:]
    URL = 'http://' + url + '/chart?code=' + 'A' + stock_code + '&n=1'

    response = requests.get(URL)
    res = pd.read_json(response.text, orient='records').drop_duplicates()
    
    halfline = (res['high'][0] + res['low'][0])/2

    return halfline 

## 전일종가
def pastend(stock_code):
    stock_code = stock_code[1:]
    URL = 'http://' + url + '/chart?code=' + 'A' + stock_code + '&n=1'

    response = requests.get(URL)
    res = pd.read_json(response.text, orient='records').drop_duplicates()
    
    pastend = res['close'][0] 

    return pastend
