#!/bin/bash
# ============================================================================
# Скрипт установки окружения RKLLM для конвертации моделей
# ============================================================================
# Поддерживаемые версии Python: 3.9, 3.10, 3.11, 3.12
# Целевая платформа: RK3588, RK3576, RK3562, RV1126B
# ============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Логирование
log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

# Имя conda окружения
ENV_NAME="${RKLLM_ENV_NAME:-rkllm}"

# Версия Python (по умолчанию 3.11)
PYTHON_VERSION="${RKLLM_PYTHON_VERSION:-3.11}"

# Путь к директории RKLLM
RKLLM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Путь к пакетам RKLLM
PACKAGES_DIR="${RKLLM_DIR}/rkllm-toolkit/packages"

# Версия RKLLM Toolkit
RKLLM_VERSION="1.2.3"

# ============================================================================
# ПРОВЕРКА ТРЕБОВАНИЙ
# ============================================================================

check_requirements() {
    log_info "Проверка системных требований..."
    
    # Проверка conda
    if ! command -v conda &> /dev/null; then
        log_error "Conda не найдена! Установите Anaconda или Miniconda."
        exit 1
    fi
    
    CONDA_VERSION=$(conda --version)
    log_success "Found: ${CONDA_VERSION}"
    
    # Проверка наличия пакетов RKLLM
    if [ ! -d "${PACKAGES_DIR}" ]; then
        log_error "Директория с пакетами не найдена: ${PACKAGES_DIR}"
        exit 1
    fi
    
    # Поиск whl файла для указанной версии Python
    PY_VER_SHORT=$(echo "${PYTHON_VERSION}" | cut -d'.' -f1-2 | tr -d '.')
    WHL_FILE=$(find "${PACKAGES_DIR}" -name "rkllm_toolkit-${RKLLM_VERSION}-cp${PY_VER_SHORT}-*.whl" 2>/dev/null | head -1)
    
    if [ -z "${WHL_FILE}" ]; then
        log_error "WHL файл для Python ${PYTHON_VERSION} не найден!"
        log_info "Доступные версии:"
        find "${PACKAGES_DIR}" -name "rkllm_toolkit-*.whl" | while read f; do
            echo "  - $(basename "$f")"
        done
        exit 1
    fi
    
    log_success "WHL файл найден: $(basename "${WHL_FILE}")"
    
    # Проверка CUDA (опционально)
    if command -v nvidia-smi &> /dev/null; then
        CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
        log_success "NVIDIA Driver: ${CUDA_VERSION}"
        
        if command -v nvcc &> /dev/null; then
            NVCC_VERSION=$(nvcc --version | grep "release" | cut -d',' -f2 | cut -d' ' -f3)
            log_success "CUDA Toolkit: ${NVCC_VERSION}"
        else
            log_warning "nvcc не найден (конвертация будет работать на CPU)"
        fi
    else
        log_warning "NVIDIA GPU не обнаружен (конвертация будет работать на CPU)"
    fi
    
    # Проверка свободного места
    FREE_SPACE=$(df -h "${RKLLM_DIR}" | awk 'NR==2 {print $4}')
    log_info "Свободное место: ${FREE_SPACE}"
}

# ============================================================================
# СОЗДАНИЕ ОКРУЖЕНИЯ
# ============================================================================

create_conda_env() {
    log_info "Создание conda окружения '${ENV_NAME}' с Python ${PYTHON_VERSION}..."
    
    # Проверка существования окружения
    if conda env list | grep -q "^${ENV_NAME} "; then
        log_warning "Окружение '${ENV_NAME}' уже существует!"
        read -p "Удалить существующее окружение и создать заново? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Удаление старого окружения..."
            conda env remove -n "${ENV_NAME}" -y
        else
            log_info "Использование существующего окружения..."
            return 0
        fi
    fi
    
    # Создание окружения
    conda create -n "${ENV_NAME}" python="${PYTHON_VERSION}" -y
    
    if [ $? -ne 0 ]; then
        log_error "Не удалось создать conda окружение!"
        exit 1
    fi
    
    log_success "Окружение создано!"
}

# ============================================================================
# УСТАНОВКА ПАКЕТОВ
# ============================================================================

