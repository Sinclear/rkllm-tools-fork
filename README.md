# RKLLM Tools Fork

**Инструменты для конвертации LLM моделей в формат RKLLM**

[![Version](https://img.shields.io/badge/version-1.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.9--3.12-green)]()
[![Platform](https://img.shields.io/badge/platform-RK3588%20%7C%20RK3576%20%7C%20RK3562%20%7C%20RV1126B-orange)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-lightgrey)]()

---

## 🚀 Быстрый старт

```bash
# 1. Клонирование
cd /path/to/rkllm-tools-fork

# 2. Установка окружения
cd tools && bash setup_rkllm_env.sh

# 3. Активация
source ~/anaconda3/bin/activate rkllm

# 4. Конвертация модели (полный цикл)
python rkllm_manager.py full Qwen/Qwen2.5-1.5B-Instruct
```

---

## 📋 Содержание

- [Возможности](#возможности)
- [Требования](#требования)
- [Установка](#установка)
- [Использование](#использование)
- [Документация](#документация)
- [Тесты](#тесты)
- [Безопасность](#безопасность)
- [Лицензия](#лицензия)

---

## ✨ Возможности

### 🛠 Инструменты

| Инструмент | Описание |
|------------|----------|
| `setup_rkllm_env.sh` | Автоматическая установка окружения |
| `verify_rkllm_installation.py` | Комплексная проверка установки |
| `convert_hf_model.py` | Конвертация моделей в RKLLM |
| `download_hf_model.py` | Загрузка с HuggingFace Hub |
| `rkllm_manager.py` | Единый менеджер для всех операций |

### 🔧 Функции

- ✅ Автоматическое создание conda окружения
- ✅ Проверка системных требований
- ✅ Скачивание моделей с resume загрузкой
- ✅ Квантование W8A8, W4A16, W4A16_G128
- ✅ Поддержка multiple платформ (RK3588, RK3576, RK3562, RV1126B)
- ✅ Интерактивный и пакетный режимы
- ✅ Комплексное тестирование

---

## 📋 Требования

### Системные

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| CPU | 4 ядра | 8+ ядер |
| RAM | 8 GB | 16+ GB |
| Disk | 20 GB | 50+ GB SSD |
| GPU | - | NVIDIA 4GB+ VRAM |

### Программные

- **Anaconda/Miniconda** (Python 3.9-3.12)
- **Linux** x86_64 (Ubuntu 20.04+, Debian 11+)
- **NVIDIA Driver** (опционально, для GPU ускорения)

---

## ⚙️ Установка

### Шаг 1: Проверка Conda

```bash
conda --version
```

### Шаг 2: Установка окружения

```bash
cd /path/to/rkllm-tools-fork/tools
bash setup_rkllm_env.sh
```

### Шаг 3: Активация

```bash
source ~/anaconda3/bin/activate rkllm
```

### Шаг 4: Верификация

```bash
python verify_rkllm_installation.py --verbose
```

---

## 💡 Использование

### Основные команды

```bash
# Установка окружения
python rkllm_manager.py setup

# Проверка установки
python rkllm_manager.py verify

# Скачать модель
python rkllm_manager.py download <model_id>

# Конвертировать модель
python rkllm_manager.py convert <model_path> \
    --platform RK3588 \
    --quant W8A8

# Полный цикл (скачать + конвертировать)
python rkllm_manager.py full <model_id>

# Список рекомендуемых моделей
python rkllm_manager.py list
```

### Пример: Конвертация Qwen2.5

```bash
# Активация окружения
source ~/anaconda3/bin/activate rkllm

# Полный цикл
python rkllm_manager.py full Qwen/Qwen2.5-1.5B-Instruct \
    --platform RK3588 \
    --quant W8A8 \
    --context 4096
```

### Параметры конвертации

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--platform` | Целевая платформа | RK3588 |
| `--quant` | Тип квантования | W8A8 |
| `--context` | Размер контекста | 4096 |
| `--npu-cores` | Ядер NPU | 3 |
| `--opt-level` | Уровень оптимизации | 1 |

---

## 📚 Документация

### Основная документация

- [PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md) - Полная документация проекта
- [README.md](tools/README.md) - Руководство по инструментам
- [T_LITE_CONVERSION_GUIDE.md](tools/T_LITE_CONVERSION_GUIDE.md) - Инструкция по T-lite-it-2.1

### Разделы документации

1. [Обзор проекта](docs/PROJECT_DOCUMENTATION.md#обзор-проекта)
2. [Архитектура](docs/PROJECT_DOCUMENTATION.md#архитектура)
3. [Установка](docs/PROJECT_DOCUMENTATION.md#установка-и-настройка)
4. [API Reference](docs/PROJECT_DOCUMENTATION.md#api-reference)
5. [Тестирование](docs/PROJECT_DOCUMENTATION.md#тестирование)
6. [Безопасность](docs/PROJECT_DOCUMENTATION.md#безопасность)

---

## 🧪 Тесты

### Запуск тестов

```bash
# Unit тесты
python -m unittest tests.test_rkllm_tools

# Тест T-lite
python tests/test_t_lite_conversion.py --verbose

# Все тесты
bash run_tests.sh --all

# С покрытием
bash run_tests.sh --coverage
```

### Результаты тестов

| Категория | Пройдено | Провалено | Пропущено |
|-----------|----------|-----------|-----------|
| Unit тесты | 19 | 0 | 5 |
| T-lite тесты | 6 | 0 | 0 |
| **ИТОГО** | **25** | **0** | **5** |

---

## 🔒 Безопасность

### Аудит безопасности

✅ **Отсутствуют прямые ссылки** - все URL заменены на описания  
✅ **Нет жестко закодированных токенов** - используются переменные окружения  
✅ **Нет чувствительных данных** - пароли, ключи, API токены отсутствуют  
✅ **Безопасный subprocess** - используется вместо os.system  
✅ **Валидация ввода** - проверка путей и параметров  

### Проверка безопасности

```bash
# Проверка на чувствительные данные
grep -r "password\|secret\|api_key" tools/

# Проверка на прямые ссылки
grep -r "http" tools/*.py tools/*.md

# Проверка на жестко закодированные пути
grep -r "/home/\|/root/" tools/*.py
```

---

## 📄 Лицензия

- **Инструменты:** Apache 2.0
- **RKLLM Toolkit:** Лицензия Rockchip

---

## 📞 Поддержка

### Решение проблем

1. Проверьте логи установки
2. Запустите `python rkllm_manager.py verify`
3. Изучите документацию в `docs/`
4. Проверьте требования к памяти/диску

### Логи

```bash
# Логи конвертации
tail -f /tmp/rkllm_convert.log

# Логи загрузки
tail -f /tmp/hf_download.log
```

---

## 📁 Структура проекта

```
rkllm-tools-fork/
├── tools/                      # Основные инструменты
│   ├── setup_rkllm_env.sh
│   ├── verify_rkllm_installation.py
│   ├── convert_hf_model.py
│   ├── download_hf_model.py
│   ├── rkllm_manager.py
│   ├── run_tests.sh
│   └── README.md
├── tests/                      # Тесты
│   ├── test_rkllm_tools.py
│   ├── test_t_lite_conversion.py
│   └── t_lite_config.json
├── docs/                       # Документация
│   └── PROJECT_DOCUMENTATION.md
├── workdir/                    # Рабочая директория
│   ├── models/                 # Скачанные модели
│   └── outputs/                # RKLLM файлы
└── README.md                   # Этот файл
```

---

**Версия:** 1.0  
**Дата:** Март 2026  
**RKLLM SDK:** v1.2.3
