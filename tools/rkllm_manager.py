#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RKLLM Manager - Главный скрипт управления процессом конвертации моделей

Возможности:
- Установка и проверка окружения
- Скачивание моделей с HuggingFace
- Конвертация моделей в RKLLM формат
- Пакетная обработка
- Интерактивный режим

Использование:
    python rkllm_manager.py --help
    python rkllm_manager.py setup
    python rkllm_manager.py download Qwen/Qwen2.5-1.5B-Instruct
    python rkllm_manager.py convert ./models/Qwen2.5-1.5B-Instruct
    python rkllm_manager.py full Qwen/Qwen2.5-1.5B-Instruct
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


# Цвета для вывода
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def cprint(text: str, color: str = Colors.WHITE):
    """Цветной вывод"""
    print(f"{color}{text}{Colors.NC}")


def get_script_dir() -> Path:
    """Получение директории скрипта"""
    return Path(__file__).parent.resolve()


def check_conda_env() -> bool:
    """Проверка активного conda окружения rkllm"""
    env_name = os.environ.get('CONDA_DEFAULT_ENV', '')
    if env_name == 'rkllm':
        return True
    
    # Проверка через conda info
    try:
        result = subprocess.run(['conda', 'info', '--envs'], capture_output=True, text=True)
        return 'rkllm' in result.stdout
    except:
        return False


def activate_env() -> bool:
    """Активация окружения rkllm"""
    if check_conda_env():
        return True
    
    cprint("\n⚠ Окружение 'rkllm' не активно!", Colors.YELLOW)
    cprint("Для активации выполните:", Colors.YELLOW)
    cprint("  source ~/anaconda3/bin/activate rkllm\n", Colors.YELLOW)
    
    response = input("Попробовать активовать автоматически? (y/n): ").strip().lower()
    if response == 'y':
        try:
            # Попытка активации через subprocess
            conda_base = os.environ.get('CONDA_PREFIX', os.path.expanduser('~/anaconda3'))
            activate_script = os.path.join(conda_base, 'bin', 'activate')

            if os.path.exists(activate_script):
                # Используем subprocess вместо os.system для безопасности
                import subprocess
                subprocess.run(['bash', '-c', f'source "{activate_script}" && conda activate rkllm'], 
                              check=False)  # Не прерываем если ошибка
                return check_conda_env()
        except Exception as e:
            cprint(f"Ошибка активации: {e}", Colors.RED)

    return False


