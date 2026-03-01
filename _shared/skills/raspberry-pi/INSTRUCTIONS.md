# Raspberry Pi 開発ガイド — 実装パターン集

GPIO 制御・センサー通信・カメラ・システム常駐化まで、
Raspberry Pi でよく使うパターンを網羅。

---

## 初期セットアップ

### raspi-config でペリフェラルを有効化

```bash
sudo raspi-config
# Interface Options → 各ペリフェラルを Enable
# - I2C
# - SPI
# - Serial Port（UART ログイン無効 / ハードウェア UART 有効）
# - SSH
# - Camera（Pi Camera v1/v2、bullseye 以降は不要）
```

### ユーザーをグループに追加

```bash
sudo usermod -aG gpio,i2c,spi,dialout pi
# 変更反映のため再ログイン
```

### ペリフェラル確認

```bash
ls /dev/i2c*      # → /dev/i2c-1
ls /dev/spidev*   # → /dev/spidev0.0
ls /dev/ttyS*     # → /dev/ttyS0 (UART)
sudo i2cdetect -y 1   # I2C デバイスのアドレス一覧
```

---

## GPIO 制御

### gpiozero（推奨・高レベル）

```python
from gpiozero import LED, Button, PWMOutputDevice, DistanceSensor
from signal import pause

# LED
led = LED(17)          # BCM ピン番号
led.on()
led.blink(on_time=0.5, off_time=0.5)

# ボタン（内部プルアップ付き）
button = Button(4, bounce_time=0.05)
button.when_pressed  = led.on
button.when_released = led.off

# PWM（サーボ・モーター等）
motor = PWMOutputDevice(18, frequency=50)
motor.value = 0.75  # 75% デューティ

# 超音波センサー（HC-SR04）
sensor = DistanceSensor(echo=24, trigger=23)
print(f"Distance: {sensor.distance * 100:.1f} cm")

pause()  # イベントループ（Ctrl+C で終了）
```

### RPi.GPIO（低レベル制御が必要な場合）

```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PIN_LED    = 17
PIN_BUTTON = 4

GPIO.setup(PIN_LED, GPIO.OUT)
GPIO.setup(PIN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 割り込みで検出
def on_button(channel):
    state = GPIO.input(PIN_LED)
    GPIO.output(PIN_LED, not state)

GPIO.add_event_detect(PIN_BUTTON, GPIO.FALLING,
                      callback=on_button, bouncetime=200)

try:
    while True:
        time.sleep(0.1)
finally:
    GPIO.cleanup()   # 必須：GPIOをリセット
```

---

## I2C センサー

```python
import smbus2
import struct
import time

bus = smbus2.SMBus(1)  # /dev/i2c-1

# ---- BME280 温湿度センサーの例 ----
BME280_ADDR    = 0x76
REG_CHIP_ID    = 0xD0
REG_RESET      = 0xE0
REG_CTRL_MEAS  = 0xF4
REG_PRESS_MSB  = 0xF7

# デバイス確認
chip_id = bus.read_byte_data(BME280_ADDR, REG_CHIP_ID)
print(f"Chip ID: 0x{chip_id:02X}")  # → 0x60

# 設定レジスタ書き込み
bus.write_byte_data(BME280_ADDR, REG_CTRL_MEAS, 0x27)

# 複数バイト読み取り
data = bus.read_i2c_block_data(BME280_ADDR, REG_PRESS_MSB, 8)
raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
raw_temp  = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

bus.close()
```

---

## SPI デバイス

```python
import spidev

spi = spidev.SpiDev()
spi.open(0, 0)               # SPI bus 0, CS 0
spi.max_speed_hz = 1_000_000
spi.mode = 0b00              # CPOL=0, CPHA=0

# MCP3008 ADC（10bit、8ch）の例
def read_adc(channel: int) -> int:
    """チャンネル 0-7 の ADC 値を返す"""
    assert 0 <= channel <= 7
    cmd = [1, (8 + channel) << 4, 0]
    result = spi.xfer2(cmd)
    return ((result[1] & 3) << 8) | result[2]

voltage = read_adc(0) * 3.3 / 1023
print(f"ADC ch0: {voltage:.3f} V")

spi.close()
```

