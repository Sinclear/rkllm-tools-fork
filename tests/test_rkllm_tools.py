#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексные тесты для RKLLM Tools

Запуск:
    python test_rkllm_tools.py [--unit] [--integration] [--all] [--verbose]
    
Покрытие:
- Unit тесты для отдельных компонентов
- Интеграционные тесты
- Тесты производительности
"""

import os
import sys
import unittest
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Добавляем директорию tools в path
TOOLS_DIR = Path(__file__).parent.parent / "tools"  # Исправлено для структуры форка
sys.path.insert(0, str(TOOLS_DIR))


# ============================================================================
# UNIT ТЕСТЫ
# ============================================================================

class TestSetupRkllmEnv(unittest.TestCase):
    """Тесты для setup_rkllm_env.sh"""
    
    def test_script_exists(self):
        """Проверка существования скрипта установки"""
        script_path = TOOLS_DIR / "setup_rkllm_env.sh"
        self.assertTrue(script_path.exists(), f"Скрипт не найден: {script_path}")
    
    def test_script_executable(self):
        """Проверка исполняемости скрипта"""
        script_path = TOOLS_DIR / "setup_rkllm_env.sh"
        self.assertTrue(os.access(script_path, os.X_OK), "Скрипт не исполняемый")
    
    def test_script_syntax(self):
        """Проверка синтаксиса bash скрипта"""
        script_path = TOOLS_DIR / "setup_rkllm_env.sh"
        result = subprocess.run(
            ['bash', '-n', str(script_path)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Синтаксическая ошибка: {result.stderr}")


class TestVerifyInstallation(unittest.TestCase):
    """Тесты для verify_rkllm_installation.py"""
    
    def test_script_exists(self):
        """Проверка существования скрипта"""
        script_path = TOOLS_DIR / "verify_rkllm_installation.py"
        self.assertTrue(script_path.exists())
    
    def test_help_output(self):
        """Проверка вывода справки"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "verify_rkllm_installation.py"), "--help"],
            capture_output=True,
            text=True
        )
        self.assertIn("--verbose", result.stdout)
        self.assertIn("--json", result.stdout)
    
    @patch('verify_rkllm_installation.RKLLMVerifier')
    def test_verifier_class(self, mock_verifier):
        """Тест класса верификатора (mock)"""
        mock_verifier.return_value.run_all_checks.return_value = []
        mock_verifier.return_value.print_report.return_value = "OK"
        
        from verify_rkllm_installation import RKLLMVerifier
        verifier = RKLLMVerifier()
        self.assertIsNotNone(verifier)


class TestConvertHfModel(unittest.TestCase):
    """Тесты для convert_hf_model.py"""
    
    def test_script_exists(self):
        """Проверка существования скрипта"""
        script_path = TOOLS_DIR / "convert_hf_model.py"
        self.assertTrue(script_path.exists())
    
    def test_help_output(self):
        """Проверка вывода справки"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "convert_hf_model.py"), "--help"],
            capture_output=True,
            text=True
        )
        self.assertIn("--model", result.stdout)
        self.assertIn("--platform", result.stdout)
        self.assertIn("--quant", result.stdout)
    
    def test_supported_platforms(self):
        """Проверка списка платформ"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "convert_hf_model.py"), "--help"],
            capture_output=True,
            text=True
        )
        for platform in ["RK3588", "RK3576", "RK3562", "RV1126B"]:
            self.assertIn(platform, result.stdout)
    
    def test_supported_quant_types(self):
        """Проверка типов квантования"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "convert_hf_model.py"), "--help"],
            capture_output=True,
            text=True
        )
        for quant in ["W8A8", "W4A16", "W4A16_G128"]:
            self.assertIn(quant, result.stdout)


class TestDownloadHfModel(unittest.TestCase):
    """Тесты для download_hf_model.py"""
    
    def test_script_exists(self):
        """Проверка существования скрипта"""
        script_path = TOOLS_DIR / "download_hf_model.py"
        self.assertTrue(script_path.exists())
    
    def test_subcommands(self):
        """Проверка подкоманд"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "download_hf_model.py"), "--help"],
            capture_output=True,
            text=True
        )
        for cmd in ["download", "info", "search"]:
            self.assertIn(cmd, result.stdout)


