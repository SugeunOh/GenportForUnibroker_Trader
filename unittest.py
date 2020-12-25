import configparser
import pandas as pd
import subprocess

# 커스텀 모듈 임포트
from Crawling import crawling
import Optimize.orderbook
import Server.schedule_list

## 크롤링 테스트
class Test():

    ## 크롤링
    def crawling():
        config = configparser.ConfigParser()
        config.read('config.cfg', encoding='utf-8')

        gen_id = config.get('CRAWLING', 'NEWSY_ID')
        gen_pw = config.get('CRAWLING', 'NEWSY_PW')
        port_list = config.get('CRAWLING', 'PORT_LIST').split(', ')

        crawling.start(gen_id, gen_pw, port_list)
    
        return True

    ## 매수매도 최적화
    def optimize():
        raw_buybook = pd.read_json('Server/raw_buybook.json')
        raw_sellbook = pd.read_json('Server/raw_sellbook.json')

        opt_buybook = Optimize.orderbook.Buybook(raw_buybook)
        opt_sellbook = Optimize.orderbook.Sellbook(raw_sellbook)

        opt_buybook.routine()
        opt_sellbook.routine()
        
        return True

    def scheduled_job():
        preorder = Server.schedule_list.PreOrder()
        controlamountbook = Server.schedule_list.ControlAmountbook()

        preorder.routine()
        controlamountbook.routine()

if __name__ == '__main__':
    ## Test.crawling()
    ## Test.optimize()
    Test.scheduled_job()