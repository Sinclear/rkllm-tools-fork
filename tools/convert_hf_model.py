#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт конвертации языковых моделей из HuggingFace в формат RKLLM

Поддерживаемые модели:
- Llama, TinyLlama, Qwen2/Qwen2.5/Qwen3
- Phi2/Phi3, ChatGLM3-6B
- Gemma2/Gemma3/Gemma3n
- InternLM2, MiniCPM3/MiniCPM4
- TeleChat2, Qwen2-VL/Qwen3-VL
- MiniCPM-V-2_6, DeepSeek-R1-Distill
- Janus-Pro-1B, InternVL2-1B/InternVL3-1B
- SmolVLM, RWKV7, DeepSeekOCR

Использование:
    python convert_hf_model.py \
        --model Qwen/Qwen2.5-1.5B-Instruct \
        --output ./outputs \
        --platform RK3588 \
        --quant W8A8
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

# Проверка импорта RKLLM (условный импорт для тестирования)
RKLLM_AVAILABLE = False
try:
    from rkllm.api import RKLLM
    RKLLM_AVAILABLE = True
except ImportError:
    pass  # Не завершаем - разрешаем тестирование без RKLLM


@dataclass
class ConversionConfig:
    """Конфигурация конвертации"""
    model_path: str
    output_dir: str
    target_platform: str = "RK3588"
    quantized_dtype: str = "W8A8"
    quantized_algorithm: str = "normal"
    optimization_level: int = 1
    num_npu_core: int = 3
    max_context: int = 4096
    device: str = "cuda"
    dtype: str = "float32"
    dataset_file: Optional[str] = None
    do_quantization: bool = True
    hybrid_rate: int = 0
    custom_config: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ModelConverter:
    """Класс для конвертации моделей в RKLLM формат"""
    
    SUPPORTED_PLATFORMS = ["RK3588", "RK3576", "RK3562", "RV1126B"]
    
    SUPPORTED_QUANT_TYPES = {
        "W8A8": {"algorithm": "normal", "description": "8-битные веса и активации"},
        "W4A16": {"algorithm": "grq", "description": "4-битные веса, 16-битные активации"},
        "W4A16_G128": {"algorithm": "grq", "description": "4-битные веса с группировкой 128"},
        "W8A8_G128": {"algorithm": "normal", "description": "8-битные с группировкой 128"},
    }
    
    def __init__(self, config: ConversionConfig, verbose: bool = True):
        self.config = config
        self.verbose = verbose
        self.llm = None
        self.start_time = None
        
        # Валидация конфигурации
        self._validate_config()
    
    def _validate_config(self):
        """Проверка конфигурации"""
        if self.config.target_platform not in self.SUPPORTED_PLATFORMS:
            raise ValueError(f"Платформа {self.config.target_platform} не поддерживается. "
                           f"Доступны: {self.SUPPORTED_PLATFORMS}")
        
        if self.config.quantized_dtype not in self.SUPPORTED_QUANT_TYPES:
            raise ValueError(f"Тип квантования {self.config.quantized_dtype} не поддерживается. "
                           f"Доступны: {list(self.SUPPORTED_QUANT_TYPES.keys())}")
        
        # Автовыбор алгоритма квантования
        if self.config.quantized_algorithm == "normal":
            recommended = self.SUPPORTED_QUANT_TYPES[self.config.quantized_dtype]["algorithm"]
            if recommended == "grq":
                print(f"⚠ Предупреждение: Для {self.config.quantized_dtype} рекомендуется алгоритм 'grq'")
    
    def _log(self, message: str, level: str = "INFO"):
        """Логирование"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def _get_output_filename(self) -> str:
        """Генерация имени выходного файла"""
        model_name = Path(self.config.model_path).name
        quant_prefix = f"_{self.config.quantized_dtype}" if self.config.do_quantization else ""
        return f"{model_name}{quant_prefix}_{self.config.target_platform}.rkllm"
    
    def _create_default_dataset(self, path: str) -> bool:
        """Создание датасета по умолчанию для квантования"""
        default_data = [
            {"input": "Human: Привет! Как тебя зовут?\nAssistant: ", "target": "Привет! Я языковая модель, обученная для работы на устройствах с NPU Rockchip."},
            {"input": "Human: Что ты умеешь делать?\nAssistant: ", "target": "Я могу отвечать на вопросы, помогать с текстом, объяснять концепции и поддерживать беседу."},
            {"input": "Human: Расскажи о себе.\nAssistant: ", "target": "Я компактная языковая модель, оптимизированная для работы на edge-устройствах."},
            {"input": "Human: Какой у тебя размер контекста?\nAssistant: ", "target": "Я поддерживаю контекст до 4096 токенов."},
            {"input": "Human: На каких устройствах ты работаешь?\nAssistant: ", "target": "Я работаю на устройствах с процессором Rockchip RK3588, RK3576, RK3562 и RV1126B."},
            {"input": "Human: Быстро ли ты отвечаешь?\nAssistant: ", "target": "На RK3588 я генерирую от 5 до 40 токенов в секунду."},
            {"input": "Human: Сколько памяти ты используешь?\nAssistant: ", "target": "В зависимости от размера модели я занимаю от 500 МБ до 6 ГБ."},
            {"input": "Human: Можешь ли ты работать на русском?\nAssistant: ", "target": "Да, я поддерживаю множественные языки, включая русский и английский."},
        ]
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self._log(f"Ошибка создания датасета: {e}", "ERROR")
            return False
    
    def load_model(self) -> bool:
        """Загрузка модели из HuggingFace"""
        self._log("=" * 60)
        self._log("Этап 1/3: Загрузка модели")
        self._log("=" * 60)
        
        # Проверка доступности RKLLM
        if not RKLLM_AVAILABLE:
            self._log("RKLLM не установлен - пропускаем загрузку (тестовый режим)", "WARNING")
            return True
        
        # Проверка пути к модели
        if not os.path.exists(self.config.model_path):
            self._log(f"Путь к модели не найден: {self.config.model_path}", "ERROR")
            self._log("Скачайте модель с HuggingFace или укажите правильный путь", "ERROR")
            return False
        
        # Установка GPU устройства
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        
        self._log(f"Модель: {self.config.model_path}")
        self._log(f"Устройство: {self.config.device}")
        self._log(f"Тип данных: {self.config.dtype}")
        
        try:
            self.llm = RKLLM()
            
            ret = self.llm.load_huggingface(
                model=self.config.model_path,
                model_lora=None,
                device=self.config.device,
                dtype=self.config.dtype,
                custom_config=self.config.custom_config,
                load_weight=True
            )
            
            if ret != 0:
                self._log(f"Ошибка загрузки модели! Код: {ret}", "ERROR")
                return False
            
            self._log("✓ Модель успешно загружена", "SUCCESS")
            return True
            
        except Exception as e:
            self._log(f"Исключение при загрузке: {e}", "ERROR")
            return False
    
    def build_model(self) -> bool:
        """Построение и квантование модели"""
        self._log("=" * 60)
        self._log("Этап 2/3: Построение модели")
        self._log("=" * 60)
        
        # Проверка/создание датасета
        dataset_file = self.config.dataset_file
        
        if self.config.do_quantization:
            if not dataset_file or not os.path.exists(dataset_file):
                self._log("Датасет для квантования не найден, создаю стандартный...", "WARNING")
                dataset_file = os.path.join(self.config.output_dir, "data_quant.json")
                
                if not self._create_default_dataset(dataset_file):
                    self._log("Не удалось создать датасет, продолжаю без квантования", "WARNING")
                    self.config.do_quantization = False
                else:
                    self._log(f"Датасет создан: {dataset_file}", "INFO")
        
        self._log(f"Квантование: {self.config.do_quantization}")
        self._log(f"Тип квантования: {self.config.quantized_dtype}")
        self._log(f"Алгоритм: {self.config.quantized_algorithm}")
        self._log(f"Платформа: {self.config.target_platform}")
        self._log(f"Ядер NPU: {self.config.num_npu_core}")
        self._log(f"Уровень оптимизации: {self.config.optimization_level}")
        self._log(f"Макс. контекст: {self.config.max_context}")
        
        try:
            ret = self.llm.build(
                do_quantization=self.config.do_quantization,
                optimization_level=self.config.optimization_level,
                quantized_dtype=self.config.quantized_dtype,
                quantized_algorithm=self.config.quantized_algorithm,
                target_platform=self.config.target_platform,
                num_npu_core=self.config.num_npu_core,
                dataset=dataset_file if self.config.do_quantization else None,
                hybrid_rate=self.config.hybrid_rate,
                max_context=self.config.max_context
            )
            
            if ret != 0:
                self._log(f"Ошибка построения модели! Код: {ret}", "ERROR")
                return False
            
            self._log("✓ Модель успешно построена", "SUCCESS")
            return True
            
        except Exception as e:
            self._log(f"Исключение при построении: {e}", "ERROR")
            return False
    
    def export_model(self) -> bool:
        """Экспорт модели в RKLLM формат"""
        self._log("=" * 60)
        self._log("Этап 3/3: Экспорт модели")
        self._log("=" * 60)
        
        output_path = os.path.join(self.config.output_dir, self._get_output_filename())
        
        # Создание директории вывода
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        self._log(f"Выходной файл: {output_path}")
        
        try:
            ret = self.llm.export_rkllm(output_path)
            
            if ret != 0:
                self._log(f"Ошибка экспорта модели! Код: {ret}", "ERROR")
                return False
            
            # Информация о файле
            if os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                self._log(f"✓ Модель успешно экспортирована", "SUCCESS")
                self._log(f"Размер файла: {size_mb:.2f} MB", "INFO")
            
            return True
            
        except Exception as e:
            self._log(f"Исключение при экспорте: {e}", "ERROR")
            return False
    
    def convert(self) -> bool:
        """Полный процесс конвертации"""
        self.start_time = datetime.now()
        
        self._log("")
        self._log("🚀 Запуск конвертации модели в RKLLM", "INFO")
        self._log(f"Время начала: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        self._log("")
        
        # Этапы конвертации
        if not self.load_model():
            return False
        
        if not self.build_model():
            return False
        
        if not self.export_model():
            return False
        
        # Завершение
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        self._log("")
        self._log("=" * 60)
        self._log("✓ Конвертация завершена успешно!", "SUCCESS")
        self._log(f"Время выполнения: {duration}", "INFO")
        self._log("=" * 60)
        
        return True
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.llm:
            del self.llm


def parse_args() -> argparse.Namespace:
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Конвертация моделей из HuggingFace в формат RKLLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Конвертация модели Qwen2.5 с квантованием W8A8 для RK3588
  python convert_hf_model.py --model Qwen/Qwen2.5-1.5B-Instruct --platform RK3588
  
  # Конвертация с указанием пути к локальной модели
  python convert_hf_model.py --model /path/to/model --output ./outputs
  
  # Конвертация без квантования (FP16)
  python convert_hf_model.py --model Qwen/Qwen2.5-0.5B-Instruct --no-quant
  
  # Конвертация с 4-битным квантованием
  python convert_hf_model.py --model TinyLlama/TinyLlama-1.1B-Chat-v1.0 --quant W4A16

Поддерживаемые платформы: RK3588, RK3576, RK3562, RV1126B
Поддерживаемые типы квантования: W8A8, W4A16, W4A16_G128
        """
    )
    
    # Обязательные аргументы
    parser.add_argument(
        '--model', '-m',
        type=str,
        required=True,
        help='Путь к модели (локальный путь или название на HuggingFace)'
    )
    
    # Опциональные аргументы
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./outputs',
        help='Директория для сохранения RKLLM модели (по умолчанию: ./outputs)'
    )
    
    parser.add_argument(
        '--platform', '-p',
        type=str,
        choices=['RK3588', 'RK3576', 'RK3562', 'RV1126B'],
        default='RK3588',
        help='Целевая платформа (по умолчанию: RK3588)'
    )
    
    parser.add_argument(
        '--quant', '-q',
        type=str,
        choices=['W8A8', 'W4A16', 'W4A16_G128', 'W8A8_G128'],
        default='W8A8',
        help='Тип квантования (по умолчанию: W8A8)'
    )
    
    parser.add_argument(
        '--algorithm', '-a',
        type=str,
        choices=['normal', 'grq'],
        default=None,
        help='Алгоритм квантования (автовыбор по умолчанию)'
    )
    
    parser.add_argument(
        '--dataset', '-d',
        type=str,
        default=None,
        help='Путь к JSON файлу с данными для квантования'
    )
    
    parser.add_argument(
        '--no-quant',
        action='store_true',
        help='Отключить квантование (использовать FP16)'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        default='cuda',
        help='Устройство для конвертации (по умолчанию: cuda)'
    )
    
    parser.add_argument(
        '--dtype',
        type=str,
        choices=['float32', 'float16', 'bfloat16'],
        default='float32',
        help='Тип данных для загрузки модели (по умолчанию: float32)'
    )
    
    parser.add_argument(
        '--context',
        type=int,
        default=4096,
        help='Максимальный размер контекста (по умолчанию: 4096)'
    )
    
    parser.add_argument(
        '--npu-cores',
        type=int,
        choices=[1, 2, 3],
        default=3,
        help='Количество ядер NPU (по умолчанию: 3)'
    )
    
    parser.add_argument(
        '--opt-level',
        type=int,
        choices=[0, 1],
        default=1,
        help='Уровень оптимизации: 0-минимальный, 1-агрессивный (по умолчанию: 1)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Тихий режим (минимальный вывод)'
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Определение уровня verbosity
    verbose = not args.quiet
    if args.verbose:
        verbose = True
    
    # Автовыбор алгоритма квантования
    algorithm = args.algorithm
    if algorithm is None:
        quant_info = ModelConverter.SUPPORTED_QUANT_TYPES.get(args.quant, {})
        algorithm = quant_info.get("algorithm", "normal")
    
    # Создание конфигурации
    config = ConversionConfig(
        model_path=args.model,
        output_dir=args.output,
        target_platform=args.platform,
        quantized_dtype=args.quant,
        quantized_algorithm=algorithm,
        optimization_level=args.opt_level,
        num_npu_core=args.npu_cores,
        max_context=args.context,
        device=args.device,
        dtype=args.dtype,
        dataset_file=args.dataset,
        do_quantization=not args.no_quant,
    )
    
    # Вывод конфигурации
    if verbose:
        print("\n" + "=" * 70)
        print("  Конфигурация конвертации")
        print("=" * 70)
        for key, value in config.to_dict().items():
            if value is not None:
                print(f"  {key}: {value}")
        print("=" * 70 + "\n")
    
    # Запуск конвертации
    converter = ModelConverter(config, verbose=verbose)
    
    try:
        success = converter.convert()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠ Конвертация прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        converter.cleanup()


if __name__ == "__main__":
    main()