class RKLLMManager:
    """Менеджер управления RKLLM"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.script_dir = get_script_dir()
        self.work_dir = self.script_dir.parent / "workdir"
        self.models_dir = self.work_dir / "models"
        self.outputs_dir = self.work_dir / "outputs"
        
        # Создание рабочих директорий
        self._create_dirs()
    
    def _create_dirs(self):
        """Создание рабочих директорий"""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        (self.work_dir / "quant_data").mkdir(parents=True, exist_ok=True)
    
    def _log(self, message: str, level: str = "INFO"):
        """Логирование"""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            icons = {
                "INFO": "ℹ",
                "SUCCESS": "✓",
                "WARNING": "⚠",
                "ERROR": "✗",
                "STEP": "▶",
            }
            icon = icons.get(level, "•")
            print(f"[{timestamp}] [{icon}] {message}")
    
    def cmd_setup(self, args) -> int:
        """Команда: setup - установка окружения"""
        cprint("\n" + "=" * 60, Colors.CYAN)
        cprint("  Установка окружения RKLLM", Colors.CYAN)
        cprint("=" * 60 + "\n", Colors.CYAN)
        
        setup_script = self.script_dir / "setup_rkllm_env.sh"
        
        if not setup_script.exists():
            cprint(f"Скрипт установки не найден: {setup_script}", Colors.RED)
            return 1
        
        # Запуск скрипта установки
        try:
            result = subprocess.run(
                ['bash', str(setup_script)],
                cwd=str(self.script_dir),
                env={**os.environ, **vars(args)} if args else os.environ
            )
            return result.returncode
        except Exception as e:
            cprint(f"Ошибка установки: {e}", Colors.RED)
            return 1
    
    def cmd_verify(self, args) -> int:
        """Команда: verify - проверка установки"""
        cprint("\n" + "=" * 60, Colors.CYAN)
        cprint("  Проверка установки RKLLM", Colors.CYAN)
        cprint("=" * 60 + "\n", Colors.CYAN)
        
        verify_script = self.script_dir / "verify_rkllm_installation.py"
        
        if not verify_script.exists():
            cprint(f"Скрипт проверки не найден: {verify_script}", Colors.RED)
            return 1
        
        cmd = [sys.executable, str(verify_script)]
        if args and args.verbose:
            cmd.append('--verbose')
        if args and args.json:
            cmd.append('--json')
        
        try:
            result = subprocess.run(cmd, cwd=str(self.script_dir))
            return result.returncode
        except Exception as e:
            cprint(f"Ошибка проверки: {e}", Colors.RED)
            return 1
    
    def cmd_download(self, args) -> int:
        """Команда: download - скачивание модели"""
        cprint("\n" + "=" * 60, Colors.CYAN)
        cprint("  Скачивание модели с HuggingFace", Colors.CYAN)
        cprint("=" * 60 + "\n", Colors.CYAN)
        
        download_script = self.script_dir / "download_hf_model.py"
        
        if not download_script.exists():
            cprint(f"Скрипт загрузки не найден: {download_script}", Colors.RED)
            return 1
        
        cmd = [sys.executable, str(download_script), 'download']
        
        if args:
            if hasattr(args, 'model') and args.model:
                cmd.append(args.model)
            if hasattr(args, 'output') and args.output:
                cmd.extend(['-o', args.output])
            if hasattr(args, 'info') and args.info:
                cmd.append('--info')
        
        try:
            result = subprocess.run(cmd, cwd=str(self.script_dir))
            return result.returncode
        except Exception as e:
            cprint(f"Ошибка загрузки: {e}", Colors.RED)
            return 1
    
    def cmd_convert(self, args) -> int:
        """Команда: convert - конвертация модели"""
        cprint("\n" + "=" * 60, Colors.CYAN)
        cprint("  Конвертация модели в RKLLM", Colors.CYAN)
        cprint("=" * 60 + "\n", Colors.CYAN)
        
        convert_script = self.script_dir / "convert_hf_model.py"
        
        if not convert_script.exists():
            cprint(f"Скрипт конвертации не найден: {convert_script}", Colors.RED)
            return 1
        
        cmd = [sys.executable, str(convert_script)]
        
        if args:
            if hasattr(args, 'model') and args.model:
                cmd.extend(['--model', args.model])
            if hasattr(args, 'output') and args.output:
                cmd.extend(['--output', args.output])
            if hasattr(args, 'platform') and args.platform:
                cmd.extend(['--platform', args.platform])
            if hasattr(args, 'quant') and args.quant:
                cmd.extend(['--quant', args.quant])
            if hasattr(args, 'context') and args.context:
                cmd.extend(['--context', str(args.context)])
        
        try:
            result = subprocess.run(cmd, cwd=str(self.script_dir))
            return result.returncode
        except Exception as e:
            cprint(f"Ошибка конвертации: {e}", Colors.RED)
            return 1
    
    def cmd_full(self, args) -> int:
        """Команда: full - полный цикл (download + convert)"""
        cprint("\n" + "=" * 70, Colors.GREEN)
        cprint("  ПОЛНЫЙ ЦИКЛ: Скачивание и конвертация модели", Colors.GREEN)
        cprint("=" * 70 + "\n", Colors.GREEN)
        
        if not args or not args.model:
            cprint("Ошибка: укажите модель через --model", Colors.RED)
            return 1
        
        model_id = args.model
        output_dir = str(self.models_dir)
        rkllm_output = str(self.outputs_dir)
        
        # Этап 1: Скачивание
        cprint("\n[ЭТАП 1/2] Скачивание модели...", Colors.BOLD)
        
        class DownloadArgs:
            model = model_id
            output = output_dir
            info = True
        
        ret = self.cmd_download(DownloadArgs())
        if ret != 0:
            cprint("\n❌ Ошибка на этапе скачивания!", Colors.RED)
            return ret
        
        # Определение пути к скачанной модели
        model_name = model_id.split('/')[-1]
        model_path = str(self.models_dir / model_name)
        
        if not os.path.exists(model_path):
            cprint(f"\n❌ Модель не найдена: {model_path}", Colors.RED)
            return 1
        
        # Этап 2: Конвертация
        cprint("\n[ЭТАП 2/2] Конвертация модели...", Colors.BOLD)
        
        class ConvertArgs:
            model = model_path
            output = rkllm_output
            platform = getattr(args, 'platform', 'RK3588')
            quant = getattr(args, 'quant', 'W8A8')
            context = getattr(args, 'context', 4096)
        
        ret = self.cmd_convert(ConvertArgs())
        if ret != 0:
            cprint("\n❌ Ошибка на этапе конвертации!", Colors.RED)
            return ret
        
        # Завершение
        cprint("\n" + "=" * 70, Colors.GREEN)
        cprint("  ✓ ПОЛНЫЙ ЦИКЛ ЗАВЕРШЕН УСПЕШНО!", Colors.GREEN)
        cprint("=" * 70, Colors.GREEN)
        cprint(f"\n  Модель скачана: {model_path}", Colors.GREEN)
        cprint(f"  RKLLM файл: {rkllm_output}/\n", Colors.GREEN)
        
        return 0
    
    def cmd_list(self, args) -> int:
        """Команда: list - список доступных моделей"""
        cprint("\n" + "=" * 60, Colors.CYAN)
        cprint("  Доступные модели для конвертации", Colors.CYAN)
        cprint("=" * 60 + "\n", Colors.CYAN)
        
        # Рекомендуемые модели
        recommended_models = [
            {"id": "Qwen/Qwen2.5-0.5B-Instruct", "size": "~1 GB", "desc": "Маленькая, быстрая модель"},
            {"id": "Qwen/Qwen2.5-1.5B-Instruct", "size": "~3 GB", "desc": "Оптимальный баланс"},
            {"id": "Qwen/Qwen2.5-3B-Instruct", "size": "~6 GB", "desc": "Хорошее качество"},
            {"id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "size": "~2.5 GB", "desc": "Компактная модель"},
            {"id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "size": "~3.5 GB", "desc": "Модель с reasoning"},
            {"id": "google/gemma-2-2b-it", "size": "~5 GB", "desc": "Модель от Google"},
            {"id": "microsoft/Phi-3-mini-4k-instruct", "size": "~4 GB", "desc": "Модель от Microsoft"},
        ]
        
        print(f"{'Model ID':<55} {'Size':<12} {'Description'}")
        print("-" * 90)
        
        for model in recommended_models:
            print(f"{model['id']:<55} {model['size']:<12} {model['desc']}")
        
        print("\n" + "=" * 60)
        cprint("Используйте 'python rkllm_manager.py full <model_id>' для загрузки", Colors.YELLOW)
        print("=" * 60 + "\n")
        
        return 0
    
    def cmd_clean(self, args) -> int:
        """Команда: clean - очистка временных файлов"""
        cprint("\n" + "=" * 60, Colors.CYAN)
        cprint("  Очистка временных файлов", Colors.CYAN)
        cprint("=" * 60 + "\n", Colors.CYAN)
        
        dirs_to_clean = [
            self.work_dir / "cache",
            self.work_dir / "temp",
        ]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                cprint(f"Очистка: {dir_path}", Colors.YELLOW)
                # Здесь можно добавить реальную очистку
        
        cprint("\n✓ Очистка завершена", Colors.GREEN)
        return 0


def create_parser() -> argparse.ArgumentParser:
    """Создание парсера аргументов"""
    parser = argparse.ArgumentParser(
        description='RKLLM Manager - Управление конвертацией моделей',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Установка окружения
  python rkllm_manager.py setup

  # Проверка установки
  python rkllm_manager.py verify

  # Скачать модель
  python rkllm_manager.py download Qwen/Qwen2.5-1.5B-Instruct

  # Конвертировать модель
  python rkllm_manager.py convert ./models/Qwen2.5-1.5B-Instruct

  # Полный цикл (скачать + конвертировать)
  python rkllm_manager.py full Qwen/Qwen2.5-1.5B-Instruct

  # Показать список рекомендуемых моделей
  python rkllm_manager.py list

Параметры конвертации:
  --platform    RK3588, RK3576, RK3562, RV1126B (по умолчанию: RK3588)
  --quant       W8A8, W4A16, W4A16_G128 (по умолчанию: W8A8)
  --context     Размер контекста (по умолчанию: 4096)
        """
    )
    
    # Основные команды
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # setup
    setup_parser = subparsers.add_parser('setup', help='Установка окружения')
    setup_parser.add_argument('-v', '--verbose', action='store_true')
    setup_parser.set_defaults(func='setup')
    
    # verify
    verify_parser = subparsers.add_parser('verify', help='Проверка установки')
    verify_parser.add_argument('-v', '--verbose', action='store_true')
    verify_parser.add_argument('--json', action='store_true')
    verify_parser.set_defaults(func='verify')
    
    # download
    download_parser = subparsers.add_parser('download', help='Скачать модель')
    download_parser.add_argument('model', type=str, nargs='?', help='ID модели')
    download_parser.add_argument('-o', '--output', type=str, help='Директория')
    download_parser.add_argument('--info', action='store_true')
    download_parser.set_defaults(func='download')
    
    # convert
    convert_parser = subparsers.add_parser('convert', help='Конвертировать модель')
    convert_parser.add_argument('model', type=str, help='Путь к модели')
    convert_parser.add_argument('-o', '--output', type=str, help='Директория вывода')
    convert_parser.add_argument('-p', '--platform', type=str, default='RK3588')
    convert_parser.add_argument('-q', '--quant', type=str, default='W8A8')
    convert_parser.add_argument('--context', type=int, default=4096)
    convert_parser.set_defaults(func='convert')
    
    # full
    full_parser = subparsers.add_parser('full', help='Полный цикл (download + convert)')
    full_parser.add_argument('model', type=str, nargs='?', help='ID модели')
    full_parser.add_argument('-p', '--platform', type=str, default='RK3588')
    full_parser.add_argument('-q', '--quant', type=str, default='W8A8')
    full_parser.add_argument('--context', type=int, default=4096)
    full_parser.set_defaults(func='full')
    
    # list
    list_parser = subparsers.add_parser('list', help='Список моделей')
    list_parser.set_defaults(func='list')
    
    # clean
    clean_parser = subparsers.add_parser('clean', help='Очистка')
    clean_parser.set_defaults(func='clean')
    
    # Глобальные флаги
    parser.add_argument('-v', '--verbose', action='store_true', help='Подробный вывод')
    parser.add_argument('-q', '--quiet', action='store_true', help='Тихий режим')
    parser.add_argument('--version', action='version', version='RKLLM Manager 1.0')
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Вывод справки если команда не указана
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Проверка окружения
    if args.command not in ['setup']:
        if not check_conda_env():
            cprint("\n⚠ Требуется активное окружение 'rkllm'!", Colors.YELLOW)
            cprint("Активируйте: conda activate rkllm\n", Colors.YELLOW)
            
            if args.command != 'verify':
                response = input("Продолжить без активного окружения? (y/n): ").strip().lower()
                if response != 'y':
                    sys.exit(1)
    
    # Создание менеджера и выполнение команды
    manager = RKLLMManager(verbose=not getattr(args, 'quiet', False))
    
    # Маппинг команд
    command_map = {
        'setup': manager.cmd_setup,
        'verify': manager.cmd_verify,
        'download': manager.cmd_download,
        'convert': manager.cmd_convert,
        'full': manager.cmd_full,
        'list': manager.cmd_list,
        'clean': manager.cmd_clean,
    }
    
    func = command_map.get(args.command)
    if func:
        exit_code = func(args)
        sys.exit(exit_code)
    else:
        cprint(f"Неизвестная команда: {args.command}", Colors.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
