from flask import Flask, request, render_template, url_for, session, redirect, jsonify
import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import mysql.connector
import atexit
from mysql.connector import Error
from function import get_db_connection

app = Flask(__name__)
app.secret_key = 'test_1234'  # 세션을 위한 시크릿 키 추가


@app.route('/')
def mainlogin():
    return render_template("login.html")


# 로그아웃 라우트 추가
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_page'))
try:
    dht_device = adafruit_dht.DHT11(board.D21)
    print("DHT 센서 초기화 성공")
except Exception as e:
    print(f"DHT 센서 초기화 실패: {e}")
    dht_device = None
    

if __name__ == "__main__":
    try:
        from main import *
        app.run(host="0.0.0.0", port=7777)  
    except KeyboardInterrupt:
        print("서버 종료 중...")