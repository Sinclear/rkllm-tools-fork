#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилита для скачивания моделей с HuggingFace Hub

Поддерживаемые возможности:
- Скачивание полных моделей
- Скачивание конкретных файлов
- Проверка наличия модели
- Просмотр информации о модели
- Resume загрузка при обрыве

Использование:
    python download_hf_model.py Qwen/Qwen2.5-1.5B-Instruct --output ./models
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class HuggingFaceDownloader:
    """Класс для скачивания моделей с HuggingFace"""
    
    def __init__(self, output_dir: str = "./models", token: Optional[str] = None):
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.token = token or os.environ.get("HF_TOKEN")
        self.api = None
        self._init_api()
    
    def _init_api(self):
        """Инициализация HuggingFace API"""
        try:
            from huggingface_hub import HfApi, login
            
            if self.token:
                login(token=self.token)
            
            self.api = HfApi()
        except ImportError:
            print("Ошибка: huggingface_hub не установлен!")
            print("Установите: pip install huggingface_hub")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка инициализации HF API: {e}")
            sys.exit(1)
    
    def _log(self, message: str, level: str = "INFO"):
        """Логирование"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR": "✗",
            "DOWNLOAD": "↓"
        }.get(level, "•")
        print(f"[{timestamp}] [{prefix}] {message}")
    
    def model_exists(self, model_id: str) -> bool:
        """Проверка существования модели"""
        try:
            self.api.model_info(model_id)
            return True
        except Exception:
            return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Получение информации о модели"""
        try:
            info = self.api.model_info(model_id)
            
            # Получение размера репозитория
            siblings = info.siblings or []
            total_size = sum(getattr(f, 'size', 0) or 0 for f in siblings)
            
            return {
                "id": model_id,
                "author": info.author,
                "created_at": str(info.created_at) if info.created_at else None,
                "last_modified": str(info.last_modified) if info.last_modified else None,
                "tags": info.tags or [],
                "pipeline_tag": info.pipeline_tag,
                "library_name": info.library_name,
                "files_count": len(siblings),
                "total_size_bytes": total_size,
                "total_size_gb": round(total_size / (1024**3), 2),
            }
        except Exception as e:
            self._log(f"Ошибка получения информации: {e}", "ERROR")
            return None
    
    def list_model_files(self, model_id: str) -> List[str]:
        """Список файлов модели"""
        try:
            info = self.api.model_info(model_id)
            return [f.rfilename for f in (info.siblings or [])]
        except Exception as e:
            self._log(f"Ошибка получения списка файлов: {e}", "ERROR")
            return []
    
    def download_model(
        self,
        model_id: str,
        local_dir: Optional[str] = None,
        allow_patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        resume_download: bool = True,
        force_download: bool = False,
    ) -> Optional[str]:
        """
        Скачивание модели
        
        Args:
            model_id: ID модели на HuggingFace
            local_dir: Локальная директория для сохранения
            allow_patterns: Шаблоны файлов для скачивания
            ignore_patterns: Шаблоны файлов для игнорирования
            resume_download: Возобновлять загрузку при обрыве
            force_download: Принудительная загрузка
            
        Returns:
            Путь к скачанной модели или None
        """
        try:
            from huggingface_hub import snapshot_download
            
            # Определение локальной директории
            if local_dir:
                local_path = Path(local_dir).expanduser().resolve()
            else:
                model_name = model_id.split("/")[-1]
                local_path = self.output_dir / model_name
            
            self._log(f"Скачивание модели: {model_id}", "DOWNLOAD")
            self._log(f"Целевая директория: {local_path}", "INFO")
            
            # Настройка паттернов
            if allow_patterns is None:
                allow_patterns = [
                    "*.json",
                    "*.py",
                    "*.txt",
                    "*.safetensors",
                    "*.bin",
                    "*.model",
                    "*.tiktoken",
                    "*.txt",
                    "tokenizer.json",
                    "special_tokens_map.json",
                    "chat_template.jinja",
                ]
            
            if ignore_patterns is None:
                ignore_patterns = [
                    "*.msgpack",
                    "*.h5",
                    "*.ot",
                    "flax_model*",
                    "tf_model*",
                    "*.pb",
                    "onnx/*",
                    "tensorrt/*",
                ]
            
            # Скачивание
            downloaded_path = snapshot_download(
                repo_id=model_id,
                local_dir=str(local_path),
                allow_patterns=allow_patterns,
                ignore_patterns=ignore_patterns,
                resume_download=resume_download,
                force_download=force_download,
                token=self.token,
                local_dir_use_symlinks=False,
            )
            
            self._log(f"Модель скачана: {downloaded_path}", "SUCCESS")
            
            # Информация о размере
            total_size = sum(f.stat().st_size for f in local_path.rglob("*") if f.is_file())
            self._log(f"Общий размер: {total_size / (1024**3):.2f} GB", "INFO")
            
            return downloaded_path
            
        except KeyboardInterrupt:
            self._log("Загрузка прервана пользователем", "WARNING")
            return None
        except Exception as e:
            self._log(f"Ошибка загрузки: {e}", "ERROR")
            return None
    
    def download_file(
        self,
        model_id: str,
        filename: str,
        local_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Скачивание конкретного файла"""
        try:
            from huggingface_hub import hf_hub_download
            
            if local_dir:
                local_path = Path(local_dir).expanduser().resolve()
            else:
                local_path = self.output_dir
            
            self._log(f"Скачивание файла: {filename}", "DOWNLOAD")
            
            downloaded_path = hf_hub_download(
                repo_id=model_id,
                filename=filename,
                local_dir=str(local_path),
                token=self.token,
                resume_download=True,
            )
            
            self._log(f"Файл скачан: {downloaded_path}", "SUCCESS")
            return downloaded_path
            
        except Exception as e:
            self._log(f"Ошибка загрузки файла: {e}", "ERROR")
            return None


def format_size(size_bytes: int) -> str:
    """Форматирование размера в человекочитаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def cmd_download(args):
    """Команда: download"""
    downloader = HuggingFaceDownloader(
        output_dir=args.output,
        token=args.token
    )
    
    # Проверка существования модели
    if not args.skip_check:
        downloader._log(f"Проверка модели: {args.model}", "INFO")
        if not downloader.model_exists(args.model):
            downloader._log(f"Модель не найдена: {args.model}", "ERROR")
            downloader._log("Проверьте название модели или доступность HF Hub", "ERROR")
            sys.exit(1)
    
    # Получение информации о модели
    if args.info:
        info = downloader.get_model_info(args.model)
        if info:
            print("\n" + "=" * 60)
            print("  Информация о модели")
            print("=" * 60)
            for key, value in info.items():
                if value and key not in ['files_count', 'total_size_bytes']:
                    print(f"  {key}: {value}")
            print("=" * 60)
            
            if args.list_files:
                print("\nФайлы модели:")
                files = downloader.list_model_files(args.model)
                for f in files:
                    size_hint = ""
                    print(f"  {f} {size_hint}")
            print()
    
    # Скачивание
    if not args.dry_run:
        path = downloader.download_model(
            model_id=args.model,
            local_dir=args.local_dir,
            resume_download=not args.no_resume,
            force_download=args.force,
        )
        
        if path:
            print("\n" + "=" * 60)
            print("  ✓ Скачивание завершено")
            print("=" * 60)
            print(f"  Путь: {path}")
            print("=" * 60 + "\n")
        else:
            sys.exit(1)
    else:
        downloader._log("Режим сухой проверки (dry-run)", "INFO")


def cmd_search(args):
    """Команда: search"""
    try:
        from huggingface_hub import list_models
        
        query = args.query
        
        downloader = HuggingFaceDownloader(token=args.token)
        downloader._log(f"Поиск моделей: {query}", "INFO")
        
        models = list(
            list_models(
                search=query,
                limit=args.limit,
                sort="downloads",
                direction=-1,
            )
        )
        
        if not models:
            print("Модели не найдены")
            return
        
        print(f"\nНайдено моделей: {len(models)}\n")
        print(f"{'Model ID':<50} {'Downloads':<12} {'Likes':<10}")
        print("-" * 75)
        
        for model in models[:args.limit]:
            model_id = model.id
            downloads = getattr(model, 'downloads', 0) or 0
            likes = getattr(model, 'likes', 0) or 0
            print(f"{model_id:<50} {downloads:<12,} {likes:<10,}")
        
    except Exception as e:
        print(f"Ошибка поиска: {e}")


def cmd_info(args):
    """Команда: info"""
    downloader = HuggingFaceDownloader(token=args.token)
    
    if not downloader.model_exists(args.model):
        print(f"Модель не найдена: {args.model}")
        sys.exit(1)
    
    info = downloader.get_model_info(args.model)
    
    if info:
        print("\n" + "=" * 70)
        print(f"  Информация: {info['id']}")
        print("=" * 70)
        
        for key, value in info.items():
            if value:
                if key == 'tags':
                    print(f"  Tags: {', '.join(value[:10])}")
                    if len(value) > 10:
                        print(f"        ... и ещё {len(value) - 10}")
                elif key == 'total_size_gb':
                    print(f"  Размер: ~{value} GB")
                else:
                    print(f"  {key}: {value}")
        
        print("=" * 70)
        
        if args.list_files:
            print("\nФайлы модели:")
            files = downloader.list_model_files(args.model)
            print(f"  Всего файлов: {len(files)}\n")
            for f in sorted(files):
                print(f"    {f}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Утилита для скачивания моделей с HuggingFace',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Скачать модель
  python download_hf_model.py download Qwen/Qwen2.5-1.5B-Instruct
  
  # Скачать с указанием директории
  python download_hf_model.py download Qwen/Qwen2.5-0.5B-Instruct -o ./models
  
  # Показать информацию о модели
  python download_hf_model.py info Qwen/Qwen2.5-1.5B-Instruct
  
  # Поиск моделей
  python download_hf_model.py search "qwen2.5 instruct" --limit 10

Переменные окружения:
  HF_TOKEN - токен доступа к HuggingFace (для gated моделей)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команда')
    
    # Команда: download
    download_parser = subparsers.add_parser('download', help='Скачать модель')
    download_parser.add_argument('model', type=str, help='ID модели на HuggingFace')
    download_parser.add_argument('-o', '--output', type=str, default='./models', help='Директория для сохранения')
    download_parser.add_argument('-l', '--local-dir', type=str, help='Локальная директория')
    download_parser.add_argument('-t', '--token', type=str, help='HF токен')
    download_parser.add_argument('--info', action='store_true', help='Показать информацию перед загрузкой')
    download_parser.add_argument('--list-files', action='store_true', help='Показать список файлов')
    download_parser.add_argument('--skip-check', action='store_true', help='Пропустить проверку существования')
    download_parser.add_argument('--dry-run', action='store_true', help='Тестовый режим без загрузки')
    download_parser.add_argument('--force', action='store_true', help='Принудительная загрузка')
    download_parser.add_argument('--no-resume', action='store_true', help='Не возобновлять загрузку')
    download_parser.set_defaults(func=cmd_download)
    
    # Команда: info
    info_parser = subparsers.add_parser('info', help='Информация о модели')
    info_parser.add_argument('model', type=str, help='ID модели')
    info_parser.add_argument('-t', '--token', type=str, help='HF токен')
    info_parser.add_argument('--list-files', action='store_true', help='Показать список файлов')
    info_parser.set_defaults(func=cmd_info)
    
    # Команда: search
    search_parser = subparsers.add_parser('search', help='Поиск моделей')
    search_parser.add_argument('query', type=str, help='Поисковый запрос')
    search_parser.add_argument('-t', '--token', type=str, help='HF токен')
    search_parser.add_argument('--limit', type=int, default=20, help='Макс. количество результатов')
    search_parser.set_defaults(func=cmd_search)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
