#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт проверки установки RKLLM Toolkit и всех зависимостей

Использование:
    python verify_rkllm_installation.py [--verbose] [--json]
"""

import sys
import subprocess
import importlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class CheckResult:
    name: str
    status: str  # "ok", "warning", "error"
    version: Optional[str] = None
    message: Optional[str] = None
    details: Optional[Dict] = None


class RKLLMVerifier:
    """Класс для комплексной проверки установки RKLLM"""
    
    REQUIRED_PACKAGES = {
        'rkllm': {'min_version': '1.2.3'},
        'torch': {'min_version': '2.6.0'},
        'transformers': {'min_version': '4.55.2'},
        'numpy': {'min_version': '1.23.1', 'max_version': '1.26.4'},
        'datasets': {'min_version': '4.1.1'},
        'accelerate': {'min_version': '1.0.1', 'max_version': '1.5.2'},
        'sentencepiece': {'min_version': '0.2.0'},
        'tiktoken': {'min_version': '0.7.0', 'max_version': '0.9.0'},
        'protobuf': {'min_version': '4.21.6', 'max_version': '4.25.4'},
    }
    
    OPTIONAL_PACKAGES = {
        'huggingface_hub': {'message': 'Для скачивания моделей с HF'},
        'pillow': {'message': 'Для работы с изображениями'},
        'timm': {'message': 'Для визуальных моделей'},
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[CheckResult] = []
        self.python_version = sys.version.split()[0]
        
    def check_python_version(self) -> CheckResult:
        """Проверка версии Python"""
        major, minor, *_ = map(int, self.python_version.split('.'))
        
        supported_versions = [(3, 9), (3, 10), (3, 11), (3, 12)]
        
        if (major, minor) in supported_versions:
            return CheckResult(
                name="Python",
                status="ok",
                version=self.python_version,
                message=f"Версия Python поддерживается"
            )
        else:
            return CheckResult(
                name="Python",
                status="error",
                version=self.python_version,
                message=f"Версия Python не поддерживается! Требуется 3.9-3.12"
            )
    
    def check_package(self, package_name: str, constraints: Dict) -> CheckResult:
        """Проверка установленного пакета"""
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'unknown')
            
            # Проверка минимальной версии
            if 'min_version' in constraints:
                if not self._version_gte(version, constraints['min_version']):
                    return CheckResult(
                        name=package_name,
                        status="error",
                        version=version,
                        message=f"Версия ниже требуемой {constraints['min_version']}"
                    )
            
            # Проверка максимальной версии
            if 'max_version' in constraints:
                if not self._version_lte(version, constraints['max_version']):
                    return CheckResult(
                        name=package_name,
                        status="warning",
                        version=version,
                        message=f"Версия выше рекомендуемой {constraints['max_version']}"
                    )
            
            return CheckResult(
                name=package_name,
                status="ok",
                version=version,
                message="Версия соответствует требованиям"
            )
            
        except ImportError as e:
            return CheckResult(
                name=package_name,
                status="error",
                message=f"Пакет не установлен: {str(e)}"
            )
    
    def check_cuda(self) -> CheckResult:
        """Проверка доступности CUDA"""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            cuda_version = torch.version.cuda if cuda_available else None
            
            details = {
                'available': cuda_available,
                'version': cuda_version,
            }
            
            if cuda_available:
                details['device_count'] = torch.cuda.device_count()
                if torch.cuda.device_count() > 0:
                    details['device_name'] = torch.cuda.get_device_name(0)
                    details['memory_total_gb'] = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2)
            
            return CheckResult(
                name="CUDA",
                status="ok" if cuda_available else "warning",
                version=cuda_version,
                message="CUDA доступна" if cuda_available else "CUDA недоступна (конвертация на CPU)",
                details=details
            )
        except Exception as e:
            return CheckResult(
                name="CUDA",
                status="error",
                message=f"Ошибка проверки CUDA: {str(e)}"
            )
    
    def check_rkllm_api(self) -> CheckResult:
        """Проверка RKLLM API"""
        try:
            from rkllm.api import RKLLM
            
            # Проверка создания экземпляра
            llm = RKLLM()
            
            return CheckResult(
                name="RKLLM API",
                status="ok",
                version="1.2.3",
                message="RKLLM API инициализирован успешно"
            )
        except ImportError as e:
            return CheckResult(
                name="RKLLM API",
                status="error",
                message=f"RKLLM не установлен: {str(e)}"
            )
        except Exception as e:
            return CheckResult(
                name="RKLLM API",
                status="error",
                message=f"Ошибка инициализации RKLLM: {str(e)}"
            )
    
    def check_disk_space(self, path: str = "/tmp", min_gb: float = 10.0) -> CheckResult:
        """Проверка свободного места на диске"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            free_gb = free / (1024**3)
            
            details = {
                'total_gb': round(total / 1024**3, 2),
                'used_gb': round(used / 1024**3, 2),
                'free_gb': round(free_gb, 2),
                'min_required_gb': min_gb
            }
            
            if free_gb >= min_gb:
                return CheckResult(
                    name="Disk Space",
                    status="ok",
                    message=f"Достаточно свободного места: {free_gb:.2f} GB",
                    details=details
                )
            else:
                return CheckResult(
                    name="Disk Space",
                    status="warning",
                    message=f"Мало свободного места: {free_gb:.2f} GB (рекомендуется {min_gb} GB)",
                    details=details
                )
        except Exception as e:
            return CheckResult(
                name="Disk Space",
                status="error",
                message=f"Ошибка проверки диска: {str(e)}"
            )
    
    def check_memory(self, min_gb: float = 8.0) -> CheckResult:
        """Проверка доступной памяти"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            available_gb = mem.available / (1024**3)
            
            details = {
                'total_gb': round(mem.total / 1024**3, 2),
                'available_gb': round(available_gb, 2),
                'percent_used': mem.percent,
                'min_required_gb': min_gb
            }
            
            if available_gb >= min_gb:
                return CheckResult(
                    name="RAM",
                    status="ok",
                    message=f"Достаточно памяти: {available_gb:.2f} GB",
                    details=details
                )
            else:
                return CheckResult(
                    name="RAM",
                    status="warning",
                    message=f"Мало памяти: {available_gb:.2f} GB (рекомендуется {min_gb} GB)",
                    details=details
                )
        except ImportError:
            return CheckResult(
                name="RAM",
                status="warning",
                message="psutil не установлен (проверка памяти пропущена)"
            )
        except Exception as e:
            return CheckResult(
                name="RAM",
                status="error",
                message=f"Ошибка проверки памяти: {str(e)}"
            )
    
    def _version_gte(self, version: str, min_version: str) -> bool:
        """Проверка: version >= min_version"""
        return self._parse_version(version) >= self._parse_version(min_version)
    
    def _version_lte(self, version: str, max_version: str) -> bool:
        """Проверка: version <= max_version"""
        return self._parse_version(version) <= self._parse_version(max_version)
    
    def _parse_version(self, version: str) -> Tuple:
        """Парсинг версии в кортеж чисел"""
        try:
            # Удаление суффиксов типа .dev0, +cu118 и т.д.
            base_version = version.split('+')[0].split('.dev')[0].split('.post')[0]
            return tuple(map(int, base_version.split('.')[:3]))
        except:
            return (0, 0, 0)
    
    def run_all_checks(self) -> List[CheckResult]:
        """Запуск всех проверок"""
        self.results = []
        
        # Базовые проверки
        self.results.append(self.check_python_version())
        self.results.append(self.check_cuda())
        self.results.append(self.check_disk_space())
        
        try:
            self.results.append(self.check_memory())
        except:
            pass
        
        # Проверка RKLLM
        self.results.append(self.check_rkllm_api())
        
        # Проверка обязательных пакетов
        for package, constraints in self.REQUIRED_PACKAGES.items():
            self.results.append(self.check_package(package, constraints))
        
        # Проверка опциональных пакетов
        for package, info in self.OPTIONAL_PACKAGES.items():
            result = self.check_package(package, {})
            if result.status == "error":
                result.status = "warning"
                result.message = f"Не установлен ({info['message']})"
            self.results.append(result)
        
        return self.results
    
    def print_report(self, json_output: bool = False) -> str:
        """Вывод отчета"""
        if json_output:
            report = {
                'summary': {
                    'total': len(self.results),
                    'ok': sum(1 for r in self.results if r.status == 'ok'),
                    'warnings': sum(1 for r in self.results if r.status == 'warning'),
                    'errors': sum(1 for r in self.results if r.status == 'error'),
                },
                'checks': [asdict(r) for r in self.results]
            }
            return json.dumps(report, indent=2, ensure_ascii=False)
        
        # Текстовый отчет
        lines = []
        lines.append("=" * 70)
        lines.append("  RKLLM Installation Verification Report")
        lines.append("=" * 70)
        lines.append("")
        
        ok_count = sum(1 for r in self.results if r.status == 'ok')
        warn_count = sum(1 for r in self.results if r.status == 'warning')
        error_count = sum(1 for r in self.results if r.status == 'error')
        
        lines.append(f"Всего проверок: {len(self.results)}")
        lines.append(f"✓ Успешно: {ok_count}")
        lines.append(f"⚠ Предупреждения: {warn_count}")
        lines.append(f"✗ Ошибки: {error_count}")
        lines.append("")
        lines.append("-" * 70)
        
        for result in self.results:
            icon = "✓" if result.status == "ok" else "⚠" if result.status == "warning" else "✗"
            status_color = "OK" if result.status == "ok" else "WARNING" if result.status == "warning" else "ERROR"
            
            version_str = f" (v{result.version})" if result.version else ""
            lines.append(f"{icon} [{status_color}] {result.name}{version_str}")
            
            if result.message:
                lines.append(f"    {result.message}")
            
            if self.verbose and result.details:
                for key, value in result.details.items():
                    lines.append(f"    {key}: {value}")
            
            lines.append("")
        
        lines.append("-" * 70)
        
        if error_count > 0:
            lines.append("❌ Обнаружены критические ошибки! Установка неполная.")
        elif warn_count > 0:
            lines.append("⚠ Обнаружены предупреждения. Рекомендуется проверить конфигурацию.")
        else:
            lines.append("✅ Все проверки пройдены успешно! Окружение готово к работе.")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Проверка установки RKLLM')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    parser.add_argument('--json', action='store_true', help='Вывод в формате JSON')
    parser.add_argument('--output', '-o', type=str, help='Сохранить отчет в файл')
    
    args = parser.parse_args()
    
    verifier = RKLLMVerifier(verbose=args.verbose)
    verifier.run_all_checks()
    
    report = verifier.print_report(json_output=args.json)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Отчет сохранен в: {args.output}")
    else:
        print(report)
    
    # Выход с кодом ошибки если есть критические проблемы
    error_count = sum(1 for r in verifier.results if r.status == 'error')
    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
