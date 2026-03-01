# Raspberry Pi 開発規約

Raspberry Pi OS（Debian ベース）上での Python / C++ 開発ルール。
GPIO・I2C・SPI・UART 等のペリフェラル制御と Linux システム連携を想定。

---

## 基本方針

- **Python 推奨**: GPIO 制御・センサー読み取り・制御ロジックは Python 3
- **C/C++ は速度要件がある場合のみ**: リアルタイム処理・高速ループ
- **systemd で常駐化**: 自動起動は cron よりも systemd service を使う
- **SSH で遠隔開発**: Pi に直接キーボードをつながず SSH + VSCode Remote SSH

---

## Python 環境

### パッケージ管理

```bash
# 仮想環境を作る（pi ユーザーのホームに）
python3 -m venv ~/venv/myproject
source ~/venv/myproject/bin/activate

# 主要ライブラリ
pip install RPi.GPIO          # 低レベル GPIO 制御
pip install gpiozero           # 高レベル GPIO（推奨）
pip install smbus2             # I2C
pip install spidev             # SPI
pip install picamera2          # カメラモジュール（Pi 5 / bullseye+）
pip install adafruit-circuitpython-*  # Adafruit センサー類
```

### GPIO — gpiozero 推奨

```python
from gpiozero import LED, Button, PWMOutputDevice
from signal import pause

# LED 制御
led = LED(17)  # BCM ピン番号
led.on()
led.off()
led.toggle()
led.blink(on_time=0.5, off_time=0.5)

# ボタン（内部プルアップ自動）
button = Button(4, pull_up=True, bounce_time=0.05)
button.when_pressed = lambda: print("Pressed!")
button.when_released = lambda: led.toggle()

# PWM (0.0〜1.0)
motor = PWMOutputDevice(18)
motor.value = 0.75  # 75% デューティ

pause()  # イベントループ維持
```

### GPIO — RPi.GPIO 低レベル（必要な場合）

```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)   # BCM ピン番号を使用
GPIO.setwarnings(False)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(17, GPIO.HIGH)
state = GPIO.input(4)

# 割り込み
def button_callback(channel):
    print(f"Edge detected on channel {channel}")

GPIO.add_event_detect(4, GPIO.FALLING,
                      callback=button_callback,
                      bouncetime=200)

# 必ずクリーンアップ
try:
    while True:
        time.sleep(0.1)
finally:
    GPIO.cleanup()
```

---

## I2C

```python
import smbus2
import struct

bus = smbus2.SMBus(1)  # I2C バス 1 (/dev/i2c-1)
SENSOR_ADDR = 0x48

# 1バイト読み取り
value = bus.read_byte_data(SENSOR_ADDR, 0x00)

# 2バイト読み取り（ビッグエンディアン）
raw = bus.read_i2c_block_data(SENSOR_ADDR, 0x00, 2)
temperature = struct.unpack('>h', bytes(raw))[0] / 256.0

# 書き込み
bus.write_byte_data(SENSOR_ADDR, REG_CONFIG, 0x60)

# 終了時クローズ
bus.close()
```

**事前確認コマンド:**
```bash
# I2C が有効か確認
ls /dev/i2c*

# デバイスアドレスのスキャン
sudo i2cdetect -y 1
```

---

## SPI

```python
import spidev

spi = spidev.SpiDev()
spi.open(0, 0)  # バス0, チップセレクト0 (/dev/spidev0.0)
spi.max_speed_hz = 1_000_000  # 1 MHz
spi.mode = 0b00  # CPOL=0, CPHA=0

# 送受信（同時）
response = spi.xfer2([0x02, 0x00, 0x00])

spi.close()
```

---

## UART（シリアル通信）

```python
import serial

ser = serial.Serial(
    port='/dev/ttyUSB0',   # USB シリアル
    # port='/dev/ttyS0',   # UART0（GPIO 14/15）
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1.0
)

ser.write(b'Hello\r\n')
line = ser.readline().decode('utf-8').strip()
ser.close()
```

---

## systemd サービス化

### サービスファイル例

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Pi Application
After=network.target

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
# 登録・起動・自動起動設定
sudo systemctl daemon-reload
sudo systemctl start myapp
sudo systemctl enable myapp

# 状態確認・ログ
sudo systemctl status myapp
journalctl -u myapp -f
```

---

## SSH 開発フロー

```bash
# Pi の SSH 有効化（初回）
sudo raspi-config  # Interface Options → SSH → Enable

# ホストから接続
ssh pi@raspberrypi.local  # または IP アドレス

# SSH キー認証（パスワードレス）
ssh-copy-id pi@raspberrypi.local

# ファイル転送
scp local_file.py pi@raspberrypi.local:/home/pi/
rsync -avz ./project/ pi@raspberrypi.local:/home/pi/project/

# VSCode Remote SSH
# 拡張機能「Remote - SSH」→ 接続先に pi@raspberrypi.local を追加
```

---

## カメラモジュール（Pi Camera v2 / v3）

```python
from picamera2 import Picamera2
import cv2

picam2 = Picamera2()
config = picam2.create_still_configuration(
    main={"size": (1920, 1080)},
    lores={"size": (640, 480)},
    display="lores"
)
picam2.configure(config)
picam2.start()

# 静止画撮影
picam2.capture_file("photo.jpg")

# NumPy 配列として取得（OpenCV 連携）
frame = picam2.capture_array()
gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

picam2.stop()
```

---

## チェックリスト

### セットアップ
- [ ] `raspi-config` で I2C / SPI / UART / SSH を有効化
- [ ] `/boot/config.txt` でペリフェラル設定済み
- [ ] ユーザーを `gpio`, `i2c`, `spi` グループに追加済み
  - `sudo usermod -aG gpio,i2c,spi pi`
- [ ] 仮想環境を作成してパッケージ管理

### GPIO
- [ ] ピン番号を定数で定義（BCM 番号使用）
- [ ] プログラム終了時に `GPIO.cleanup()` を呼ぶ
- [ ] gpiozero を優先使用（ボイラープレートが少ない）

### 常駐アプリ
- [ ] systemd service ファイルを作成
- [ ] `Restart=on-failure` でクラッシュ時自動再起動
- [ ] ログを `journalctl` で確認できる状態
