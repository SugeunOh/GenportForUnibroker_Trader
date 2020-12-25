'''
트레이딩 서버
'''
import configparser
from flask import Flask
import pandas as pd

## from server.scheduled_job_list import BuyBookRoutine

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# 스케줄링 작업 리스트
from schedule_list import PreOrder, ControlAmountbook


app = Flask(__name__)

executors = {
    'default': ThreadPoolExecutor(32),
    'processpool': ProcessPoolExecutor(16)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

sched = BackgroundScheduler(timezone='Asia/Seoul', executors=executors, job_defaults=job_defaults)

preorder = PreOrder()
controlamountbook = ControlAmountbook()

## 예약 작업 추가
sched.add_job(preorder.routine, 'cron', day_of_week='mon-fri', hour=8, minute=53)
sched.add_job(controlamountbook.routine_day, 'cron', day_of_week='mon-fri', minute='*')

print('-------- Scheduled Job List --------')
sched.print_jobs()
print('-------- ------------------ --------')

## 매수오더북
@app.route('/buybook', methods=['GET'])
def get_buybook():
    res_df = pd.read_json('Server/opt_buybook.json')     
    result = res_df.to_json(orient='records', indent=4, force_ascii=False) 

    return result

## 매도오더북
@app.route('/sellbook', methods=['GET'])
def get_sellbook():
    res_df = pd.read_json('Server/opt_sellbook.json') 
    result = res_df.to_json(orient='records', indent=4, force_ascii=False) 
    
    return result

## 계좌현황
@app.route('/accountbook', methods=['GET'])
def get_accbook():
    controlamountbook.routine_req()
    res_df = pd.read_json('amountbook.json') 
    result = res_df.to_json(orient='records', indent=4, force_ascii=False) 
    
    return result
    
if __name__ == '__main__':
    sched.start()
    app.run(debug=True, port=2000)