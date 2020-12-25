'''
최적화
'''
import configparser
import json
import numpy as np
import pandas as pd
import requests

import Optimize
from Optimize.custom import Price

# 매수북 최적화
# input : raw_buybook
# output : opt_buybook([종목, 수량, 매수가, 매도가(-), 익절가, 손절가])
class Buybook():
    def __init__(self, orderbook):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg', encoding='utf-8')

        self.raw_orderbook = orderbook
        self.opt_orderbook = pd.DataFrame(columns=['종목', '수량', '매수가', '매도가', '익절가', '손절가'])
        self.broker_server = self.config.get('BROKER', 'BROKER_SERVER')
        self.price = Optimize.custom.Price()

    ## 매수종목이 존재하는지 체크
    def check_exist_tradelist(self):
        chk_tradelist = self.raw_orderbook[self.raw_orderbook['종목코드'] != '매수 대상 종목이 없습니다.']
        
        if len(chk_tradelist.index) > 0:
            return True

        else:
            return False

    ## 매수종목 설정
    def make_stocklist(self):

        ### 매수종목 종목코드 호출
        self.opt_orderbook['종목'] = self.raw_orderbook[
            self.raw_orderbook['매수가격(원)'].apply(lambda x: not isinstance(x, str))
            ]['종목코드'].drop_duplicates()
        
        ### 포함 갯수확인
        self.opt_orderbook['포함갯수'] = self.opt_orderbook['종목'].apply(
            lambda k: len(self.raw_orderbook[self.raw_orderbook['종목코드'] == str(k)].index)
        )
        return True

    ## 매수가 설정
    def set_buyprice(self):
        self.opt_orderbook['매수가'] = self.opt_orderbook['종목'].apply(lambda k: self.price.buyprice(k))

        return True

    ## 매도가 설정
    def set_sellprice(self):
        self.opt_orderbook['매도가'] = ['-' for i in range(len(self.opt_orderbook.index))]

        return True

    ## 익절가 설정
    def set_exitprice(self):
        self.opt_orderbook['익절가'] = self.opt_orderbook['종목'].apply(lambda k: self.price.exitprice(k))

        return True

    ## 손절가 설정 
    def set_cutprice(self):
        self.opt_orderbook['손절가'] = self.opt_orderbook['종목'].apply(lambda k: self.price.cutprice(k))

        return True
    
    ## 주문비중 설정
    def set_ordersize(self):
        tot_ordersize = self.opt_orderbook['포함갯수'].astype(int).sum()
        self.opt_orderbook['비중'] = self.opt_orderbook['포함갯수'].apply(lambda k: round(k/tot_ordersize*100, 2)).astype(int)
        self.opt_orderbook = self.opt_orderbook.drop(columns='포함갯수')
        
        return True

    ### 매수수량 설정    
    def set_amount(self):
        res_url = 'http://' + self.broker_server + '/' + 'accountinfo'
        res = requests.get(res_url).text
        json_data = json.loads(res)

        twoday_money = int(json_data['twoday_amount'])

        self.opt_orderbook['금액'] = self.opt_orderbook['비중'].apply(lambda k: round(twoday_money * k/100))
        
        ## 매수 over를 방지하기 위해 1주 작게 제작 
        self.opt_orderbook['수량'] = (self.opt_orderbook['금액'] / self.opt_orderbook['매수가']).astype(int) - 1
        self.opt_orderbook = self.opt_orderbook.drop(columns='금액')

        return True

    ## json으로 저장
    def save_json(self):
        ## 필요데이터만 컷
        self.opt_orderbook = self.opt_orderbook[['종목', '수량', '매수가', '매도가', '익절가', '손절가']]

        with open('Server/opt_buybook.json', 'w', encoding='utf-8') as buybook:
            self.opt_orderbook.to_json(buybook, orient='records', indent=4, force_ascii=False)

        return True

    ## 전체루틴
    def routine(self):
        check_flag = self.check_exist_tradelist()
        
        if check_flag is True:
            self.make_stocklist()
            self.set_buyprice()
            self.set_sellprice()
            self.set_exitprice()
            self.set_cutprice()
            self.set_ordersize()
            self.set_amount()
        
        else:
            pass

        self.save_json()

        return True

