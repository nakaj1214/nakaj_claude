# ESP32 開発ガイド — 実装パターン集

PlatformIO + Arduino フレームワークを基本とした ESP32 開発パターン。
WiFi・FreeRTOS・省電力・OTA・ファイルシステムを網羅。

---

## PlatformIO プロジェクトセットアップ

### 新規プロジェクト作成

```bash
# PlatformIO CLI でプロジェクト作成
pio project init --board esp32dev --ide vscode

# または VSCode の PlatformIO 拡張からウィザードで作成
# Home → New Project → Board: Espressif ESP32 Dev Module
```

### platformio.ini 設定例

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
upload_speed = 921600

lib_deps =
    bblanchon/ArduinoJson @ ^7.0.0
    knolleary/PubSubClient @ ^2.8.0
    adafruit/Adafruit_BME280_Library @ ^2.2.4

build_flags =
    -DCORE_DEBUG_LEVEL=3

; リリース用（ログ無効化）
[env:release]
extends = env:esp32dev
build_flags = -DCORE_DEBUG_LEVEL=0

; ESP32-S3 の場合
[env:esp32s3]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
```

### よく使う PlatformIO コマンド

```bash
pio run                    # ビルド
pio run --target upload    # ビルド + 書き込み
pio device monitor         # シリアルモニター（Ctrl+C で終了）
pio run --target clean     # ビルドキャッシュ削除
pio lib search "ArduinoJson"  # ライブラリ検索
```

---

## プロジェクト構成

```
project/
├── platformio.ini
├── include/
│   └── config.h          # ピン定義・定数・WiFi 設定
├── src/
│   ├── main.cpp          # setup() / loop()
│   ├── wifi_manager.cpp  # WiFi 接続ロジック
│   └── sensor.cpp        # センサー読み取り
└── lib/
    └── MyLib/            # プロジェクト固有ライブラリ
```

### config.h テンプレート

```cpp
// include/config.h
#pragma once

// ピン定義（GPIO 番号）
constexpr uint8_t PIN_LED        = 2;
constexpr uint8_t PIN_BUTTON     = 4;
constexpr uint8_t PIN_ADC        = 34;   // 入力専用
constexpr uint8_t PIN_I2C_SDA    = 21;
constexpr uint8_t PIN_I2C_SCL    = 22;

// 設定値
constexpr uint32_t BAUD_RATE     = 115200;
constexpr uint32_t SLEEP_US      = 60ULL * 1000000ULL;  // 60秒

// WiFi / API キーは secrets.h に分離
// #include "secrets.h"  → .gitignore に追加すること
```

---

## WiFi 接続

### 基本的な接続パターン

```cpp
#include <WiFi.h>

const char* SSID     = "your_ssid";   // 本番は secrets.h から
const char* PASSWORD = "your_pass";

bool connectWiFi(uint32_t timeout_ms = 15000) {
    WiFi.mode(WIFI_STA);
    WiFi.begin(SSID, PASSWORD);
    Serial.print("Connecting to WiFi");

    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if ((uint32_t)(millis() - start) > timeout_ms) {
            Serial.println("\nTimeout!");
            return false;
        }
        delay(500);
        Serial.print(".");
    }
    Serial.printf("\nConnected! IP: %s\n", WiFi.localIP().toString().c_str());
    return true;
}

// 再接続チェック（loop() で呼ぶ）
void maintainWiFi() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi lost, reconnecting...");
        WiFi.reconnect();
    }
}
```

### HTTPS GET リクエスト

```cpp
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

String httpGet(const char* url) {
    WiFiClientSecure client;
    client.setInsecure();  // 本番では証明書検証を行う
    HTTPClient http;

    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");
    int code = http.GET();

    String body = "";
    if (code == HTTP_CODE_OK) {
        body = http.getString();
    } else {
        Serial.printf("HTTP error: %d\n", code);
    }
    http.end();
    return body;
}
```

---

## FreeRTOS タスク

### 基本パターン（loop() の代替）

```cpp
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>

QueueHandle_t dataQueue;

// センサー読み取りタスク（コア 0 推奨）
void sensorTask(void* pvParameters) {
    const TickType_t delay = pdMS_TO_TICKS(100);
    while (true) {
        float value = analogRead(PIN_ADC) * 3.3f / 4095.0f;
        xQueueSend(dataQueue, &value, 0);  // 0 = キュー満杯でも待たない
        vTaskDelay(delay);
    }
}

// 表示タスク（コア 1）
void displayTask(void* pvParameters) {
    float value;
    while (true) {
        if (xQueueReceive(dataQueue, &value, portMAX_DELAY) == pdTRUE) {
            Serial.printf("Voltage: %.3f V\n", value);
        }
    }
}

void setup() {
    Serial.begin(BAUD_RATE);
    dataQueue = xQueueCreate(10, sizeof(float));

    xTaskCreatePinnedToCore(sensorTask,  "Sensor",  4096, nullptr, 1, nullptr, 0);
    xTaskCreatePinnedToCore(displayTask, "Display", 4096, nullptr, 1, nullptr, 1);
}

void loop() {
    vTaskDelay(portMAX_DELAY);  // loop() は空にする
}
```

### ミューテックスで共有リソース保護

```cpp
SemaphoreHandle_t i2cMutex;

void setup() {
    i2cMutex = xSemaphoreCreateMutex();
}

