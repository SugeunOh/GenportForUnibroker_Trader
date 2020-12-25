import configparser
import time
import json
import pandas as pd
import requests
from datetime import datetime
import os

past_dir = os.path.dirname(os.getcwd())

# 주문
class Order():

    ### 필요데이터 설정
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg', encoding='utf-8')
        self.broker_port = self.config.get('BROKER', 'BROKER_SERVER')
        self.res_url_head = 'http://' + self.broker_port + '/'

    ## 람다용
    ## 매수주문 
    def buy_order(self, buy_row):

        ### 계좌조회
        acc_url = self.res_url_head + 'accountinfo'
        res = requests.get(acc_url).text
        acc_num = json.loads(res)['acc_num']
        
        ### URL 조합
        endpoint = 'buy'
        acc = '?acc=' + acc_num        
        
        ### 주문정보
        stock_code = str(buy_row['종목'][0])
        front_code = '&front=' + stock_code[0]
        code = '&code=' + stock_code[1:]
        price = '&price=' + str(buy_row['매수가'])
        amount = '&amount=' + str(buy_row['수량'])

        ### 주문 리퀘스트
        buy_url = self.res_url_head + endpoint + acc + front_code + code + amount + price
        res = requests.get(buy_url).text

        trade_result = str(json.loads(res)['message']) # Result     

        return trade_result[:5]

    ## 매도주문
    def sell_order(self, sell_row):

        ### 계좌조회
        acc_url = self.res_url_head + 'accountinfo'
        res = requests.get(acc_url).text
        acc_num = json.loads(res)['acc_num']
        
        ### URL 조합
        endpoint = 'sell'
        acc = '?acc=' + acc_num        

        ### 주문정보
        stock_code = str(sell_row['종목'])
        front_code = '&front=' + stock_code[0]
        code = '&code=' + stock_code[1:]
        price = '&price=' + str(sell_row['매도가'])
        amount = '&amount=' + str(sell_row['수량'])

        ### 주문 리퀘스트
        buy_url = self.res_url_head + endpoint + acc + front_code + code + amount + price
        res = requests.get(buy_url).text
        trade_result = str(json.loads(res)['message']) # Result     
        
        return trade_result[:5]

# input : buybook, sellbook
# output : 주문현황 추가
class PreOrder():

    ### 필요데이터 설정
    def __init__(self):
        self.buybook = pd.read_json('Server/opt_buybook.json')
        self.sellbook = pd.read_json('Server/opt_sellbook.json')
        self.order = Order()

        self.config = configparser.ConfigParser()
        self.config.read('config.cfg', encoding='utf-8')
        self.broker_port = self.config.get('BROKER', 'BROKER_SERVER')
        self.res_url_head = 'http://' + self.broker_port + '/'

    ## 매수주문
    def buy(self):
        if len(self.buybook.index) > 0:
            self.buybook['현황'] = self.buybook.apply(self.order.buy_order, axis=1)

        else:
            self.buybook = pd.DataFrame(['-'], '금일 매수종목이 없습니다!')

        ## json 파일로 저장(API 통신)
        with open('today_buybook.json', 'w', encoding='utf-8') as book:
            self.buybook.to_json(book, orient='records', indent=4, force_ascii=False)

    ## 매도주문
    def sell(self):
        if len(self.sellbook.index) > 0:
            self.sellbook['현황'] = self.sellbook.apply(self.order.sell_order, axis=1)

        else:
            self.sellbook = pd.DataFrame(['-'], '금일 매도종목이 없습니다!')
            ## json 파일로 저장(API 통신)

        ## json 파일로 저장(API 통신)
        with open('today_sellbook.json', 'w', encoding='utf-8') as book:
            self.sellbook.to_json(book, orient='records', indent=4, force_ascii=False)

    ## 전체루틴
    def routine(self):
        self.buy()
        ## self.sell()

        return True


