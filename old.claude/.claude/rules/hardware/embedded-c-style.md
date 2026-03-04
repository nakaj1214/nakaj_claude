# 組み込み C/C++ コーディングスタイル

Raspberry Pi / ESP32 など組み込みデバイス向けの C/C++ コーディングルール。
リソース制約・ハードウェア依存・リアルタイム要件を考慮した実践指針。

---

## 型・定数

### stdint.h の型を使う（サイズ明示）

```c
// ✅ Good: サイズが明確
uint8_t  pin_state;
uint16_t adc_value;
uint32_t timestamp_ms;
int16_t  temperature;

// ❌ Bad: プラットフォームで変わる
int pin_state;
unsigned int adc_value;
long timestamp;
```

### マジックナンバーを定数化する

```c
// ✅ Good
#define LED_PIN         2
#define BAUD_RATE       115200
#define ADC_MAX_VALUE   4095   // ESP32 12bit ADC
#define SAMPLE_RATE_HZ  100

static const uint16_t SENSOR_TIMEOUT_MS = 5000;

// ❌ Bad
if (adc_value > 4095) { ... }
delay(5000);
```

---

## メモリ管理

### 動的メモリ割り当てを避ける

```c
// ✅ Good: スタック・静的領域を使う
static uint8_t rx_buffer[256];
uint8_t local_buf[64];

// ❌ Bad: ヒープ断片化・メモリリークリスク（特にマイコン）
uint8_t* buf = malloc(256);
// ... free() を忘れると詰む
```

### バッファサイズに余裕を持つ

```c
#define RX_BUFFER_SIZE  256

static uint8_t rx_buf[RX_BUFFER_SIZE];
static uint16_t rx_head = 0;
static uint16_t rx_tail = 0;

// バッファ満杯チェック
bool is_buffer_full(void) {
    return ((rx_head + 1) % RX_BUFFER_SIZE) == rx_tail;
}
```

---

## volatile と割り込み

### 割り込みから変更される変数には `volatile` を付ける

```c
// ✅ Good: 割り込み内でセットされるフラグ
static volatile bool data_ready = false;
static volatile uint16_t encoder_count = 0;

void IRAM_ATTR gpio_isr_handler(void* arg) {  // ESP32: IRAM_ATTR 必須
    data_ready = true;
    encoder_count++;
}

// メインループ
void loop() {
    if (data_ready) {
        data_ready = false;  // クリアしてから処理
        process_data();
    }
}
```

### 割り込みハンドラーは短く保つ

```c
// ✅ Good: フラグだけ立てる
static volatile bool button_pressed = false;

void IRAM_ATTR button_isr(void* arg) {
    button_pressed = true;
    // ここで重い処理をしない！
}

// ❌ Bad: ISR 内でシリアル出力・遅延
void button_isr_bad(void* arg) {
    Serial.println("Button!");  // ISR 内で Serial は危険
    delay(50);                  // 絶対NG
}
```

---

## ペリフェラル・GPIO

### ピン番号は定数で定義する

```c
// ✅ Good: 一箇所で管理
#define PIN_LED         2
#define PIN_BUTTON      4
#define PIN_SENSOR_SDA  21
#define PIN_SENSOR_SCL  22
#define PIN_CS_SD       5

// ❌ Bad: 直書き（変更時に全箇所修正が必要）
digitalWrite(2, HIGH);
```

### 初期化関数をペリフェラル別に分ける

```c
void init_gpio(void) {
    pinMode(PIN_LED, OUTPUT);
    pinMode(PIN_BUTTON, INPUT_PULLUP);
    digitalWrite(PIN_LED, LOW);
}

void init_i2c(void) {
    Wire.begin(PIN_SDA, PIN_SCL);
    Wire.setClock(400000);  // 400kHz Fast Mode
}

void init_uart(void) {
    Serial.begin(BAUD_RATE);
    Serial2.begin(9600, SERIAL_8N1, PIN_RX2, PIN_TX2);
}
```

---

## タイミング・ループ

### `delay()` の代わりに非ブロッキングタイマーを使う

```c
// ✅ Good: 他の処理をブロックしない
static uint32_t last_sample_ms = 0;
const uint32_t SAMPLE_INTERVAL_MS = 100;

void loop() {
    uint32_t now = millis();
    if (now - last_sample_ms >= SAMPLE_INTERVAL_MS) {
        last_sample_ms = now;
        read_sensor();
    }
    // 他の処理も並行して動く
    handle_serial();
    update_display();
}

// ❌ Bad: delay はすべてブロックする
void loop_bad() {
    read_sensor();
    delay(100);  // この間 Serial も GPIO も止まる
}
```

### オーバーフロー対策

```c
// ✅ Good: millis() は 49日で折り返すが、引き算は正しく機能する
if ((uint32_t)(millis() - last_time) >= interval) { ... }

// ❌ Bad: オーバーフロー時に誤動作
if (millis() - last_time >= interval) { ... }  // 型次第で問題になる
```

---

## エラーハンドリング

### 戻り値を必ずチェックする

```c
// ✅ Good
esp_err_t ret = nvs_flash_init();
if (ret != ESP_OK) {
    ESP_LOGE(TAG, "NVS init failed: %s", esp_err_to_name(ret));
    return;
}

// ✅ Good (Arduino / I2C)
Wire.beginTransmission(SENSOR_ADDR);
Wire.write(REG_CONFIG);
uint8_t err = Wire.endTransmission();
if (err != 0) {
    Serial.printf("I2C error: %d\n", err);
    return false;
}
```

### ウォッチドッグを活用する（ESP32）

```c
#include "esp_task_wdt.h"

void setup() {
    esp_task_wdt_init(5, true);   // 5秒でリセット
    esp_task_wdt_add(NULL);       // 現在タスクを監視対象に
}

void loop() {
    esp_task_wdt_reset();  // WDT リセット（生存確認）
    // ... メイン処理
}
```

---

## デバッグ・ログ

### シリアルデバッグは条件コンパイルで制御

```c
#define DEBUG_ENABLED 1

#if DEBUG_ENABLED
  #define DEBUG_PRINT(x)    Serial.print(x)
  #define DEBUG_PRINTLN(x)  Serial.println(x)
  #define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINTF(...)
#endif

// 使い方
DEBUG_PRINTF("ADC value: %d, Temp: %.2f\n", adc_val, temp);
```

### ESP-IDF のログシステムを使う（ESP32 推奨）

```c
#include "esp_log.h"

static const char *TAG = "MY_MODULE";

ESP_LOGI(TAG, "Sensor initialized");
ESP_LOGW(TAG, "Voltage low: %.2f V", voltage);
ESP_LOGE(TAG, "I2C timeout after %d ms", timeout_ms);
ESP_LOGD(TAG, "Raw ADC: %d", raw);  // デバッグのみ
```

---

## チェックリスト

- [ ] 整数型は `uint8_t` / `int16_t` 等 stdint 型を使用
- [ ] マジックナンバーを `#define` または `const` で定数化
- [ ] 動的メモリ割り当て（malloc/new）を使っていない
- [ ] 割り込みハンドラーは最小限（フラグセットのみ）
- [ ] 割り込みから変更する変数に `volatile` を付与
- [ ] `delay()` をメインループで使っていない（非ブロッキング設計）
- [ ] `millis()` の差分演算で符号なし型を使用
- [ ] ペリフェラル初期化の戻り値をチェック
- [ ] デバッグ出力を条件コンパイルで制御
