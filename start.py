'''
크롤링, 최적화, 트레이딩 서버 관리
1. 크롤링
2. 매수매도북 최적화
3. 서버기동
'''
import configparser
import subprocess
import pandas as pd

# 커스텀 모듈 임포트
from Crawling import crawling
import Optimize.orderbook

if __name__ == '__main__':
    print('---------------------------------')
    print('\n[HAYMAN TRADER FOR GENPORT]\n')
    print('---------------------------------')

    # 1. 크롤링
    config = configparser.ConfigParser()
    config.read('config.cfg', encoding='utf-8')

    gen_id = config.get('CRAWLING', 'NEWSY_ID')
    gen_pw = config.get('CRAWLING', 'NEWSY_PW')
    port_list = config.get('CRAWLING', 'PORT_LIST').split(', ')
    
    crawling.start(gen_id, gen_pw, port_list)
    
    # 2. 매수매도북 최적화
    raw_buybook = pd.read_json('Server/raw_buybook.json')
    raw_sellbook = pd.read_json('Server/raw_sellbook.json')

    opt_buybook = Optimize.orderbook.Buybook(raw_buybook)
    opt_sellbook = Optimize.orderbook.Sellbook(raw_sellbook)

    opt_buybook.routine()
    opt_sellbook.routine()

    subprocess.Popen(['python', "Server/server.py"], shell=True)

