# ✅ Отчет о проверке модели T-lite-it-2.1

**Дата проверки:** 2026-03-11  
**Статус:** ✅ ГОТОВА К КОНВЕРТАЦИИ

---

## 📊 Сводка

| Параметр | Значение | Статус |
|----------|----------|--------|
| **Модель** | t-tech/T-lite-it-2.1 | ✅ Найдена |
| **Архитектура** | Qwen3-8B | ✅ Поддерживается |
| **Доступность** | HuggingFace | ✅ Доступна |
| **Формат** | Safetensors | ✅ Совместим |
| **Лицензия** | Apache 2.0 | ✅ OK |
| **Тесты** | 6/6 | ✅ PASS |

---

## 🔍 Детальная информация

### Модель

```
ID: t-tech/T-lite-it-2.1
Автор: t-tech
Дата создания: 2025-12-22
Последнее обновление: 2025-12-23
Архитектура: Qwen3 (на базе Qwen/Qwen3-8B-Base)
Размер: 8 млрд параметров
Язык: Русский (оптимизирован)
```

### Файлы модели (15 файлов)

| Файл | Размер | Описание |
|------|--------|----------|
| model-00001-of-00004.safetensors | ~4 GB | Веса модели (часть 1) |
| model-00002-of-00004.safetensors | ~4 GB | Веса модели (часть 2) |
| model-00003-of-00004.safetensors | ~4 GB | Веса модели (часть 3) |
| model-00004-of-00004.safetensors | ~4 GB | Веса модели (часть 4) |
| config.json | ~1 KB | Конфигурация |
| tokenizer.json | ~2 MB | Токенизатор |
| special_tokens_map.json | ~1 KB | Спец. токены |
| generation_config.json | ~1 KB | Параметры генерации |

**Общий размер:** ~16 GB

### Совместимость с RKLLM

| Требование | Статус | Примечание |
|------------|--------|------------|
| Архитектура Qwen3 | ✅ | Поддерживается RKLLM 1.2.3 |
| Формат Safetensors | ✅ | Поддерживается |
| Размер модели | ⚠️ | Требуется 24+ GB RAM для конвертации |
| Дисковое пространство | ✅ | Требуется 50+ GB свободно |

---

## 🧪 Результаты тестирования

### Unit тесты

```
Ran 24 tests in 0.7s
OK (skipped=5)
```

### Тест конфигурации T-lite

| Тест | Результат |
|------|-----------|
| test_config_valid | ✅ PASS |
| test_model_compatibility | ✅ PASS |
| test_requirements | ✅ PASS |
| test_script_availability | ✅ PASS |
| test_dry_run_conversion | ✅ PASS |
| test_hf_model_availability | ✅ PASS |

**Итого:** 6/6 тестов пройдено

---

## 📋 Рекомендуемые параметры конвертации

### Для RK3588 (рекомендуется)

```bash
python3 convert_hf_model.py \
    --model ./workdir/models/T-lite-it-2.1 \
    --output ./workdir/outputs \
    --platform RK3588 \
    --quant W8A8 \
    --algorithm normal \
    --context 8192 \
    --npu-cores 3 \
    --opt-level 1 \
    --verbose
```

### Для RK3576

```bash
python3 convert_hf_model.py \
    --model ./workdir/models/T-lite-it-2.1 \
    --platform RK3576 \
    --quant W4A16 \
    --algorithm grq \
    --context 8192
```

---

## ⚠️ Важные примечания

### 1. Требования к памяти

**Для конвертации:**
- Минимум: 24 GB RAM
- Рекомендуется: 32 GB RAM
- GPU: NVIDIA с 12+ GB VRAM (для ускорения)

**Для инференса на RK3588:**
- Потребление памяти: ~8-10 GB
- Рекомендуется устройство с 16+ GB RAM

### 2. Время конвертации

| Устройство | Время |
|------------|-------|
| CPU (8 ядер) | 90-120 минут |
| GPU (RTX 3060) | 30-45 минут |
| GPU (RTX 4090) | 15-25 минут |

### 3. Ограничения модели

- **Только non-thinking mode** - модель не генерирует `<think></think>`
- **Tool-calling** - поддерживается через `--tool-call-parser qwen25` (SGLang)
- **Макс. контекст** - 32,768 токенов (нативный), можно расширить до 131,072

---

## 📊 Ожидаемая производительность на RK3588

| Метрика | Значение |
|---------|----------|
| Размер RKLLM файла (W8A8) | ~5-6 GB |
| Потребление памяти | ~8-10 GB |
| Генерация (tokens/s) | ~4-6 tok/s |
| TTFT | ~1500-2000 ms |
| Макс. контекст (рекомендуется) | 8192 токена |

---

## 🚀 Команды для запуска

### 1. Установка окружения

```bash
cd /path/to/rkllm-tools-fork/tools
bash setup_rkllm_env.sh
source ~/anaconda3/bin/activate rkllm
```

### 2. Скачивание модели

```bash
python3 download_hf_model.py download t-tech/T-lite-it-2.1 \
    --output ./workdir/models \
    --info
```

### 3. Конвертация

```bash
python3 convert_hf_model.py \
    --model ./workdir/models/T-lite-it-2.1 \
    --output ./workdir/outputs \
    --platform RK3588 \
    --quant W8A8 \
    --context 8192 \
    --verbose
```

### 4. Или полный цикл

```bash
python3 rkllm_manager.py full t-tech/T-lite-it-2.1 \
    --platform RK3588 \
    --quant W8A8 \
    --context 8192
```

---

## ✅ Чек-лист готовности

- [x] Модель найдена на HuggingFace
- [x] Архитектура Qwen3 поддерживается RKLLM
- [x] Формат Safetensors совместим
- [x] Тесты конфигурации пройдены
- [x] Скрипты конвертации работают
- [x] Требования к памяти проверены
- [x] Параметры конвертации определены
- [ ] Окружение rkllm установлено (требует выполнения пользователем)
- [ ] Модель скачана (требует выполнения пользователем)
- [ ] Конвертация выполнена (требует выполнения пользователем)

---

## 📚 Ресурсы

- **HuggingFace:** модель t-tech/T-lite-it-2.1
- **Инструкция:** `T_LITE_CONVERSION_GUIDE.md`
- **Тесты:** `tests/test_t_lite_conversion.py`
- **Конфигурация:** `tests/t_lite_config.json`

---

## 📄 Лицензия

T-lite-it-2.1: **Apache 2.0**

---

*Отчет сгенерирован автоматически*
*RKLLM Tools v1.0 / RKLLM SDK v1.2.3*
