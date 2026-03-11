# 📘 Инструкция по конвертации T-lite-it-2.1 для RK3588

## 📋 О модели

| Параметр | Значение |
|----------|----------|
| **Модель** | T-lite-it-2.1 |
| **Архитектура** | Qwen3-8B |
| **Язык** | Русский (оптимизирован) |
| **Контекст** | 32,768 токенов (нативный) |
| **Размер** | ~16 GB (4 файла safetensors) |
| **Лицензия** | Apache 2.0 |
| **HuggingFace** | модель t-tech/T-lite-it-2.1 |

### Особенности
- ✅ Поддерживает **tool-calling** (ключевое улучшение vs T-lite-it-1.0)
- ✅ Только **non-thinking mode** (не генерирует `<think></think>`)
- ✅ Оптимизированный токенизатор для русского языка
- ✅ Превосходит Qwen3-8B в сценариях вызова инструментов

---

## 🚀 Быстрый старт

### Шаг 1: Установка окружения

```bash
cd /path/to/rkllm-tools-fork/tools

# Запуск установки
bash setup_rkllm_env.sh
```

### Шаг 2: Активация окружения

```bash
source ~/anaconda3/bin/activate rkllm

# Проверка установки
python3 verify_rkllm_installation.py --verbose
```

### Шаг 3: Скачивание модели

```bash
# Вариант A: Через download_hf_model.py
python3 download_hf_model.py download t-tech/T-lite-it-2.1 \
    --output ./workdir/models \
    --info

# Вариант B: Через rkllm_manager.py
python3 rkllm_manager.py download t-tech/T-lite-it-2.1
```

**Ожидаемый размер:** ~16 GB  
**Время скачивания:** зависит от скорости интернета (30-60 мин)

### Шаг 4: Конвертация в RKLLM

```bash
# Перейдите в директорию tools
cd /path/to/rkllm-tools-fork/tools

# Запуск конвертации
python3 convert_hf_model.py \
    --model ./workdir/models/T-lite-it-2.1 \
    --output ./workdir/outputs \
    --platform RK3588 \
    --quant W8A8 \
    --context 8192 \
    --verbose
```

**Параметры конвертации:**
- `--platform RK3588` - целевая платформа
- `--quant W8A8` - 8-битное квантование (рекомендуется)
- `--context 8192` - размер контекста (можно увеличить до 16384)
- `--npu-cores 3` - использовать 3 ядра NPU

### Шаг 5: Проверка результата

```bash
# Проверка выходного файла
ls -lh ./workdir/outputs/

# Ожидаемый файл: T-lite-it-2.1_W8A8_RK3588.rkllm
# Ожидаемый размер: ~5-6 GB
```

---

## ⚙️ Альтернативные команды

### Полный цикл одной командой

```bash
python3 rkllm_manager.py full t-tech/T-lite-it-2.1 \
    --platform RK3588 \
    --quant W8A8 \
    --context 8192
```

### Конвертация с 4-битным квантованием

```bash
python3 convert_hf_model.py \
    --model ./workdir/models/T-lite-it-2.1 \
    --output ./workdir/outputs \
    --platform RK3588 \
    --quant W4A16 \
    --algorithm grq \
    --context 8192
```

**Преимущества W4A16:**
- Меньший размер модели (~4 GB)
- Меньше потребление памяти на устройстве

**Недостатки:**
- Немного ниже точность
- Медленнее генерация

---

## 📊 Ожидаемая производительность на RK3588

| Параметр | Значение |
|----------|----------|
| **Размер модели** | ~5-6 GB (W8A8) |
| **Потребление памяти** | ~8-10 GB |
| **Генерация (tokens/s)** | ~4-6 tok/s |
| **TTFT (Time To First Token)** | ~1500-2000 ms |
| **Макс. контекст** | 8192 токена |

### Сравнение с другими моделями

| Модель | Размер | Tokens/s | Память |
|--------|--------|----------|--------|
| Qwen2.5-0.5B | 0.5B | 42 tok/s | 654 MB |
| Qwen2.5-1.5B | 1.5B | 16 tok/s | 1659 MB |
| **T-lite-it-2.1** | **8B** | **~5 tok/s** | **~8 GB** |
| ChatGLM3-6B | 6B | 5 tok/s | 5976 MB |

---

## 🔧 Настройка параметров

### Увеличение контекста

Для работы с длинными текстами измените `config.json` перед конвертацией:

```json
{
    "rope_scaling": {
        "rope_type": "yarn",
        "factor": 2.0,
        "original_max_position_embeddings": 32768
    }
}
```

### Рекомендуемые параметры генерации

```python
# Для использования на устройстве
temperature = 0.7
top_p = 0.8
top_k = 20
presence_penalty = 1.0
```

---

## ⚠️ Возможные проблемы и решения

### 1. Недостаточно памяти при конвертации

**Ошибка:** `CUDA out of memory`

**Решение:**
```bash
# Использовать CPU (медленнее)
python3 convert_hf_model.py \
    --model ./workdir/models/T-lite-it-2.1 \
    --device cpu \
    --dtype float32
```

### 2. Ошибка загрузки модели

**Ошибка:** `Model not found`

**Решение:** Убедитесь что модель скачана корректно:
```bash
ls -lh ./workdir/models/T-lite-it-2.1/
# Должны быть файлы:
# - config.json
# - model-00001-of-00004.safetensors
# - model-00002-of-00004.safetensors
# - model-00003-of-00004.safetensors
# - model-00004-of-00004.safetensors
```

### 3. Долгая конвертация

**Время конвертации:** 60-120 минут на CPU, 20-40 минут на GPU

**Решение:** Используйте GPU:
```bash
export CUDA_VISIBLE_DEVICES=0
python3 convert_hf_model.py --model ... --device cuda
```

---

## 📁 Структура выходных файлов

```
workdir/
├── models/
│   └── T-lite-it-2.1/           # Скачанная модель
│       ├── config.json
│       ├── model-00001-of-00004.safetensors
│       └── ...
├── outputs/
│   └── T-lite-it-2.1_W8A8_RK3588.rkllm  # Готовая RKLLM модель
└── quant_data/
    └── data_quant.json          # Данные для квантования
```

---

## 🧪 Тестирование

### Проверка перед конвертацией

```bash
# Запуск тестов
cd /path/to/rkllm-tools-fork/tools

# Unit тесты
python3 -m unittest tests.test_rkllm_tools

# Тест T-lite конфигурации
python3 tests/test_t_lite_conversion.py --verbose
```

### Ожидаемые результаты тестов

```
Ran 24 tests in 0.7s
OK (skipped=5)

Модель: T-lite-it-2.1
Архитектура: Qwen3
Пройдено: 6
Провалено: 0
```

---

## 📚 Дополнительные ресурсы

- **Документация RKLLM:** `doc/Rockchip_RKLLM_SDK_EN_1.2.3.pdf`
- **GitHub RKLLM:** репозиторий airockchip/rknn-llm
- **Статья о модели:** Habr (поиск по запросу "T-lite-it-2.1")
- **arXiv:** статья 2512.10430

---

## 📄 Лицензия

T-lite-it-2.1 распространяется под лицензией **Apache 2.0**.

---

*Инструкция актуальна для RKLLM SDK v1.2.3*
*Дата обновления: 2026-03-11*