---

## UART（シリアル通信）

```python
import serial
import time

# デバイスパス: USB シリアルなら /dev/ttyUSB0、ハードウェアUARTなら /dev/ttyS0
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    timeout=1.0
)

# 送信
ser.write(b'AT\r\n')

# 受信（1行）
response = ser.readline().decode('utf-8').strip()
print(f"Response: {response}")

# 受信（バイト数指定）
data = ser.read(4)

ser.close()
```

---

## カメラモジュール（picamera2）

```python
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import cv2
import time

picam2 = Picamera2()

# 静止画設定
still_cfg = picam2.create_still_configuration(
    main={"size": (1920, 1080), "format": "RGB888"}
)
picam2.configure(still_cfg)
picam2.start()
time.sleep(1)  # センサー安定待ち

# 撮影 → ファイル保存
picam2.capture_file("photo.jpg")

# NumPy 配列として取得（OpenCV 連携）
frame = picam2.capture_array()           # RGB
bgr   = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
cv2.imwrite("photo_cv.jpg", bgr)

picam2.stop()
```

### 動画ストリーミング（Flask + MJPEG）

```python
from picamera2 import Picamera2
from flask import Flask, Response
import io

app = Flask(__name__)
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"size": (640, 480)}
))
picam2.start()

def generate_frames():
    while True:
        buf = io.BytesIO()
        picam2.capture_file(buf, format='jpeg')
        frame = buf.getvalue()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
               + frame + b'\r\n')

@app.route('/video')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

---

## systemd サービス化

```bash
# /etc/systemd/system/myapp.service を作成
sudo nano /etc/systemd/system/myapp.service
```

```ini
[Unit]
Description=My Raspberry Pi App
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/myapp
ExecStart=/home/pi/venv/myproject/bin/python main.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# 登録・起動
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp

# 状態確認・ログ
sudo systemctl status myapp
journalctl -u myapp -f --lines=50
```

---

## SSH リモート開発

```bash
# Pi への SSH 接続
ssh pi@raspberrypi.local    # mDNS で解決
ssh pi@192.168.1.xxx        # IP 直接

# SSH キー設定（パスワードレス）
ssh-copy-id pi@raspberrypi.local

# ファイル同期（rsync で差分転送）
rsync -avz --exclude='__pycache__' \
    ./project/ pi@raspberrypi.local:/home/pi/project/

# リモートでコマンド実行
ssh pi@raspberrypi.local 'sudo systemctl restart myapp'

# ポートフォワード（Flask を localhost で確認）
ssh -L 8080:localhost:8080 pi@raspberrypi.local
```

---

## よくあるトラブル

| 症状 | 原因 | 対処 |
|------|------|------|
| `GPIO.cleanup()` を忘れた | 前回の GPIO 設定が残っている | `GPIO.cleanup()` を finally で必ず呼ぶ |
| `FileNotFoundError: /dev/i2c-1` | I2C が無効 | `raspi-config` で I2C を有効化 |
| I2C で `0x00` しかスキャンされない | 配線ミス / プルアップ不足 | SDA/SCL の配線と 4.7kΩ プルアップ抵抗を確認 |
| カメラ `permission denied` | pi ユーザーの権限不足 | `sudo usermod -aG video pi` |
| UART で文字化け | ボーレート不一致 | 両端のボーレートを合わせる |
| `systemctl start` で失敗 | Python パス誤り | `ExecStart` に仮想環境の python パスを書く |

---

## よくある実装チェックリスト

- [ ] `raspi-config` で I2C / SPI / UART / SSH を有効化済み
- [ ] `usermod -aG gpio,i2c,spi pi` でグループ設定済み
- [ ] GPIO ピン番号を定数で定義（BCM 番号）
- [ ] `GPIO.cleanup()` を `finally` ブロックで呼んでいる
- [ ] 長時間動作は systemd service で管理
- [ ] SSH キー認証を設定してパスワードレスアクセス
