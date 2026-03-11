# RKLLM Tools - Утилиты для конвертации LLM моделей

Комплект инструментов для удобной установки окружения, проверки установки и конвертации языковых моделей из HuggingFace в формат RKLLM для работы на NPU Rockchip.

## 📋 Содержание

- [Возможности](#возможности)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Установка](#установка)
- [Использование](#использование)
- [Поддерживаемые модели](#поддерживаемые-модели)
- [Производительность](#производительность)
- [Структура проекта](#структура-проекта)
- [FAQ](#faq)

## 🚀 Возможности

- **Автоматическая установка** - создание изолированного conda окружения со всеми зависимостями
- **Проверка установки** - комплексная диагностика окружения и зависимостей
- **Скачивание моделей** - загрузка моделей с HuggingFace Hub с поддержкой resume
- **Конвертация моделей** - преобразование в RKLLM формат с различными типами квантования
- **Пакетная обработка** - полный цикл "скачать + конвертировать" одной командой
- **Интерактивный режим** - удобный менеджер для всех операций

## 📋 Требования

### Системные требования

| Компонент | Минимальные | Рекомендуемые |
|-----------|-------------|---------------|
| CPU | 4 ядра | 8+ ядер |
| RAM | 8 GB | 16+ GB |
| Disk | 20 GB | 50+ GB SSD |
| GPU (опционально) | - | NVIDIA с 4GB+ VRAM |

### Программные требования

- **Anaconda** или **Miniconda** (Python 3.9-3.12)
- **Linux** x86_64 (Ubuntu 20.04+, Debian 11+)
- **NVIDIA Driver** (опционально, для ускорения конвертации)

## 🎯 Быстрый старт

```bash
# 1. Перейдите в директорию tools
cd /path/to/rkllm-tools-fork/tools

# 2. Установите окружение
bash setup_rkllm_env.sh

# 3. Активируйте окружение
source ~/anaconda3/bin/activate rkllm

# 4. Проверьте установку
python verify_rkllm_installation.py

# 5. Скачайте и сконвертируйте модель (полный цикл)
python rkllm_manager.py full Qwen/Qwen2.5-1.5B-Instruct
```

## 📦 Установка

### Шаг 1: Проверка Conda

```bash
conda --version
```

Если conda не установлена, скачайте с официального сайта Anaconda или Miniconda.

### Шаг 2: Запуск установки

```bash
cd /path/to/rkllm-tools-fork/tools
bash setup_rkllm_env.sh
```

Скрипт автоматически:
- Проверит системные требования
- Создаст conda окружение `rkllm` с Python 3.11
- Установит все необходимые зависимости
- Установит RKLLM Toolkit 1.2.3
- Создаст рабочие директории

### Шаг 3: Активация окружения

```bash
source ~/anaconda3/bin/activate rkllm
```

### Шаг 4: Верификация

```bash
python verify_rkllm_installation.py --verbose
```

## 💡 Использование

### RKLLM Manager - главный инструмент

```bash
# Показать справку
python rkllm_manager.py --help

# Установка окружения
python rkllm_manager.py setup

# Проверка установки
python rkllm_manager.py verify

# Скачать модель
python rkllm_manager.py download Qwen/Qwen2.5-1.5B-Instruct

# Конвертировать локальную модель
python rkllm_manager.py convert ./models/Qwen2.5-1.5B-Instruct

# Полный цикл (скачать + конвертировать)
python rkllm_manager.py full Qwen/Qwen2.5-1.5B-Instruct

# Показать список рекомендуемых моделей
python rkllm_manager.py list
```

### Параметры конвертации

```bash
# Конвертация с указанием платформы
python rkllm_manager.py convert ./models/model \
    --platform RK3588 \
    --quant W8A8 \
    --context 4096

# Доступные платформы: RK3588, RK3576, RK3562, RV1126B
# Типы квантования: W8A8, W4A16, W4A16_G128
```

### Прямое использование скриптов

```bash
# Скачивание модели
python download_hf_model.py download Qwen/Qwen2.5-1.5B-Instruct -o ./models

# Информация о модели
python download_hf_model.py info Qwen/Qwen2.5-1.5B-Instruct --list-files

# Поиск моделей
python download_hf_model.py search "qwen2.5 instruct" --limit 10

# Конвертация
python convert_hf_model.py \
    --model ./models/Qwen2.5-1.5B-Instruct \
    --output ./outputs \
    --platform RK3588 \
    --quant W8A8
```

## 🤗 Поддерживаемые модели

### Языковые модели

| Семейство | Модели |
|-----------|--------|
| **Qwen** | Qwen2, Qwen2.5, Qwen3, Qwen2-VL, Qwen3-VL |
| **Llama** | Llama, Llama2, Llama3 |
| **TinyLlama** | TinyLlama-1.1B |
| **Phi** | Phi-2, Phi-3 |
| **Gemma** | Gemma2, Gemma3, Gemma3n |
| **ChatGLM** | ChatGLM3-6B |
| **InternLM** | InternLM2 |
| **MiniCPM** | MiniCPM3, MiniCPM4 |
| **DeepSeek** | DeepSeek-R1-Distill |
| **TeleChat** | TeleChat2 |
| **RWKV** | RWKV7 |

### Мультимодальные модели

| Модель | Описание |
|--------|----------|
| Qwen2-VL / Qwen3-VL | Визионные модели от Qwen |
| MiniCPM-V-2_6 | Компактная визионная модель |
| InternVL2 / InternVL3 | Визионные модели от OpenGVLab |
| Janus-Pro-1B | Мультимодальная модель |
| SmolVLM | Легкая визионная модель |

## ⚡ Производительность

### Бенчмарк на RK3588 (W8A8 квантование)

| Модель | Размер | Tokens/s | TTFT (ms) | Память (MB) |
|--------|--------|----------|-----------|-------------|
| Qwen2 | 0.5B | 42.58 | 143.83 | 654 |
| Qwen3 | 0.6B | 32.16 | 213.50 | 774 |
| TinyLLAMA | 1.1B | 24.49 | 239.00 | 1085 |
| Qwen2.5 | 1.5B | 16.32 | 412.27 | 1659 |
| InternLM2 | 1.8B | 15.58 | 374.00 | 1766 |
| TeleChat2 | 3B | 10.22 | 649.60 | 2777 |
| ChatGLM3 | 6B | 4.94 | 1395.34 | 5976 |

### Рекомендации по выбору квантования

| Тип | Память | Производительность | Качество |
|-----|--------|-------------------|----------|
| **W8A8** | Средняя | Высокая | Отличное |
| **W4A16** | Низкая | Средняя | Хорошее |
| **W4A16_G128** | Низкая | Средняя | Хорошее |

## 📁 Структура проекта

```
rknn-llm/
├── tools/                          # Утилиты (созданные)
│   ├── setup_rkllm_env.sh          # Скрипт установки окружения
│   ├── verify_rkllm_installation.py # Проверка установки
│   ├── convert_hf_model.py         # Конвертация моделей
│   ├── download_hf_model.py        # Скачивание с HuggingFace
│   └── rkllm_manager.py            # Главный менеджер
├── workdir/                        # Рабочая директория (создается)
│   ├── models/                     # Скачанные модели
│   ├── outputs/                    # RKLLM файлы
│   └── quant_data/                 # Данные для квантования
├── rkllm-toolkit/
│   └── packages/                   # Пакеты RKLLM
│       ├── requirements.txt
│       └── rkllm_toolkit-*.whl
└── examples/                       # Примеры использования
```

## 🔧 Настройка окружения

### Переменные окружения

```bash
# Выбор имени окружения
export RKLLM_ENV_NAME=rkllm

# Выбор версии Python (3.9, 3.10, 3.11, 3.12)
export RKLLM_PYTHON_VERSION=3.11

# Токен HuggingFace (для gated моделей)
export HF_TOKEN=your_token_here
```

### Для Python 3.12

```bash
export BUILD_CUDA_EXT=0
```

### Для RWKV7 моделей

```bash
export RKLLM_USE_RWKV7=true
```

## 📝 Примеры использования

### Пример 1: Конвертация Qwen2.5-0.5B

```bash
# Активация окружения
source ~/anaconda3/bin/activate rkllm

# Скачивание модели
python download_hf_model.py download Qwen/Qwen2.5-0.5B-Instruct --info

# Конвертация
python convert_hf_model.py \
    --model ./models/Qwen2.5-0.5B-Instruct \
    --platform RK3588 \
    --quant W8A8

# Результат: ./outputs/Qwen2.5-0.5B-Instruct_W8A8_RK3588.rkllm
```

### Пример 2: Полный цикл для DeepSeek-R1

```bash
python rkllm_manager.py full deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
    --platform RK3588 \
    --quant W8A8 \
    --context 4096
```

### Пример 3: Создание кастомного датасета

Создайте файл `data_quant.json`:

```json
[
    {"input": "Human: Привет!\nAssistant: ", "target": "Привет! Как могу помочь?"},
    {"input": "Human: Что такое RK3588?\nAssistant: ", "target": "RK3588 - это процессор от Rockchip с NPU."}
]
```

Используйте при конвертации:

```bash
python convert_hf_model.py \
    --model ./models/model \
    --dataset ./data_quant.json \
    --quant W8A8
```

## ❓ FAQ

### Q: Ошибка "CUDA unavailable"
**A:** Конвертация будет работать на CPU, но медленнее. Для ускорения установите NVIDIA драйверы и CUDA Toolkit.

### Q: Сколько места нужно для конвертации?
**A:** Для модели 1.5B требуется ~10-15 GB свободного места.

### Q: Как долго длится конвертация?
**A:** Для Qwen2.5-1.5B на CPU: ~30-60 минут. На GPU с CUDA: ~10-20 минут.

### Q: Где взять токен HuggingFace?
**A:** На официальном сайте HuggingFace в разделе настроек токенов. Нужен для gated моделей (Llama, Gemma).

### Q: Как проверить работу модели на устройстве?
**A:** Используйте примеры из `examples/rkllm_api_demo/deploy/`.

### Q: Ошибка нехватки памяти
**A:**
- Закройте другие приложения
- Используйте `--dtype float16` при конвертации
- Выберите модель меньшего размера

## 📚 Дополнительные ресурсы

- **Официальная документация:** RKLLM SDK (см. `doc/Rockchip_RKLLM_SDK_EN_1.2.3.pdf`)
- **Готовые модели:** rkllm_model_zoo (код доступа: rkllm)
- **GitHub:** репозиторий airockchip/rknn-llm
- **Документация SDK:** `doc/Rockchip_RKLLM_SDK_EN_1.2.3.pdf`

## 📄 Лицензия

Данный инструмент распространяется в составе RKLLM SDK. См. `LICENSE` в корневой директории.

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи установки
2. Запустите `python rkllm_manager.py verify`
3. Изучите документацию SDK
4. Проверьте issues на GitHub

---

**Версия инструментов:** 1.0
**Версия RKLLM SDK:** 1.2.3
**Дата обновления:** Март 2026
