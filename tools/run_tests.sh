#!/bin/bash
# ============================================================================
# Скрипт сборки и запуска тестов RKLLM Tools
# ============================================================================
# Использование:
#   ./run_tests.sh              - Запуск unit тестов
#   ./run_tests.sh --all        - Все тесты (unit + integration)
#   ./run_tests.sh --coverage   - С покрытием
#   ./run_tests.sh --build      - Сборка и тесты
# ============================================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$SCRIPT_DIR/tests"
REPORTS_DIR="$SCRIPT_DIR/reports"

# Логирование
log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================================================
# ФУНКЦИИ
# ============================================================================

print_header() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

check_prerequisites() {
    log_info "Проверка зависимостей..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 не найден!"
        exit 1
    fi
    log_success "Python: $(python3 --version)"
    
    # Conda (опционально)
    if command -v conda &> /dev/null; then
        log_success "Conda: $(conda --version)"
    else
        log_warning "Conda не найдена (необходима для интеграционных тестов)"
    fi
    
    # unittest
    python3 -m unittest --help > /dev/null 2>&1 || {
        log_error "unittest не доступен!"
        exit 1
    }
    log_success "unittest: доступен"
}

create_reports_dir() {
    mkdir -p "$REPORTS_DIR"
    log_info "Директория отчетов: $REPORTS_DIR"
}

run_unit_tests() {
    print_header "Запуск unit тестов"
    
    cd "$TESTS_DIR"
    
    python3 -m unittest test_rkllm_tools \
        --verbose \
        2>&1 | tee "$REPORTS_DIR/unit_tests.log"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log_success "Unit тесты пройдены!"
    else
        log_error "Unit тесты не пройдены!"
    fi
    
    return $exit_code
}

run_integration_tests() {
    print_header "Запуск интеграционных тестов"
    
    # Проверка conda окружения
    if [ -z "$CONDA_DEFAULT_ENV" ] || [ "$CONDA_DEFAULT_ENV" != "rkllm" ]; then
        log_warning "Окружение rkllm не активно!"
        log_info "Активируйте: source ~/anaconda3/bin/activate rkllm"
        
        read -p "Продолжить без окружения rkllm? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warning "Интеграционные тесты пропущены"
            return 0
        fi
    fi
    
    cd "$TESTS_DIR"
    
    RUN_INTEGRATION=1 python3 -m unittest test_rkllm_tools.TestIntegrationSetup \
        --verbose \
        2>&1 | tee "$REPORTS_DIR/integration_tests.log"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log_success "Интеграционные тесты пройдены!"
    else
        log_error "Интеграционные тесты не пройдены!"
    fi
    
    return $exit_code
}

run_coverage() {
    print_header "Запуск тестов с покрытием"
    
    if ! python3 -c "import coverage" 2>/dev/null; then
        log_warning "coverage не установлен, пропускаем..."
        return 0
    fi
    
    cd "$TESTS_DIR"
    
    coverage run -m unittest test_rkllm_tools
    coverage report -m > "$REPORTS_DIR/coverage_report.txt"
    coverage html -d "$REPORTS_DIR/coverage_html"
    
    log_success "Отчет о покрытии: $REPORTS_DIR/coverage_html/index.html"
}

build_and_test() {
    print_header "Сборка и тестирование"
    
    # Проверка структуры проекта
    log_info "Проверка структуры проекта..."
    
    local required_files=(
        "setup_rkllm_env.sh"
        "verify_rkllm_installation.py"
        "convert_hf_model.py"
        "download_hf_model.py"
        "rkllm_manager.py"
        "README.md"
    )
    
    local missing=0
    for file in "${required_files[@]}"; do
        if [ -f "$SCRIPT_DIR/$file" ]; then
            log_success "✓ $file"
        else
            log_error "✗ $file (отсутствует)"
            ((missing++))
        fi
    done
    
    if [ $missing -gt 0 ]; then
        log_error "Отсутствует файлов: $missing"
        return 1
    fi
    
    log_success "Все файлы проекта на месте!"
    
    # Запуск тестов
    run_unit_tests
}

