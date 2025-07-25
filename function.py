from flask import Flask, request, render_template, url_for, session, redirect, jsonify
import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import mysql.connector
import atexit
from mysql.connector import Error


LED_PINS = { "red" : 2, "green" : 23, "blue" : 4}

GPIO.setmode(GPIO.BCM)

for pin in LED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)


BUZZER = 18
# LED_GREEN = 23
# LED_RED = 2
# LED_BLUE = 4
led_state = False

# DB 연결을 함수로 만들어 연결 끊김 문제 해결
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="test",
            password="12345",
            database="smartfarm"
        )
        return conn
    except Error as e:
        print(f"DB 연결 오류: {e}")
        return None

# GPIO 초기화 함수
def init_gpio():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUZZER, GPIO.OUT)
        GPIO.setwarnings(False)  # 경고 메시지 비활성화
        
        # 핀이 이미 사용 중인 경우를 대비해 정리
        try:
            GPIO.cleanup(LED_PINS["red"])
            GPIO.cleanup(LED_PINS["green"])
            GPIO.cleanup(LED_PINS["blue"])
        except:
            pass
            
        GPIO.setup(LED_PINS["green"], GPIO.OUT)
        GPIO.setup(LED_PINS["red"], GPIO.OUT)
        GPIO.setup(LED_PINS["blue"], GPIO.OUT)

        GPIO.output(LED_PINS["green"], GPIO.LOW)  # LED 초기 상태: OFF
        GPIO.output(LED_PINS["red"], GPIO.LOW)  # LED 초기 상태: OFF
        GPIO.output(LED_PINS["blue"], GPIO.LOW)  # LED 초기 상태: OFF

        print(f"GPIO green 초기화 완료")
        print(f"GPIO red 초기화 완료")
        print(f"GPIO blue 초기화 완료")
        return True
    
    except Exception as e:
        print(f"GPIO 초기화 오류: {e}")
        return False

def trigger_alarm():
    for _ in range(5):
        GPIO.output(BUZZER, True)
        GPIO.output(LED_PINS["red"], True)
        time.sleep(0.3)
        GPIO.output(BUZZER, False)
        GPIO.output(LED_PINS["red"], False)
        time.sleep(0.3)

def normal_alarm():
    for _ in range(3):
        GPIO.output(LED_PINS["green"], GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(LED_PINS["green"], GPIO.LOW)  # LED 초기 상태: OFF
        time.sleep(0.3)


# DHT11 센서를 GPIO 21번 핀에 연결
try:
    dht = adafruit_dht.DHT11(board.D21)
except Exception as e:
    print(f"DHT 센서 초기화 오류: {e}")
    dht = None

def authenticate_user(user_id, password):
    """사용자 인증"""
    conn = get_db_connection()  # 수정: 연결 함수 사용
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        sql = "SELECT user_nick FROM user WHERE user_id=%s AND password=%s"
        cursor.execute(sql, (user_id, password))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"사용자 인증 오류: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_latest_temp_humid_data():
    """최신 온습도 데이터 조회"""
    conn = get_db_connection()  # 수정: 연결 함수 사용
    if not conn:
        return {'temp': "DB 연결 오류", 'humid': "DB 연결 오류", 'date': "DB 연결 오류"}
    try:
        cursor = conn.cursor()
        sql = "SELECT temp, humid, date FROM tempHumData ORDER BY date DESC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if result:
            temp, humid, date = result
            return {'temp': temp, 'humid': humid, 'date': date}
        else:
            return {'temp': "데이터없음", 'humid': "데이터없음", 'date': "데이터없음"}
    except Error as e:
        print(f"데이터 조회 오류: {e}")
        return {'temp': "조회 오류", 'humid': "조회 오류", 'date': "조회 오류"}
    finally:
        if conn:
            conn.close()
