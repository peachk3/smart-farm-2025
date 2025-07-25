 function measure() {
    // // 버튼 비활성화 및 로딩 표시
    // const measureBtn = event.target;
    // measureBtn.disabled = true;
    // measureBtn.textContent = '측정 중...';
    // document.getElementById("result").innerHTML = "🔄 측정 중...";           
    fetch("/measure", {
            method: "POST"
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                var today = new Date();
                var year = today.getFullYear();
                var month = ('0' + (today.getMonth() + 1)).slice(-2);
                var day =  ('0' + today.getDate()).slice(-2);
                var hours = ('0' + today.getHours()).slice(-2);
                var mins = ('0' + today.getMinutes()).slice(-2);
                var seconds = ('0' + today.getSeconds()).slice(-2);
                var dateTimeString = year + '-' + month + '-' + day + ' ' + hours + ':' + mins + ':' + seconds;
                document.getElementById("measure-result").innerHTML = `
                🌡 온도: ${data.temperature}℃ <br>
                💧 습도: ${data.humidity}% <br>
                📅 측정 시간: ${dateTimeString}
                `;
            } else {
                document.getElementById("measure-result").innerHTML = `
                ❌ 측정 실패: ${data.error}
                `;
            }
        })
        .catch(err => {
            document.getElementById("measure-result").innerHTML =
                "❌ 요청 중 오류 발생: " + err;
        })
        .finally(() => {
            // 버튼 다시 활성화
            measureBtn.disabled = false;
            measureBtn.textContent = '📥 측정';
        });
    }

    // LED 제어를 AJAX로 변경 (페이지 새로고침 방지)
    function toggleLED() {
    const ledBtn = event.target;
    ledBtn.disabled = true;

    fetch("/ledControl", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                ledBtn.textContent = data.button_text || 'LED 제어';
                document.getElementById("led-status").textContent = data.led_state ? 'ON' : 'OFF';
            } else {
                alert('LED 제어 실패');
            }
        })
        .catch(err => {
            console.error('LED 제어 오류:', err);
            // 오류 시 페이지 새로고침으로 폴백
            window.location.reload();
        })
        .finally(() => {
            ledBtn.disabled = false;
        });
    }
    function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
    });
    const day = String(now.getDate());
    const month = now.toLocaleDateString('en-US', {month: 'long'});
    const formattedDate = `${day} ${month}`;
    document.getElementById("time-text").textContent = timeString;
    document.getElementById("current-date").textContent = `${formattedDate}`;
}

// 1초마다 업데이트
setInterval(updateTime, 1000);
updateTime();  // 처음 한 번 즉시 실행