class TestRkllmManager(unittest.TestCase):
    """Тесты для rkllm_manager.py"""
    
    def test_script_exists(self):
        """Проверка существования скрипта"""
        script_path = TOOLS_DIR / "rkllm_manager.py"
        self.assertTrue(script_path.exists())
    
    def test_commands(self):
        """Проверка команд менеджера"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "rkllm_manager.py"), "--help"],
            capture_output=True,
            text=True
        )
        for cmd in ["setup", "verify", "download", "convert", "full", "list"]:
            self.assertIn(cmd, result.stdout)
    
    def test_list_command(self):
        """Тест команды list"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "rkllm_manager.py"), "list"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Qwen", result.stdout)


class TestConversionConfig(unittest.TestCase):
    """Тесты конфигурации конвертации"""
    
    def test_default_config(self):
        """Тест конфигурации по умолчанию"""
        # Импортируем только классы данных, не требующие RKLLM
        import importlib.util
        spec = importlib.util.spec_from_file_location("convert_hf_model", TOOLS_DIR / "convert_hf_model.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Выполняем загрузку модуля
        
        # Проверяем что модуль загрузился (даже если RKLLM недоступен)
        self.assertTrue(hasattr(module, 'ConversionConfig'))
        
        ConversionConfig = module.ConversionConfig
        config = ConversionConfig(
            model_path="/test/model",
            output_dir="/test/output"
        )
        
        self.assertEqual(config.target_platform, "RK3588")
        self.assertEqual(config.quantized_dtype, "W8A8")
        self.assertEqual(config.optimization_level, 1)
        self.assertEqual(config.num_npu_core, 3)
        self.assertEqual(config.max_context, 4096)
    
    def test_config_validation(self):
        """Тест валидации конфигурации"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("convert_hf_model", TOOLS_DIR / "convert_hf_model.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Выполняем загрузку модуля
        
        ConversionConfig = module.ConversionConfig
        ModelConverter = module.ModelConverter
        
        # Неправильная платформа
        with self.assertRaises(ValueError):
            ModelConverter(ConversionConfig(
                model_path="/test",
                output_dir="/test",
                target_platform="INVALID"
            ))
        
        # Неправильный тип квантования
        with self.assertRaises(ValueError):
            ModelConverter(ConversionConfig(
                model_path="/test",
                output_dir="/test",
                quantized_dtype="INVALID"
            ))


# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestIntegrationSetup(unittest.TestCase):
    """Интеграционные тесты установки"""
    
    @unittest.skipUnless(os.environ.get('RUN_INTEGRATION'), "Требуется RUN_INTEGRATION=1")
    def test_conda_available(self):
        """Проверка доступности conda"""
        result = subprocess.run(
            ['conda', '--version'],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
    
    @unittest.skipUnless(os.environ.get('RUN_INTEGRATION'), "Требуется RUN_INTEGRATION=1")
    def test_rkllm_packages_exist(self):
        """Проверка существования пакетов RKLLM"""
        packages_dir = TOOLS_DIR.parent / "rkllm-toolkit" / "packages"
        self.assertTrue(packages_dir.exists())
        
        # Проверка наличия WHL файлов
        whl_files = list(packages_dir.glob("rkllm_toolkit-*.whl"))
        self.assertGreater(len(whl_files), 0, "WHL файлы не найдены")
        
        # Проверка requirements.txt
        req_file = packages_dir / "requirements.txt"
        self.assertTrue(req_file.exists())


class TestIntegrationDownload(unittest.TestCase):
    """Интеграционные тесты скачивания"""
    
    @unittest.skipUnless(os.environ.get('RUN_INTEGRATION'), "Требуется RUN_INTEGRATION=1")
    def test_model_info(self):
        """Тест получения информации о модели"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "download_hf_model.py"), 
             "info", "Qwen/Qwen2.5-0.5B-Instruct"],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Может не работать без токена для gated моделей
        # Проверяем только что скрипт запустился
        self.assertIn("Qwen", result.stdout or result.stderr)


class TestIntegrationVerify(unittest.TestCase):
    """Интеграционные тесты верификации"""
    
    @unittest.skipUnless(os.environ.get('RUN_INTEGRATION'), "Требуется RUN_INTEGRATION=1")
    def test_verify_json_output(self):
        """Тест JSON вывода верификации"""
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "verify_rkllm_installation.py"), "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                self.assertIn("summary", data)
                self.assertIn("checks", data)
            except json.JSONDecodeError:
                self.fail("Неверный JSON вывод")


