# ESP32 開発規約

ESP32 / ESP32-S3 / ESP32-C3 向けの開発ルール。
PlatformIO + Arduino フレームワーク を基本とし、ESP-IDF 固有機能も扱う。

---

## 基本方針

- **PlatformIO を使う**（Arduino IDE より管理しやすい）
- **Arduino フレームワーク**が基本。低レベル制御が必要なら ESP-IDF API を混在使用
- **FreeRTOS タスク**で並行処理（loop() に全部書かない）
- **シリアルモニター**でデバッグ（Serial.printf / ESP_LOGx）
- **ディープスリープ**で省電力設計

---

## PlatformIO プロジェクト構成

```
project/
├── platformio.ini        # ビルド設定
├── src/
│   └── main.cpp          # エントリーポイント
├── include/
│   └── config.h          # ピン定義・定数
├── lib/                  # ローカルライブラリ
└── test/                 # ユニットテスト（Unity）
```

### platformio.ini の基本設定

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
upload_speed = 921600

; ライブラリ依存関係
lib_deps =
    bblanchon/ArduinoJson @ ^7.0.0
    knolleary/PubSubClient @ ^2.8
    adafruit/Adafruit_BME280_Library @ ^2.2.0

; ビルドフラグ
build_flags =
    -DCORE_DEBUG_LEVEL=3    ; デバッグログレベル（0〜5）
    -DCONFIG_FREERTOS_HZ=1000

[env:release]
extends = env:esp32dev
build_flags =
    -DCORE_DEBUG_LEVEL=0
```

---

## ピン定義とヘッダー

```cpp
// include/config.h
#pragma once

// ピン定義（BCM ではなく GPIO 番号）
constexpr uint8_t PIN_LED         = 2;
constexpr uint8_t PIN_BUTTON      = 4;
constexpr uint8_t PIN_ADC_SENSOR  = 34;  // 入力専用ピン
constexpr uint8_t PIN_I2C_SDA     = 21;
constexpr uint8_t PIN_I2C_SCL     = 22;
constexpr uint8_t PIN_SPI_MOSI    = 23;
constexpr uint8_t PIN_SPI_MISO    = 19;
constexpr uint8_t PIN_SPI_CLK     = 18;
constexpr uint8_t PIN_SPI_CS      = 5;

// 設定定数
constexpr uint32_t BAUD_RATE      = 115200;
constexpr uint32_t WIFI_TIMEOUT_MS = 10000;
constexpr uint32_t MQTT_PORT      = 1883;
```

---

## WiFi 接続

```cpp
#include <WiFi.h>

const char* WIFI_SSID = "your_ssid";       // 本番は NVS や secrets.h から読む
const char* WIFI_PASS = "your_password";

bool connectWifi(uint32_t timeout_ms = 10000) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting to WiFi");

    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > timeout_ms) {
            Serial.println("\nWiFi timeout!");
            return false;
        }
        delay(500);
        Serial.print(".");
    }
    Serial.printf("\nConnected: %s\n", WiFi.localIP().toString().c_str());
    return true;
}
```

---

## FreeRTOS タスク

### 基本パターン（loop() の代替）

```cpp
// タスク定義
void sensorTask(void* pvParameters) {
    const TickType_t xDelay = pdMS_TO_TICKS(100);  // 100ms 周期

    while (true) {
        float temp = readTemperature();
        // キューに送信
        xQueueSend(dataQueue, &temp, portMAX_DELAY);
        vTaskDelay(xDelay);
    }
}

void displayTask(void* pvParameters) {
    float temp;
    while (true) {
        if (xQueueReceive(dataQueue, &temp, portMAX_DELAY) == pdTRUE) {
            updateDisplay(temp);
        }
    }
}

// setup() でタスク生成
QueueHandle_t dataQueue;

void setup() {
    dataQueue = xQueueCreate(10, sizeof(float));

    // コア0 でセンサー読み取り（WiFi はコア0 が推奨）
    xTaskCreatePinnedToCore(sensorTask, "SensorTask",
                            4096, nullptr, 1, nullptr, 0);
    // コア1 で表示更新
    xTaskCreatePinnedToCore(displayTask, "DisplayTask",
                            4096, nullptr, 1, nullptr, 1);
}

