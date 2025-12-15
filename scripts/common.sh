#!/usr/bin/env bash
# GlareGuard Theme Installer - Common Functions
# 공통 함수 라이브러리

# 중복 로드 방지 가드
[[ -n "${_GLAREGUARD_COMMON_LOADED:-}" ]] && return 0
_GLAREGUARD_COMMON_LOADED=1

set -euo pipefail

# ============================================================
# 색상 정의 (ANSI escape codes)
# ============================================================
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'  # No Color

# ============================================================
# 프로젝트 정보
# ============================================================
readonly PROJECT_NAME="GlareGuard"
readonly VERSION="0.1.0"

# ============================================================
# 경로 설정
# ============================================================
# 스크립트가 어디서 실행되든 프로젝트 루트를 찾음
get_script_dir() {
    local source="${BASH_SOURCE[0]}"
    while [ -h "$source" ]; do
        local dir="$(cd -P "$(dirname "$source")" && pwd)"
        source="$(readlink "$source")"
        [[ $source != /* ]] && source="$dir/$source"
    done
    echo "$(cd -P "$(dirname "$source")" && pwd)"
}

# 이미 정의된 경우 덮어쓰지 않음 (install.sh와 충돌 방지)
COMMON_SCRIPT_DIR="$(get_script_dir)"
PROJECT_ROOT="${PROJECT_ROOT:-$(dirname "$COMMON_SCRIPT_DIR")}"

# 백업 비활성화 플래그 (기본: 백업 활성화)
NO_BACKUP="${NO_BACKUP:-false}"

# ============================================================
# 메시지 출력 함수
# ============================================================
print_header() {
    echo ""
    echo -e "${BOLD}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║     ${PROJECT_NAME} Theme Installer               ║${NC}"
    echo -e "${BOLD}║     녹내장 사용자를 위한 IDE 테마            ║${NC}"
    echo -e "${BOLD}╚══════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_step() {
    echo -e "${BOLD}>>>${NC} $1"
}

# ============================================================
# OS 감지
# ============================================================
check_os() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            echo "linux"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

is_macos() {
    [[ "$(check_os)" == "macos" ]]
}

is_linux() {
    [[ "$(check_os)" == "linux" ]]
}

# ============================================================
# 디렉토리/파일 유틸리티
# ============================================================
create_dir_if_needed() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        if mkdir -p "$dir" 2>/dev/null; then
            print_info "디렉토리 생성: $dir"
            return 0
        else
            print_error "디렉토리 생성 실패: $dir"
            print_info "권한을 확인하세요: sudo mkdir -p \"$dir\""
            return 1
        fi
    fi
    return 0
}

# 기존 파일/디렉토리 백업
backup_existing() {
    local target="$1"
    local platform="$2"

    if [[ "$NO_BACKUP" == "true" ]]; then
        return 0
    fi

    if [[ -e "$target" ]]; then
        local backup_base="$HOME/.glareguard-backup"
        local timestamp
        timestamp="$(date +%Y%m%d-%H%M%S)"
        local backup_dir="$backup_base/$timestamp/$platform"

        create_dir_if_needed "$backup_dir" || return 1

        local basename
        basename="$(basename "$target")"

        if mv "$target" "$backup_dir/$basename" 2>/dev/null; then
            print_warning "기존 파일 백업됨: $backup_dir/$basename"
            return 0
        else
            print_error "백업 실패: $target"
            return 1
        fi
    fi
    return 0
}

# 파일 복사 with 확인 및 에러 캡처
copy_file() {
    local src="$1"
    local dest="$2"
    local err_msg

    if [[ ! -f "$src" ]]; then
        print_error "소스 파일 없음: $src"
        return 1
    fi

    if err_msg=$(cp "$src" "$dest" 2>&1); then
        return 0
    else
        print_error "파일 복사 실패: $src -> $dest"
        [[ -n "$err_msg" ]] && print_error "원인: $err_msg"
        return 1
    fi
}

# 디렉토리 복사 with 확인 및 에러 캡처
copy_dir() {
    local src="$1"
    local dest="$2"
    local err_msg

    if [[ ! -d "$src" ]]; then
        print_error "소스 디렉토리 없음: $src"
        return 1
    fi

    if err_msg=$(cp -r "$src" "$dest" 2>&1); then
        return 0
    else
        print_error "디렉토리 복사 실패: $src -> $dest"
        [[ -n "$err_msg" ]] && print_error "원인: $err_msg"
        return 1
    fi
}

# ============================================================
# 사용자 입력
# ============================================================
confirm_action() {
    local message="$1"
    local default="${2:-n}"

    local prompt
    if [[ "$default" == "y" ]]; then
        prompt="[Y/n]"
    else
        prompt="[y/N]"
    fi

    echo -n -e "${YELLOW}$message $prompt: ${NC}"
    read -r response

    response="${response:-$default}"
    response="${response,,}"  # 소문자 변환

    [[ "$response" == "y" || "$response" == "yes" ]]
}

# ============================================================
# 종료 코드
# ============================================================
readonly EXIT_SUCCESS=0
readonly EXIT_ERROR=1
readonly EXIT_INVALID_ARGS=2
readonly EXIT_UNSUPPORTED_OS=3
readonly EXIT_PERMISSION_ERROR=4
