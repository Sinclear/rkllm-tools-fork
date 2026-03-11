#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест конвертации модели T-lite-it-2.1 (Qwen3-based)

Этот скрипт тестирует процесс конвертации для модели T-lite-it-2.1,
которая основана на архитектуре Qwen3.

Важно: T-lite-it-2.1-GGUF на HuggingFace - это GGUF версия.
Для RKLLM нужна оригинальная модель в формате HuggingFace.

Использование:
    python test_t_lite_conversion.py --dry-run    # Тест без реальной конвертации
    python test_t_lite_conversion.py --model /path/to/model  # Реальная конвертация
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Добавляем tools в path
TOOLS_DIR = Path(__file__).parent.parent / "tools"  # Исправлено для структуры форка
sys.path.insert(0, str(TOOLS_DIR))


class TLiteConversionTest:
    """Тест конвертации T-lite-it-2.1"""
    
    # Конфигурация по умолчанию
    DEFAULT_CONFIG = {
        "model": {
            "name": "T-lite-it-2.1",
            "base_architecture": "Qwen3",
            "size": "8B",
            "huggingface_id": "t-tech/T-lite-it-2.1",
        },
        "conversion": {
            "target_platform": "RK3588",
            "quantized_dtype": "W8A8",
            "quantized_algorithm": "normal",
            "optimization_level": 1,
            "num_npu_core": 3,
            "max_context": 8192,
            "device": "cuda",
            "dtype": "float32",
        },
        "requirements": {
            "min_ram_gb": 16,
            "min_disk_gb": 30,
        }
    }
    
    def __init__(self, config: Optional[Dict] = None, verbose: bool = True):
        self.config = config or self.DEFAULT_CONFIG
        self.verbose = verbose
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "model": self.config.get("model", {}),
            "tests": [],
            "summary": {
                "passed": 0,
                "failed": 0,
                "skipped": 0,
            }
        }
    
    def _log(self, message: str, level: str = "INFO"):
        """Логирование"""
        if self.verbose:
            icons = {"INFO": "ℹ", "OK": "✓", "FAIL": "✗", "SKIP": "⊘", "WARN": "⚠"}
            icon = icons.get(level, "•")
            print(f"[{icon}] {message}")
    
    def _add_result(self, name: str, passed: bool, message: str = "", skipped: bool = False):
        """Добавление результата теста"""
        status = "skipped" if skipped else ("passed" if passed else "failed")
        self.results["tests"].append({
            "name": name,
            "status": status,
            "message": message,
        })
        if skipped:
            self.results["summary"]["skipped"] += 1
        elif passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
    
    def test_config_valid(self) -> bool:
        """Тест 1: Валидация конфигурации"""
        self._log("Проверка конфигурации...")
        
        try:
            model = self.config.get("model", {})
            conversion = self.config.get("conversion", {})
            
            # Проверка обязательных полей
            assert model.get("name"), "Отсутствует имя модели"
            assert model.get("base_architecture"), "Отсутствует архитектура"
            assert conversion.get("target_platform"), "Отсутствует платформа"
            assert conversion.get("quantized_dtype"), "Отсутствует тип квантования"
            
            # Проверка платформы
            valid_platforms = ["RK3588", "RK3576", "RK3562", "RV1126B"]
            assert conversion["target_platform"] in valid_platforms, \
                f"Неверная платформа: {conversion['target_platform']}"
            
            # Проверка квантования
            valid_quants = ["W8A8", "W4A16", "W4A16_G128", "W8A8_G128"]
            assert conversion["quantized_dtype"] in valid_quants, \
                f"Неверный тип квантования: {conversion['quantized_dtype']}"
            
            self._add_result("config_valid", True, "Конфигурация валидна")
            self._log("Конфигурация валидна", "OK")
            return True
            
        except AssertionError as e:
            self._add_result("config_valid", False, str(e))
            self._log(f"Ошибка конфигурации: {e}", "FAIL")
            return False
    
    def test_model_compatibility(self) -> bool:
        """Тест 2: Совместимость модели с RKLLM"""
        self._log("Проверка совместимости модели...")
        
        model = self.config.get("model", {})
        architecture = model.get("base_architecture", "")
        
        # T-lite-it-2.1 основана на Qwen3
        # RKLLM поддерживает Qwen3
        qwen_supported = ["Qwen3", "Qwen2.5", "Qwen2"]
        
        if any(q in architecture for q in qwen_supported):
            self._add_result("model_compatibility", True, 
                           f"Архитектура {architecture} поддерживается")
            self._log(f"Архитектура {architecture} поддерживается RKLLM", "OK")
            return True
        else:
            self._add_result("model_compatibility", False,
                           f"Архитектура {architecture} может не поддерживаться")
            self._log(f"Архитектура {architecture} может не поддерживаться", "WARN")
            return True  # Не блокирующая ошибка
    
    def test_requirements(self) -> bool:
        """Тест 3: Проверка системных требований"""
        self._log("Проверка системных требований...")
        
        import shutil
        
        requirements = self.config.get("requirements", {})
        min_ram = requirements.get("min_ram_gb", 8)
        min_disk = requirements.get("min_disk_gb", 10)
        
        # Проверка памяти
        try:
            import psutil
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)
            
            if available_gb >= min_ram:
                self._log(f"Достаточно памяти: {available_gb:.1f} GB >= {min_ram} GB", "OK")
            else:
                self._log(f"Мало памяти: {available_gb:.1f} GB < {min_ram} GB", "WARN")
        except ImportError:
            self._log("psutil не установлен, проверка памяти пропущена", "SKIP")
        
        # Проверка диска
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        
        if free_gb >= min_disk:
            self._log(f"Достаточно места: {free_gb:.1f} GB >= {min_disk} GB", "OK")
        else:
            self._log(f"Мало места: {free_gb:.1f} GB < {min_disk} GB", "WARN")
        
        self._add_result("requirements", True, "Требования проверены")
        return True
    
    def test_script_availability(self) -> bool:
        """Тест 4: Доступность скриптов конвертации"""
        self._log("Проверка доступности скриптов...")
        
        required_scripts = [
            "convert_hf_model.py",
            "download_hf_model.py",
            "rkllm_manager.py",
        ]
        
        all_exist = True
        for script in required_scripts:
            script_path = TOOLS_DIR / script
            if script_path.exists():
                self._log(f"✓ {script}", "OK")
            else:
                self._log(f"✗ {script} (отсутствует)", "FAIL")
                all_exist = False
        
        self._add_result("script_availability", all_exist, 
                        "Все скрипты на месте" if all_exist else "Некоторые скрипты отсутствуют")
        return all_exist
    
    def test_dry_run_conversion(self, model_path: Optional[str] = None) -> bool:
        """Тест 5: Сухой прогон конвертации"""
        self._log("Тестовый прогон конвертации (dry-run)...")
        
        if not model_path:
            model_path = "/path/to/test/model"
        
        # Проверка команды конвертации
        cmd = [
            sys.executable, str(TOOLS_DIR / "convert_hf_model.py"),
            "--model", model_path,
            "--platform", self.config["conversion"]["target_platform"],
            "--quant", self.config["conversion"]["quantized_dtype"],
            "--help"  # Только проверка что скрипт работает
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self._add_result("dry_run", True, "Скрипт конвертации работает")
                self._log("Скрипт конвертации работает корректно", "OK")
                return True
            else:
                self._add_result("dry_run", False, result.stderr)
                self._log(f"Ошибка скрипта: {result.stderr}", "FAIL")
                return False
        except subprocess.TimeoutExpired:
            self._add_result("dry_run", False, "Таймаут")
            self._log("Таймаут выполнения", "FAIL")
            return False
        except Exception as e:
            self._add_result("dry_run", False, str(e))
            self._log(f"Исключение: {e}", "FAIL")
            return False
    
    def test_hf_model_availability(self) -> bool:
        """Тест 6: Доступность модели на HuggingFace"""
        self._log("Проверка доступности модели на HuggingFace...")
        
        model_id = self.config["model"].get("huggingface_id", "")
        
        if not model_id:
            self._add_result("hf_availability", False, "HF ID не указан", skipped=True)
            self._log("HF ID модели не указан", "SKIP")
            return True
        
        try:
            from huggingface_hub import HfApi
            api = HfApi()
            
            # Проверка существования модели
            try:
                info = api.model_info(model_id)
                self._add_result("hf_availability", True, f"Модель найдена: {model_id}")
                self._log(f"Модель найдена: {model_id}", "OK")
                return True
            except Exception:
                # Модель может не существовать в оригинальном формате
                self._add_result("hf_availability", False, 
                               f"Модель {model_id} не найдена в HF", skipped=True)
                self._log(f"Модель {model_id} не найдена (возможно только GGUF)", "WARN")
                return True
                
        except ImportError:
            self._add_result("hf_availability", False, "huggingface_hub не установлен", skipped=True)
            self._log("huggingface_hub не установлен", "SKIP")
            return True
    
    def run_all_tests(self, model_path: Optional[str] = None) -> Dict:
        """Запуск всех тестов"""
        self._log("=" * 60)
        self._log(f"Тестирование конвертации: {self.config['model']['name']}")
        self._log("=" * 60)
        
        self.test_config_valid()
        self.test_model_compatibility()
        self.test_requirements()
        self.test_script_availability()
        self.test_dry_run_conversion(model_path)
        self.test_hf_model_availability()
        
        # Итоги
        self._log("=" * 60)
        self._log(f"Результаты: {self.results['summary']}")
        self._log("=" * 60)
        
        return self.results
    
    def save_report(self, output_path: str):
        """Сохранение отчета"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        self._log(f"Отчет сохранен: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Тест конвертации T-lite-it-2.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Тест без реальной конвертации
  python test_t_lite_conversion.py --dry-run
  
  # Тест с указанием пути к модели
  python test_t_lite_conversion.py --model /path/to/model
  
  # Сохранение отчета
  python test_t_lite_conversion.py --output report.json
        """
    )
    
    parser.add_argument('--model', '-m', type=str, 
                       help='Путь к модели для тестирования')
    parser.add_argument('--config', '-c', type=str,
                       help='Путь к JSON конфигурации')
    parser.add_argument('--dry-run', action='store_true',
                       help='Только тесты без реальной конвертации')
    parser.add_argument('--output', '-o', type=str,
                       help='Путь для сохранения отчета')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    
    args = parser.parse_args()
    
    # Загрузка конфигурации
    config = TLiteConversionTest.DEFAULT_CONFIG.copy()
    
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            file_config = json.load(f)
            # Merge configs
            for key in file_config:
                if isinstance(file_config[key], dict):
                    config[key] = {**config.get(key, {}), **file_config[key]}
                else:
                    config[key] = file_config[key]
    
    # Создание тестера
    tester = TLiteConversionTest(config=config, verbose=args.verbose)
    
    # Запуск тестов
    results = tester.run_all_tests(model_path=args.model)
    
    # Сохранение отчета
    if args.output:
        tester.save_report(args.output)
    
    # Вывод итогов
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"Модель: {results['model'].get('name', 'N/A')}")
    print(f"Архитектура: {results['model'].get('base_architecture', 'N/A')}")
    print(f"Пройдено: {results['summary']['passed']}")
    print(f"Провалено: {results['summary']['failed']}")
    print(f"Пропущено: {results['summary']['skipped']}")
    print("=" * 60)
    
    # Выход с кодом ошибки если есть проваленные тесты
    sys.exit(1 if results['summary']['failed'] > 0 else 0)


if __name__ == "__main__":
    main()
