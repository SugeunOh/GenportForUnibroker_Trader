# **GENPORT FOR UNIBROKER**

젠포트에서 지원되지 않는 증권사에서 트레이딩을 할 수 있습니다.

* * *
**이 프로그램으로 인해 발생하는 손실에 대해 프로그램 제작자는 일체의 책임을 지지 않습니다.** 

**모의투자를 이용한 테스팅 수행 후 실전 운용을 하시기 바랍니다.**
* * *

## **사용방법**

1. 의존성을 설치합니다.
    > pip install -r requirements.txt

2.  [Flask-KorStockBroker](https://github.com/lyy9257/Flask-KoreaStockBroker)
를 실행합니다.

3. config.cfg 파일에 정보를 입력합니다.
 
        [CRAWLING]
        NEWSY_ID = (젠포트 ID)
        NEWSY_PW = (젠포트 비밀번호)
        PORT_LIST = (포트폴리오 리스트, 111111, 222222, 333333 형식으로 입력)

        [BROKER]
        BROKER_SERVER = (본인 컴퓨터 기준 127.0.0.1:5000)
        BROKER_NAME = 

4. start.py 파일을 실행합니다.
    > python start.py

* * *

## **프로그램 구조**

![1](Diagram\customprice.png)


## **지원되는 기능**

1. 1개 계좌에서 여러 포트를 한큐에 트레이딩합니다.
2. 매수가, 매도가의 커스텀이 가능합니다.(Optimize-Custom.py 파일 수정을 통해)
3. 8시 52분에 매수 주문을 수행합니다.
4. 장시간동안 약 7~8초 간격으로 손절, 매도, 익절 감시를 수행합니다.