install_packages() {
    log_info "Активация окружения '${ENV_NAME}'..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "${ENV_NAME}"
    
    log_info "Установка базовых зависимостей..."
    
    # Для Python 3.12 нужно установить BUILD_CUDA_EXT=0
    if [[ "${PYTHON_VERSION}" == "3.12" ]]; then
        log_warning "Для Python 3.12 устанавливаем BUILD_CUDA_EXT=0"
        export BUILD_CUDA_EXT=0
    fi
    
    # Установка requirements.txt
    REQUIREMENTS_FILE="${PACKAGES_DIR}/requirements.txt"
    
    # Проверка на RWKV7
    if [[ "${RKLLM_USE_RWKV7}" == "true" ]]; then
        REQUIREMENTS_FILE="${PACKAGES_DIR}/requirements_rwkv7.txt"
        log_info "Использование требований для RWKV7..."
    fi
    
    if [ ! -f "${REQUIREMENTS_FILE}" ]; then
        log_error "Файл требований не найден: ${REQUIREMENTS_FILE}"
        exit 1
    fi
    
    log_info "Установка пакетов из ${REQUIREMENTS_FILE}..."
    pip install --upgrade pip
    pip install -r "${REQUIREMENTS_FILE}"
    
    if [ $? -ne 0 ]; then
        log_error "Ошибка установки зависимостей!"
        exit 1
    fi
    
    log_success "Базовые зависимости установлены!"
    
    # Установка RKLLM Toolkit
    log_info "Установка RKLLM Toolkit ${RKLLM_VERSION}..."
    PY_VER_SHORT=$(echo "${PYTHON_VERSION}" | cut -d'.' -f1-2 | tr -d '.')
    WHL_FILE=$(find "${PACKAGES_DIR}" -name "rkllm_toolkit-${RKLLM_VERSION}-cp${PY_VER_SHORT}-*.whl" | head -1)
    
    if [ -z "${WHL_FILE}" ]; then
        log_error "WHL файл не найден!"
        exit 1
    fi
    
    pip install "${WHL_FILE}"
    
    if [ $? -ne 0 ]; then
        log_error "Ошибка установки RKLLM Toolkit!"
        exit 1
    fi
    
    log_success "RKLLM Toolkit установлен!"
    
    # Установка дополнительных утилит
    log_info "Установка дополнительных утилит..."
    pip install huggingface_hub requests tqdm
    
    conda deactivate
}

# ============================================================================
# ВЕРИФИКАЦИЯ
# ============================================================================

verify_installation() {
    log_info "Верификация установки..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "${ENV_NAME}"
    
    # Проверка версии Python
    PYTHON_VER=$(python --version)
    log_success "${PYTHON_VER}"
    
    # Проверка RKLLM
    python -c "from rkllm.api import RKLLM; print('RKLLM API: OK')" || {
        log_error "Ошибка импорта RKLLM!"
        exit 1
    }
    
    # Проверка torch
    python -c "import torch; print(f'PyTorch: {torch.__version__}')" || {
        log_error "Ошибка импорта PyTorch!"
        exit 1
    }
    
    # Проверка transformers
    python -c "import transformers; print(f'Transformers: {transformers.__version__}')" || {
        log_error "Ошибка импорта Transformers!"
        exit 1
    }
    
    # Проверка CUDA
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
    
    conda deactivate
    
    log_success "Все проверки пройдены!"
}

# ============================================================================
# СОЗДАНИЕ ШАБЛОНОВ
# ============================================================================

create_templates() {
    log_info "Создание рабочих директорий..."
    
    WORK_DIR="${RKLLM_DIR}/workdir"
    mkdir -p "${WORK_DIR}/models"
    mkdir -p "${WORK_DIR}/outputs"
    mkdir -p "${WORK_DIR}/quant_data"
    
    # Создание шаблона data_quant.json
    QUANT_TEMPLATE="${WORK_DIR}/quant_data/data_quant.json.example"
    if [ ! -f "${QUANT_TEMPLATE}" ]; then
        cat > "${QUANT_TEMPLATE}" << 'EOF'
[
    {"input": "Human: Привет! Как тебя зовут?\nAssistant: ", "target": "Привет! Я языковая модель."},
    {"input": "Human: Что ты умеешь?\nAssistant: ", "target": "Я могу отвечать на вопросы и помогать с задачами."},
    {"input": "Human: Расскажи о себе.\nAssistant: ", "target": "Я компактная языковая модель для edge-устройств."}
]
EOF
        log_success "Создан шаблон: ${QUANT_TEMPLATE}"
    fi
    
    log_success "Рабочие директории созданы в: ${WORK_DIR}"
}

# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================================

main() {
    echo "============================================================"
    echo "  RKLLM Environment Setup Script"
    echo "  Версия SDK: ${RKLLM_VERSION}"
    echo "  Python: ${PYTHON_VERSION}"
    echo "  Окружение: ${ENV_NAME}"
    echo "============================================================"
    echo
    
    check_requirements
    echo
    
    create_conda_env
    echo
    
    install_packages
    echo
    
    verify_installation
    echo
    
    create_templates
    echo
    
    echo "============================================================"
    log_success "Установка завершена успешно!"
    echo "============================================================"
    echo
    echo "Для активации окружения выполните:"
    echo "  source ~/anaconda3/bin/activate ${ENV_NAME}"
    echo
    echo "Для проверки установки:"
    echo "  python -c \"from rkllm.api import RKLLM; print('RKLLM готов!')\""
    echo
    echo "Рабочая директория: ${WORK_DIR}"
    echo "============================================================"
}

# Запуск
main "$@"
