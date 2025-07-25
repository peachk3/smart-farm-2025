from flask import Flask, request, render_template, url_for, session, redirect, jsonify
import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import mysql.connector
import atexit
from mysql.connector import Error
from function import authenticate_user
from function import get_latest_temp_humid_data
from function import init_gpio
from function import normal_alarm
from function import trigger_alarm
from function import get_db_connection
from function import dht
from function import LED_PINS
from login import app

# GPIO 초기화 실행
gpio_initialized = init_gpio()
BUZZER = 18

led_state = False  # 초기값 설정 (LED 꺼짐 상태)

@app.route('/login', methods=['POST'])
def main():
    global led_state
    # GPIO 초기화 실행

    user_id = request.form['id']
    password = request.form['pw']

    # 사용자 인증
    user = authenticate_user(user_id, password)
    
    if user:
        user_nick = user[0]
        # 메인 페이지로 리다이렉트하여 중복 코드 제거
        # session['logged_in'] = True 
        session['user_nick'] = user_nick  # 세션에 사용자 정보 저장
        return redirect(url_for('main_page'))
    else:
        state = "LOGIN FAIL. TRY AGAIN"
        return render_template("index.html", state=state)


@app.route('/main')
def main_page():
    if 'user_nick' not in session:
        return redirect(url_for('mainlogin'))

    user_nick = session['user_nick']
        # 예시 - 실제 API를 통해 받아오는 것이 일반적
    weather_info = "☀️ 30℃ "  # 또는 API 결과값 가공해서 넣기
    # ✅ 온습도 자동 측정
    if dht:
        try:
            temperature = dht.temperature
            humidity = dht.humidity
            
            if temperature is not None and humidity is not None:
                print(f"[자동측정] Temp: {temperature}°C, Humi: {humidity}%")

                # 알람 조건 처리
                if 18 <= temperature <= 20:
                    normal_alarm()
                if temperature >= 21 and humidity > 80:
                    trigger_alarm()

                # DB 저장
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    sql = "INSERT INTO tempHumData (temp, humid) VALUES (%s, %s)"
                    cursor.execute(sql, (temperature, humidity))
                    conn.commit()
                    cursor.close()
                    conn.close()
        except Exception as e:
            print(f"[자동측정 오류] {e}")

    # 📋 최신값 불러오기
    temp_data = get_latest_temp_humid_data()
    button_text = "OFF" if led_state else "ON"

    return render_template("main.html", 
        temp=temp_data['temp'], 
        humid=temp_data['humid'], 
        date=temp_data['date'],
        user_nick=user_nick, 
        button_text=button_text, 
        led_state=led_state,
        weather_info=weather_info,
        login_form=False)

@app.route("/ledControl", methods=['POST'])
def led_control():
    global led_state
    
    # 로그인 체크
    if 'user_nick' not in session:
        return redirect(url_for('mainlogin'))
    
    # GPIO 초기화 체크
    if not gpio_initialized:
        error_msg = "GPIO가 초기화되지 않았습니다"
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'success': False, 'error': error_msg}), 500
        else:
            return redirect(url_for('main_page'))
    
    try:
        # LED 상태 토글
        led_state = not led_state
        if led_state:
            # 흰색 켜기
            GPIO.output(BUZZER, True)
            GPIO.output(LED_PINS["red"], GPIO.HIGH)
            GPIO.output(LED_PINS["green"], GPIO.HIGH)
            GPIO.output(LED_PINS["blue"], GPIO.HIGH)
        else:
            # 모두 끄기
            GPIO.output(BUZZER, False)
            GPIO.output(LED_PINS["red"], GPIO.LOW)
            GPIO.output(LED_PINS["green"], GPIO.LOW)
            GPIO.output(LED_PINS["blue"], GPIO.LOW)

        print(f"LED 상태: {'ON' if led_state else 'OFF'}")
        
        # AJAX 요청인지 확인
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            # AJAX 응답: JSON으로 상태만 반환
            return jsonify({
                'success': True,
                'led_state': led_state,
                'button_text': 'OFF' if led_state else 'ON'
            })
        else:
            # 일반 폼 요청: 메인 페이지로 리다이렉트
            return redirect(url_for('main_page'))
            
    except Exception as e:
        print(f"LED 제어 오류: {e}")
        
        if request.headers.get('Content-Type') == 'application/json' or request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            # 오류 시에도 메인 페이지로 돌아가기
            return redirect(url_for('main_page'))
        