void loop() {
    // FreeRTOS タスクを使う場合は loop() を空にする
    vTaskDelay(portMAX_DELAY);
}
```

### セマフォ・ミューテックス（共有リソース保護）

```cpp
SemaphoreHandle_t i2cMutex;

void setup() {
    i2cMutex = xSemaphoreCreateMutex();
}

void taskA(void* arg) {
    while (true) {
        if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            // I2C 通信（排他制御）
            readI2CSensor();
            xSemaphoreGive(i2cMutex);
        }
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
```

---

## ディープスリープ（省電力）

```cpp
#include "esp_sleep.h"

// タイマーウェイクアップ（60秒後）
void goDeepSleep(uint64_t sleep_us = 60ULL * 1000000ULL) {
    esp_sleep_enable_timer_wakeup(sleep_us);
    Serial.println("Going to deep sleep...");
    Serial.flush();
    esp_deep_sleep_start();
}

// GPIO ウェイクアップ（ボタン押下）
void enableGpioWakeup() {
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_BUTTON, LOW);
}

// ウェイクアップ原因の確認
void checkWakeupReason() {
    esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();
    switch (cause) {
        case ESP_SLEEP_WAKEUP_TIMER:   Serial.println("Timer wakeup"); break;
        case ESP_SLEEP_WAKEUP_EXT0:    Serial.println("GPIO wakeup");  break;
        default:                        Serial.println("Reset");        break;
    }
}
```

---

## NVS（フラッシュに設定を保存）

```cpp
#include <Preferences.h>

Preferences prefs;

// 書き込み
void saveSettings(const char* ssid, const char* pass) {
    prefs.begin("wifi", false);  // "wifi" 名前空間, 読み書きモード
    prefs.putString("ssid", ssid);
    prefs.putString("pass", pass);
    prefs.end();
}

// 読み取り
String loadSSID() {
    prefs.begin("wifi", true);  // 読み取り専用
    String ssid = prefs.getString("ssid", "");  // デフォルト値 ""
    prefs.end();
    return ssid;
}
```

---

## OTA アップデート

```cpp
#include <ArduinoOTA.h>

void setupOTA(const char* hostname = "esp32") {
    ArduinoOTA.setHostname(hostname);
    ArduinoOTA.setPassword("ota_password");  // 本番ではハードコードしない

    ArduinoOTA.onStart([]() {
        Serial.println("OTA Start");
    });
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("OTA Error[%u]\n", error);
    });
    ArduinoOTA.begin();
}

void loop() {
    ArduinoOTA.handle();  // loop() で必ず呼ぶ
    // ...
}
```

---

## フラッシュファイルシステム（LittleFS）

```cpp
#include <LittleFS.h>

void setup() {
    if (!LittleFS.begin(true)) {  // true = フォーマット on fail
        Serial.println("LittleFS mount failed");
        return;
    }

    // ファイル書き込み
    File f = LittleFS.open("/config.json", "w");
    f.println("{\"interval\": 60}");
    f.close();

    // ファイル読み取り
    File r = LittleFS.open("/config.json", "r");
    String content = r.readString();
    r.close();
}
```

---

## チェックリスト

### プロジェクト設定
- [ ] `platformio.ini` でボードとフレームワークを明示
- [ ] `include/config.h` にピン番号・定数を集約
- [ ] WiFi パスワード・API キーをコードに直書きしない（NVS か secrets.h + .gitignore）

### コーディング
- [ ] `delay()` をメインループ・タスクで多用しない（`vTaskDelay` を使う）
- [ ] 割り込みハンドラーには `IRAM_ATTR` を付ける
- [ ] 割り込みから変更する変数に `volatile` を付ける
- [ ] 共有リソースをミューテックスで保護

### デバッグ
- [ ] `Serial.printf` または `ESP_LOGx` でデバッグ出力
- [ ] リリースビルドで `CORE_DEBUG_LEVEL=0` に設定
- [ ] `pio run --target monitor` でシリアルモニター確認

### 省電力（バッテリー駆動の場合）
- [ ] ディープスリープを実装（センサーデバイス等）
- [ ] WiFi を使わないときは `WiFi.disconnect(true)` で切断
- [ ] CPU クロックを下げる（`setCpuFrequencyMhz(80)`）