# 매수북 최적화
# input : raw_buybook
# output : opt_buybook([종목, 수량, 매수가(-), 매도가, 익절가, 손절가])
class Sellbook():
    def __init__(self, orderbook):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg', encoding='utf-8')

        self.raw_orderbook = orderbook
        self.opt_orderbook = pd.DataFrame(columns=['종목', '수량', '매수가', '매도가', '익절가', '손절가'])
        self.broker_server = self.config.get('BROKER', 'BROKER_SERVER')
        self.price = Optimize.custom.Price()

    ## 매수종목이 존재하는지 체크
    def check_exist_tradelist(self):
        chk_tradelist = self.raw_orderbook[self.raw_orderbook['종목코드'] != '매도 대상 종목이 없습니다.']
        
        if len(chk_tradelist.index) > 0:
            return True

        else:
            return False

    ## 매도종목 설정
    def make_stocklist(self):

        ### 매수종목 종목코드 호출
        self.opt_orderbook['종목'] = self.raw_orderbook[
            self.raw_orderbook['매도가격(원)'].apply(lambda x: not isinstance(x, str))
            ]['종목코드'].drop_duplicates()
        
        ### 포함 갯수확인
        self.opt_orderbook['포함갯수'] = self.opt_orderbook['종목'].apply(
            lambda k: len(self.raw_orderbook[self.raw_orderbook['종목코드'] == str(k)].index)
        )

        return True

    ## 매수가 설정
    def set_buyprice(self):
        self.opt_orderbook['매수가'] = ['-' for i in range(len(self.opt_orderbook.index))]

        return True

    ## 매도가 설정
    def set_sellprice(self):
        self.opt_orderbook['매도가'] = self.opt_orderbook['종목'].apply(lambda k : self.price.sellprice(k))

        return True

    ## 익절가 설정
    def set_exitprice(self):
        self.opt_orderbook['손절가'] = self.opt_orderbook['종목'].apply(lambda k: self.price.exitprice(k))

        return True

    ## 손절가 설정 
    def set_cutprice(self):
        self.opt_orderbook['매수가'] = self.opt_orderbook['종목'].apply(lambda k: self.price.cutprice(k))

        return True

    ## 주문비중 설정
    def set_ordersize(self):
        tot_ordersize = len(self.opt_orderbook.index)
        self.opt_orderbook['비중'] = self.opt_orderbook['포함갯수'].apply(lambda k: round(k/tot_ordersize*100, 2)).astype(int)
        self.opt_orderbook = self.opt_orderbook.drop(columns='포함갯수')

        # print(self.opt_orderbook)

        return True

    ### 매수수량 설정    
    def set_amount(self):
        res_url = 'http://' + self.broker_server + '/' + 'accountinfo'
        res = requests.get(res_url).text
        json_data = json.loads(res)

        twoday_money = int(json_data['twoday_amount'])

        self.opt_orderbook['금액'] = self.opt_orderbook['비중'].apply(lambda k: round(twoday_money * k/100))
        
        ## 매수 over를 방지하기 위해 1주 작게 제작 
        self.opt_orderbook['수량'] = (self.opt_orderbook['금액'] / self.opt_orderbook['매수가']).astype(int) - 1
        self.opt_orderbook = self.opt_orderbook.drop(columns='금액')

        return True

    ## json으로 저장
    def save_json(self):
        self.opt_orderbook = self.opt_orderbook[['종목', '수량', '매수가', '매도가', '익절가', '손절가']]

        with open('Server/opt_sellbook.json', 'w', encoding='utf-8') as buybook:
            self.opt_orderbook.to_json(buybook, orient='records', indent=4, force_ascii=False)

        return True

    ## 전체루틴
    def routine(self):
        check_flag = self.check_exist_tradelist()
        
        if check_flag is True:
            self.make_stocklist()
            self.set_buyprice()
            self.set_sellprice()
            self.set_exitprice()
            self.set_cutprice()
        
        else:
            pass
            
        self.save_json()
        
        return True