void safeI2CRead(void* arg) {
    while (true) {
        if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            // I2C 通信（排他制御済み）
            readSensor();
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

// 設定: 60秒後にタイマーウェイクアップ
void goDeepSleep(uint64_t seconds = 60) {
    esp_sleep_enable_timer_wakeup(seconds * 1000000ULL);
    Serial.println("Entering deep sleep...");
    Serial.flush();
    esp_deep_sleep_start();
}

// GPIO でウェイクアップ（ボタン等）
void enableGpioWakeup() {
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_BUTTON, LOW);
}

// ウェイクアップ理由の確認
void checkWakeupCause() {
    switch (esp_sleep_get_wakeup_cause()) {
        case ESP_SLEEP_WAKEUP_TIMER:  Serial.println("Timer wakeup"); break;
        case ESP_SLEEP_WAKEUP_EXT0:   Serial.println("GPIO wakeup");  break;
        default:                       Serial.println("Power on / Reset"); break;
    }
}

// センサーデバイスの典型フロー
void setup() {
    Serial.begin(BAUD_RATE);
    checkWakeupCause();

    if (connectWiFi()) {
        float temp = readSensor();
        postToServer(temp);
        WiFi.disconnect(true);
    }
    goDeepSleep(60);  // 60秒後に再実行
}
```

---

## NVS（フラッシュへの設定保存）

```cpp
#include <Preferences.h>

Preferences prefs;

// 書き込み
void saveConfig(const String& ssid, const String& token) {
    prefs.begin("app", false);  // 名前空間 "app", 読み書きモード
    prefs.putString("ssid", ssid);
    prefs.putString("token", token);
    prefs.putUInt("count", prefs.getUInt("count", 0) + 1);
    prefs.end();
}

// 読み取り
String loadSSID() {
    prefs.begin("app", true);  // 読み取り専用
    String ssid = prefs.getString("ssid", "default_ssid");
    prefs.end();
    return ssid;
}

// NVS 初期化（初回のみ）
void initNVS() {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }
}
```

---

## OTA アップデート

```cpp
#include <ArduinoOTA.h>

void setupOTA(const char* hostname = "esp32") {
    ArduinoOTA.setHostname(hostname);
    // ArduinoOTA.setPassword("secret");  // パスワード設定（推奨）

    ArduinoOTA.onStart([]() {
        Serial.println("OTA Start: " +
            String(ArduinoOTA.getCommand() == U_FLASH ? "Sketch" : "Filesystem"));
    });
    ArduinoOTA.onEnd([]() {
        Serial.println("\nOTA End");
    });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("OTA Error[%u]\n", error);
    });
    ArduinoOTA.begin();
}

void loop() {
    ArduinoOTA.handle();  // 必ず毎ループ呼ぶ
}
```

---

## LittleFS（フラッシュファイルシステム）

```cpp
#include <LittleFS.h>
#include <ArduinoJson.h>

void initFS() {
    if (!LittleFS.begin(true)) {  // true = フォーマット on failure
        Serial.println("LittleFS mount failed");
    }
}

// JSON 設定ファイルの読み書き
bool saveConfig(float interval, const String& server) {
    File f = LittleFS.open("/config.json", "w");
    if (!f) return false;

    JsonDocument doc;
    doc["interval"] = interval;
    doc["server"] = server;
    serializeJson(doc, f);
    f.close();
    return true;
}

bool loadConfig(float& interval, String& server) {
    File f = LittleFS.open("/config.json", "r");
    if (!f) return false;

    JsonDocument doc;
    if (deserializeJson(doc, f)) { f.close(); return false; }
    interval = doc["interval"] | 60.0f;
    server   = doc["server"].as<String>();
    f.close();
    return true;
}
```

---

## シリアルデバッグ

```cpp
// ESP_LOGx（ESP-IDF スタイル、推奨）
#include "esp_log.h"
static const char* TAG = "MAIN";

ESP_LOGI(TAG, "Start. Free heap: %lu bytes", esp_get_free_heap_size());
ESP_LOGW(TAG, "Low battery: %.2f V", voltage);
ESP_LOGE(TAG, "Sensor timeout after %d ms", timeout_ms);

// CORE_DEBUG_LEVEL=3 以上でデバッグログ表示
ESP_LOGD(TAG, "Raw ADC: %d", raw);

// 条件コンパイルでデバッグ出力制御
#ifdef DEBUG
  Serial.printf("[DEBUG] heap: %lu\n", esp_get_free_heap_size());
#endif
```

---

## よくあるトラブル

| 症状 | 原因 | 対処 |
|------|------|------|
| 書き込みに失敗する | BOOT ボタンを押していない | 書き込み中に BOOT ボタンを押し続ける |
| リセットループ | WDT タイムアウト / スタックオーバーフロー | タスクスタックサイズを増やす / WDT リセット追加 |
| WiFi に繋がらない | 5GHz には繋がらない | ESP32 は 2.4GHz のみ対応 |
| ディープスリープから復帰しない | ウェイクアップ設定忘れ | `esp_sleep_enable_*_wakeup()` を sleep 前に設定 |
| NVS エラー | フラッシュ破損 | `nvs_flash_erase()` してから再初期化 |
| ヒープ不足でクラッシュ | 動的割り当て多用 | `esp_get_free_heap_size()` で確認、静的バッファに変更 |

---

## 実装チェックリスト

- [ ] `include/config.h` にピン番号・定数を集約
- [ ] WiFi パスワード・API キーは `secrets.h` に分離（.gitignore に追加）
- [ ] `delay()` を使わず `vTaskDelay()` または非ブロッキングタイマー
- [ ] 割り込みハンドラーに `IRAM_ATTR` を付与
- [ ] 割り込みから参照する変数に `volatile` を付与
- [ ] リリースビルドで `CORE_DEBUG_LEVEL=0` に設定
- [ ] ディープスリープ前に `Serial.flush()` で出力を待つ
- [ ] LittleFS は `begin(true)` でフォーマット on failure を設定