# 계좌북 현황호출
# input : raw_buybook
# output : opt_buybook([종목, 수량, 매수가(-), 매도가, 익절가, 손절가])
class ControlAmountbook():
    def __init__(self):
        ### 필요데이터 설정
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg', encoding='utf-8')
        self.broker_port = self.config.get('BROKER', 'BROKER_SERVER')
        self.res_url_head = 'http://' + self.broker_port + '/'
        
        self.order = Order() 
        self.sellbook = pd.read_json('Server/opt_sellbook.json')
        self.opt_amountbook = pd.DataFrame(
            columns=['종목', '이름', '수량', '수익률', '매수가', '현재가', '손익가', '매도가', '익절가', '손절가']
        )

    ## 호출 
    def request_acc(self):
        try:
            ### 호출 
            acc_url = self.res_url_head + 'stockaccountinfo'
            res = requests.get(acc_url).text

            ### 데이터 호출
            self.raw_amountbook = pd.read_json(res, orient='records')

            self.raw_amountbook['익절가'] = (self.amountbook['손익단가'] * 1.06).astype(int) # 6% 익절
            self.raw_amountbook['손절가'] = (self.amountbook['손익단가'] * 0.92).astype(int) # 8% 손절  
            
            return True

        except:
            return True

    ## 람다용
    ## 매도가 호출
    def get_sellprice(self, stockcode):
        try:
            indices = list(np.where(self.sellbook["종목"] == stockcode)[0])
            price = self.sellbook.iloc[indices]['매도가'].get_value()
        except:
            price = 0
        
        return 0
    
    ## 손익절감시
    def watch_exitcut(self, idx):
        now = idx['현재가']
        sellprice = idx['매도가']
        exitprice = idx['익절가']
        cutprice = idx['손절가']

        order_data = idx[['종목', '현재가', '수량']].rename({'현재가':'매도가'})

        ### 매도가 도달
        if sellprice > 0:
            if sellprice < now:
                result = '[매도] ' + self.order.sell_order(order_data)

                return result 

        else:
            pass

        ### 손절 도달시
        if cutprice > now:
            result = '[손절] ' + self.order.sell_order(order_data)

        ### 익절 도달
        elif exitprice < now:
            result = '[익절] ' + self.order.sell_order(order_data)  

        ### 없으면 감시
        else:
            result = '지속감시'

        return result 


    ## json양식과 매칭
    def match(self):
        self.opt_amountbook['종목'] = self.raw_amountbook['종목코드']
        self.opt_amountbook['이름'] = self.raw_amountbook['종목명']
        self.opt_amountbook['수량'] = self.raw_amountbook['매도가능수량']
        self.opt_amountbook['수익률'] = self.raw_amountbook['수익률'].round(2).astype(str)
        self.opt_amountbook['매수가'] = self.raw_amountbook['체결장부단가'].astype(int)
        self.opt_amountbook['손익가'] = self.raw_amountbook['손익단가']

        self.opt_amountbook['매도가'] = self.opt_amountbook['종목'].apply(lambda k : self.get_sellprice(k))
        self.opt_amountbook['익절가'] = (self.raw_amountbook['체결장부단가'] * 1.08).astype(int)
        self.opt_amountbook['손절가'] = (self.raw_amountbook['체결장부단가'] * 0.9).astype(int)

        return True

    ## 람다식
    ## 현재가 확인
    def now_price(self, stock_code):
        URL = self.res_url_head + '/chart?code=' + stock_code + '&n=1'
        response = requests.get(URL)
        raw_value = pd.read_json(response.text, orient='records')
        price_now = raw_value['close'][0]

        return price_now

    ## 종목감시
    def marketeye(self):
        if len(self.opt_amountbook.index) > 0:

            '''
            ## 종목리스트 호출
            stocklist = 'code=' + self.opt_amountbook['종목'] + '&'

            ## 계좌번호 호출
            
            url = self.res_url_head + 'marketeye' + '?' + ' '.join([str(elem) for elem in stocklist.tolist()]) 
            res = requests.get(url).text
            json_data = json.loads(res)
            print(url)
            self.opt_amountbook = self.opt_amountbook.drop(columns='현재가')

            marketeye_book = pd.DataFrame(json_data)[['종목코드', '현재가']]
            print(marketeye_book)
            self.opt_amountbook = self.opt_amountbook.join(marketeye_book.set_index('종목코드'), on='종목')
            '''

            self.opt_amountbook['현재가'] = self.opt_amountbook['종목'].apply(lambda k : self.now_price(k))
            self.opt_amountbook['손익절주문'] = self.opt_amountbook.apply(self.watch_exitcut, axis=1)

        ## 계좌 없을경우
        else:
            print('[INFO] Amount is Empty!')
            self.opt_amountbook = pd.DataFrame(['-'], '계좌에 종목이 없습니다!')
        
        return True

    ## 저장
    def save_json(self):
        ## json 파일로 저장(API 통신)
        with open('amountbook.json', 'w', encoding='utf-8') as book:
            self.opt_amountbook.to_json(book, orient='records', indent=4, force_ascii=False)

        return True

    def routine_day(self):
        res_time = datetime.now()
        start_time = 859
        end_time = 1530
        now_time = int(res_time.strftime('%H%M'))

        if now_time > start_time and now_time < end_time:
            for i in range(6):
                print('[%s/6]' %(i+1))
                self.request_acc()
                self.match()
                self.marketeye()
                self.save_json()
                time.sleep(7)

        else:
            print('[INFO] %s 현재 폐장 상태입니다.' %now_time)
            
        return True
    
    def routine_req(self):
        print('[INFO] Chatbot Requested')
        self.request_acc()
        self.match()
        self.marketeye()
        self.save_json()

        return True