test_t_lite_config() {
    print_header "Тест конфигурации T-lite-it-2.1"
    
    local config_file="$TESTS_DIR/t_lite_config.json"
    
    if [ ! -f "$config_file" ]; then
        log_error "Конфигурация не найдена: $config_file"
        return 1
    fi
    
    # Проверка JSON
    python3 -c "import json; json.load(open('$config_file'))" && {
        log_success "Конфигурация валидна"
    } || {
        log_error "Неверный формат JSON"
        return 1
    }
    
    # Вывод информации
    log_info "Информация о модели:"
    python3 -c "
import json
with open('$config_file') as f:
    data = json.load(f)
    print(f\"  Модель: {data['model']['name']}\")
    print(f\"  Архитектура: {data['model']['base_architecture']}\")
    print(f\"  Размер: {data['model']['size']}\")
    print(f\"  Платформа: {data['conversion']['target_platform']}\")
    print(f\"  Квантование: {data['conversion']['quantized_dtype']}\")
"
}

generate_report() {
    print_header "Генерация отчета"
    
    local report_file="$REPORTS_DIR/test_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Отчет о тестировании RKLLM Tools

**Дата:** $(date '+%Y-%m-%d %H:%M:%S')
**Версия:** 1.0

## Результаты тестов

### Unit тесты
$(cat "$REPORTS_DIR/unit_tests.log" 2>/dev/null | tail -20 || echo "Не проводились")

### Интеграционные тесты
$(cat "$REPORTS_DIR/integration_tests.log" 2>/dev/null | tail -20 || echo "Не проводились")

## Структура проекта

$(ls -la "$SCRIPT_DIR"/*.py "$SCRIPT_DIR"/*.sh 2>/dev/null)

## Статус

$(if [ -f "$REPORTS_DIR/unit_tests.log" ] && grep -q "OK" "$REPORTS_DIR/unit_tests.log"; then
    echo "✅ Unit тесты: ПРОЙДЕНЫ"
else
    echo "⏸ Unit тесты: НЕ ПРОВОДИЛИСЬ"
fi)

---
*Сгенерировано автоматически*
EOF
    
    log_success "Отчет сохранен: $report_file"
}

show_help() {
    cat << EOF
Скрипт сборки и тестирования RKLLM Tools

Использование:
    $0 [OPTIONS]

Опции:
    --all           Запустить все тесты (unit + integration)
    --unit          Только unit тесты (по умолчанию)
    --integration   Только интеграционные тесты
    --coverage      Тесты с покрытием
    --build         Сборка и тесты
    --t-lite        Тест конфигурации T-lite-it-2.1
    --report        Сгенерировать отчет
    --clean         Очистить отчеты
    --help          Показать эту справку

Примеры:
    $0                  # Unit тесты
    $0 --all            # Все тесты
    $0 --build          # Сборка + тесты
    $0 --t-lite         # Тест T-lite конфигурации
EOF
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    local mode="unit"
    
    # Парсинг аргументов
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                mode="all"
                shift
                ;;
            --unit)
                mode="unit"
                shift
                ;;
            --integration)
                mode="integration"
                shift
                ;;
            --coverage)
                mode="coverage"
                shift
                ;;
            --build)
                mode="build"
                shift
                ;;
            --t-lite)
                mode="t-lite"
                shift
                ;;
            --report)
                mode="report"
                shift
                ;;
            --clean)
                mode="clean"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Неизвестная опция: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header "RKLLM Tools - Тестирование"
    check_prerequisites
    create_reports_dir
    
    case $mode in
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        all)
            run_unit_tests && run_integration_tests
            ;;
        coverage)
            run_unit_tests
            run_coverage
            ;;
        build)
            build_and_test
            ;;
        t-lite)
            test_t_lite_config
            ;;
        report)
            generate_report
            ;;
        clean)
            log_info "Очистка отчетов..."
            rm -rf "$REPORTS_DIR"/*
            log_success "Очистка завершена"
            ;;
    esac
    
    generate_report
}

main "$@"