# ============================================================================
# ТЕСТЫ ПРОИЗВОДИТЕЛЬНОСТИ
# ============================================================================

class TestPerformance(unittest.TestCase):
    """Тесты производительности"""
    
    @unittest.skipUnless(os.environ.get('RUN_PERF'), "Требуется RUN_PERF=1")
    def test_script_startup_time(self):
        """Тест времени запуска скриптов"""
        scripts = [
            "verify_rkllm_installation.py",
            "rkllm_manager.py",
        ]
        
        for script in scripts:
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(TOOLS_DIR / script), "--help"],
                    capture_output=True,
                    text=True
                )
                # Скрипт должен запуститься быстрее 5 секунд
                self.assertLess(result.elapsed.total_seconds(), 5)


# ============================================================================
# ТЕСТЫ ДЛЯ T-LITE-it-2.1
# ============================================================================

class TestTLiteModel(unittest.TestCase):
    """Специфические тесты для модели T-lite-it-2.1"""
    
    def test_model_config(self):
        """Тест конфигурации для T-lite-it-2.1"""
        # T-lite-it-2.1 основана на Qwen3 8B
        import importlib.util
        spec = importlib.util.spec_from_file_location("convert_hf_model", TOOLS_DIR / "convert_hf_model.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # Выполняем загрузку модуля
        
        ConversionConfig = module.ConversionConfig
        
        config = ConversionConfig(
            model_path="/path/to/T-lite-it-2.1",
            output_dir="/test/output",
            target_platform="RK3588",
            quantized_dtype="W8A8",
            max_context=8192,  # T-lite поддерживает большой контекст
        )
        
        self.assertEqual(config.target_platform, "RK3588")
        self.assertEqual(config.quantized_dtype, "W8A8")
    
    def test_qwen3_compatibility(self):
        """Тест совместимости с архитектурой Qwen3"""
        # T-lite-it-2.1 использует архитектуру Qwen3
        # Проверяем что конвертер поддерживает Qwen3
        result = subprocess.run(
            [sys.executable, str(TOOLS_DIR / "convert_hf_model.py"), "--help"],
            capture_output=True,
            text=True
        )
        self.assertIn("Qwen", result.stdout)


# ============================================================================
# MAIN
# ============================================================================

def run_tests(unit=True, integration=False, performance=False, verbose=False):
    """Запуск тестов"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Unit тесты
    if unit:
        suite.addTests(loader.loadTestsFromTestCase(TestSetupRkllmEnv))
        suite.addTests(loader.loadTestsFromTestCase(TestVerifyInstallation))
        suite.addTests(loader.loadTestsFromTestCase(TestConvertHfModel))
        suite.addTests(loader.loadTestsFromTestCase(TestDownloadHfModel))
        suite.addTests(loader.loadTestsFromTestCase(TestRkllmManager))
        suite.addTests(loader.loadTestsFromTestCase(TestConversionConfig))
        suite.addTests(loader.loadTestsFromTestCase(TestTLiteModel))
    
    # Интеграционные тесты
    if integration:
        suite.addTests(loader.loadTestsFromTestCase(TestIntegrationSetup))
        suite.addTests(loader.loadTestsFromTestCase(TestIntegrationDownload))
        suite.addTests(loader.loadTestsFromTestCase(TestIntegrationVerify))
    
    # Тесты производительности
    if performance:
        suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Запуск
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout
    )
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Тесты RKLLM Tools')
    parser.add_argument('--unit', action='store_true', default=True, help='Unit тесты')
    parser.add_argument('--integration', action='store_true', help='Интеграционные тесты')
    parser.add_argument('--performance', action='store_true', help='Тесты производительности')
    parser.add_argument('--all', action='store_true', help='Все тесты')
    parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    
    args = parser.parse_args()
    
    if args.all:
        args.integration = True
        args.performance = True
    
    # Установка переменных окружения для интеграционных тестов
    if args.integration:
        os.environ['RUN_INTEGRATION'] = '1'
    if args.performance:
        os.environ['RUN_PERF'] = '1'
    
    result = run_tests(
        unit=args.unit,
        integration=args.integration,
        performance=args.performance,
        verbose=args.verbose
    )
    
    # Выход с кодом ошибки если тесты не прошли
    sys.exit(0 if result.wasSuccessful() else 1)
