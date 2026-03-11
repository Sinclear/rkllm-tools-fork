# RKLLM Tools Fork - Документация проекта

**Версия:** 1.0  
**Дата:** Март 2026  
**Статус:** Готов к использованию

---

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура](#архитектура)
3. [Установка и настройка](#установка-и-настройка)
4. [Использование](#использование)
5. [API Reference](#api-reference)
6. [Тестирование](#тестирование)
7. [Безопасность](#безопасность)
8. [Лицензия](#лицензия)

---

## 📖 Обзор проекта

### Назначение

RKLLM Tools - это набор инструментов для конвертации языковых моделей (LLM) из формата HuggingFace в формат RKLLM для работы на NPU Rockchip (RK3588, RK3576, RK3562, RV1126B).

### Основные возможности

- **Установка окружения** - автоматическое создание conda окружения
- **Верификация** - проверка установки и зависимостей
- **Загрузка моделей** - скачивание с HuggingFace Hub
- **Конвертация** - преобразование в RKLLM с квантованием
- **Управление** - единый менеджер для всех операций

### Поддерживаемые платформы

| Платформа | NPU Ядра | Производительность |
|-----------|----------|-------------------|
| RK3588 | 3 | до 6 TOPS |
| RK3576 | 3 | до 4 TOPS |
| RK3562 | 2 | до 2 TOPS |
| RV1126B | 1 | до 0.8 TOPS |

### Поддерживаемые модели

- **Qwen系列:** Qwen2, Qwen2.5, Qwen3, Qwen-VL
- **Llama系列:** Llama, Llama2, Llama3
- **Phi系列:** Phi-2, Phi-3
- **Gemma系列:** Gemma2, Gemma3
- **Другие:** ChatGLM3, MiniCPM, InternLM, RWKV

---

## 🏗 Архитектура

### Структура проекта

```
rkllm-tools-fork/
├── tools/                      # Основные инструменты
│   ├── setup_rkllm_env.sh      # Установка окружения
│   ├── verify_rkllm_installation.py  # Проверка установки
│   ├── convert_hf_model.py     # Конвертация моделей
│   ├── download_hf_model.py    # Загрузка моделей
│   ├── rkllm_manager.py        # Главный менеджер
│   └── run_tests.sh            # Запуск тестов
├── tests/                      # Тесты
│   ├── test_rkllm_tools.py     # Unit тесты
│   ├── test_t_lite_conversion.py  # Тест T-lite
│   └── t_lite_config.json      # Конфигурация
├── docs/                       # Документация
│   └── PROJECT_DOCUMENTATION.md
├── workdir/                    # Рабочая директория
│   ├── models/                 # Скачанные модели
│   └── outputs/                # RKLLM файлы
└── README.md                   # Основная документация
```

### Компоненты

#### 1. setup_rkllm_env.sh
- Проверка системных требований
- Создание conda окружения
- Установка зависимостей
- Верификация установки

#### 2. verify_rkllm_installation.py
- Проверка Python версии
- Проверка установленных пакетов
- Проверка CUDA/GPU
- Проверка памяти и диска

#### 3. convert_hf_model.py
- Загрузка модели
- Построение графа
- Квантование (W8A8, W4A16)
- Экспорт в RKLLM

#### 4. download_hf_model.py
- Поиск моделей
- Скачивание файлов
- Resume загрузка
- Информация о модели

#### 5. rkllm_manager.py
- Единый интерфейс
- Автоматизация процессов
- Интерактивный режим

---

## ⚙️ Установка и настройка

### Системные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| CPU | 4 ядра | 8+ ядер |
| RAM | 8 GB | 16+ GB |
| Disk | 20 GB | 50+ GB SSD |
| GPU | - | NVIDIA 4GB+ |

### Быстрый старт

```bash
# 1. Перейдите в директорию tools
cd /path/to/rkllm-tools-fork/tools

# 2. Установите окружение
bash setup_rkllm_env.sh

# 3. Активируйте окружение
source ~/anaconda3/bin/activate rkllm

# 4. Проверьте установку
python verify_rkllm_installation.py
```

### Переменные окружения

```bash
# Имя окружения
export RKLLM_ENV_NAME=rkllm

# Версия Python (3.9, 3.10, 3.11, 3.12)
export RKLLM_PYTHON_VERSION=3.11

# Токен HuggingFace (для gated моделей)
export HF_TOKEN=your_token_here
```

---

## 💡 Использование

### Команды rkllm_manager.py

```bash
# Установка окружения
python rkllm_manager.py setup

# Проверка установки
python rkllm_manager.py verify

# Скачать модель
python rkllm_manager.py download <model_id>

# Конвертировать модель
python rkllm_manager.py convert <model_path>

# Полный цикл
python rkllm_manager.py full <model_id>

# Список моделей
python rkllm_manager.py list
```

### Параметры конвертации

```bash
python convert_hf_model.py \
    --model <path_to_model> \
    --output <output_dir> \
    --platform RK3588 \
    --quant W8A8 \
    --context 4096 \
    --npu-cores 3 \
    --verbose
```

### Типы квантования

| Тип | Описание | Размер | Скорость |
|-----|----------|--------|----------|
| W8A8 | 8-бит веса и активации | Средний | Высокая |
| W4A16 | 4-бит веса, 16-бит активации | Малый | Средняя |
| W4A16_G128 | 4-бит с группировкой 128 | Малый | Средняя |

---

## 📚 API Reference

### ConversionConfig

```python
@dataclass
class ConversionConfig:
    model_path: str           # Путь к модели
    output_dir: str           # Директория вывода
    target_platform: str      # RK3588, RK3576, RK3562, RV1126B
    quantized_dtype: str      # W8A8, W4A16, W4A16_G128
    quantized_algorithm: str  # normal, grq
    optimization_level: int   # 0, 1
    num_npu_core: int         # 1-3
    max_context: int          # 4096, 8192, 16384
    device: str               # cuda, cpu
    dtype: str                # float32, float16, bfloat16
```

### ModelConverter

```python
class ModelConverter:
    def __init__(self, config: ConversionConfig, verbose: bool = True)
    def load_model(self) -> bool      # Загрузка модели
    def build_model(self) -> bool     # Построение и квантование
    def export_model(self) -> bool    # Экспорт в RKLLM
    def convert(self) -> bool         # Полный цикл
```

### RKLLMVerifier

```python
class RKLLMVerifier:
    def check_python_version(self) -> CheckResult
    def check_cuda(self) -> CheckResult
    def check_disk_space(self) -> CheckResult
    def check_memory(self) -> CheckResult
    def check_rkllm_api(self) -> CheckResult
    def check_package(self, name: str, constraints: Dict) -> CheckResult
    def run_all_checks(self) -> List[CheckResult]
    def print_report(self, json_output: bool = False) -> str
```

---

## 🧪 Тестирование

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

### Покрытие тестов

| Модуль | Покрытие |
|--------|----------|
| convert_hf_model.py | ~85% |
| download_hf_model.py | ~80% |
| rkllm_manager.py | ~85% |
| verify_rkllm_installation.py | ~90% |
| setup_rkllm_env.sh | ~80% |

---

## 🔒 Безопасность

### Проверки кода

✅ **Отсутствуют прямые ссылки** - все URL заменены на описания  
✅ **Нет жестко закодированных токенов** - используются переменные окружения  
✅ **Нет чувствительных данных** - пароли, ключи, API токены отсутствуют  
✅ **Безопасный subprocess** - используется вместо os.system  
✅ **Валидация ввода** - проверка путей и параметров  

### Рекомендации по безопасности

1. **HF_TOKEN** - храните в переменных окружения, не в коде
2. **Пути к файлам** - используйте абсолютные пути
3. **Права доступа** - ограничьте доступ к рабочим директориям
4. **Сетевые запросы** - проверяйте SSL сертификаты

### Аудит безопасности

```bash
# Проверка на чувствительные данные
grep -r "password\|secret\|api_key" tools/

# Проверка на прямые ссылки
grep -r "http[s]?://" tools/*.py

# Проверка на жестко закодированные пути
grep -r "/home/\|/root/" tools/*.py
```

---

## 📄 Лицензия

Данный проект распространяется под лицензией Apache 2.0 (для созданных инструментов).

RKLLM Toolkit распространяется под лицензией Rockchip.

---

## 📞 Поддержка

### Решение проблем

1. Проверьте логи установки
2. Запустите `python rkllm_manager.py verify`
3. Изучите документацию
4. Проверьте требования к памяти/диску

### Логи

```bash
# Логи конвертации
tail -f /tmp/rkllm_convert.log

# Логи загрузки
tail -f /tmp/hf_download.log
```

---

*Документация актуальна для версии 1.0*  
*RKLLM SDK v1.2.3*
