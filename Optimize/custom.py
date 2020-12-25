'''
커스텀 함수
현재 추가된 기능 : 매수, 매도가 설정
'''
import configparser
import math
import numpy as np
import pandas as pd
import random

from Optimize.talib import *

# 가격 설정
# orderbook['종목코드'].apply(labmda x : buyprice(x)) 형식으로 적용하여 사용
# Input : 종목코드
# Output : 매수가
class Price():

    ### 초기화
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg', encoding='utf-8')
        self.broker_server = self.config.get('BROKER', 'BROKER_SERVER')

    ### 매수가
    def buyprice(self, stock_code):
        buy_line = (1.7, 1.8, 1.9, 2.0)
        hitline = random.choice(buy_line)/100
        price = pastend(stock_code) * (1 - hitline)
        buy_price = self.set_hoga(price)

        return buy_price

    ### 매도가 설정
    ### orderbook['종목코드'].apply(labmda x : sellprice(x)) 형식으로 적용하여 사용
    ### Input : 종목코드
    ### Output : 매도가
    def sellprice(self, stock_code):
        price = (pastend(stock_code) + halfline(stock_code) + pivot(stock_code))/3
        sell_price = self.set_hoga(price)
        
        return sell_price

    ### 익절가 설정
    ### orderbook['종목코드'].apply(labmda x : sellprice(x)) 형식으로 적용하여 사용
    ### Input : 종목코드
    ### Output : 익절가
    def exitprice(self, stock_code):
        exit_price = '-'
        return exit_price

    ### 손절가 설정
    ### orderbook['종목코드'].apply(labmda x : sellprice(x)) 형식으로 적용하여 사용
    ### Input : 종목코드
    ### Output : 손절가
    def cutprice(self, stock_code):
        cut_price = '-'
        return cut_price

    ### 존재하는 호가에 맞추어 가격 보정
    ### 업, 다운중 가까운 호가에 맞추어 보정
    def set_hoga(self, price):
        if price - self.downPrice(price) > price - self.upPrice(price):
            return self.upPrice(price)

        else:
            return self.downPrice(price)

    ## 호가단위 계산
    def hogaUnitCalc(self, price):
        hogaUnit = 1
        if price < 1000:
            hogaUnit = 1
        elif price < 5000:
            hogaUnit = 5
        elif price < 10000:
            hogaUnit = 10
        elif price < 50000:
            hogaUnit = 50
        elif price < 100000 :
            hogaUnit = 100
        
        return hogaUnit

    ## 호가단위 계산(내림)
    def downPrice(self, currentPrice):
        hogaPrice = math.floor(currentPrice) # 소수점은 내려준다.
        hoga = self.hogaUnitCalc(hogaPrice) # 호가 단위를 구한다.
        
        # 안나눠 떨어질 경우  -> 나눠질때까지 1씩 빼준다.
        while hogaPrice % hoga  != 0 :
            hogaPrice = hogaPrice - 1

        return hogaPrice
        
    ## 호가단위 계산(올림)
    def upPrice(self, currentPrice):
        hogaPrice = math.floor(currentPrice) # 소수점은 내려준다.
        hoga = self.hogaUnitCalc(hogaPrice) # 호가 단위를 구한다.
        
        # 안나눠 떨어질 경우  -> 나눠질때까지 1씩 더해준다.
        while hogaPrice % hoga  != 0 :
            hogaPrice = hogaPrice + 1

        return hogaPrice