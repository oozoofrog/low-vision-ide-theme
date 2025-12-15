#!/usr/bin/env bash
# GlareGuard Theme Installer - VS Code
# VS Code 테마 설치 스크립트

set -euo pipefail

# 공통 함수 로드
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ============================================================
# VS Code 설치 설정
# ============================================================
VSCODE_EXTENSIONS_DIR="$HOME/.vscode/extensions"
VSCODE_SOURCE_DIR="$PROJECT_ROOT/vscode"

# 확장 정보 변수 (get_extension_info에서 설정)
EXTENSION_NAME=""
EXTENSION_PUBLISHER=""
EXTENSION_VERSION=""
VSCODE_THEME_DIR=""

# ============================================================
# package.json에서 확장 정보 추출
# ============================================================
get_extension_info() {
    local package_json="$VSCODE_SOURCE_DIR/package.json"

    if [[ ! -f "$package_json" ]]; then
        print_error "package.json 파일을 찾을 수 없습니다: $package_json"
        return 1
    fi

    # jq가 있으면 사용, 없으면 grep/sed로 파싱
    if command -v jq &>/dev/null; then
        EXTENSION_NAME=$(jq -r '.name' "$package_json")
        EXTENSION_PUBLISHER=$(jq -r '.publisher' "$package_json")
        EXTENSION_VERSION=$(jq -r '.version' "$package_json")
    else
        # jq 없을 때 fallback (기본 파싱)
        EXTENSION_NAME=$(grep '"name"' "$package_json" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        EXTENSION_PUBLISHER=$(grep '"publisher"' "$package_json" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
        EXTENSION_VERSION=$(grep '"version"' "$package_json" | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/')
    fi

    # 값 검증
    if [[ -z "$EXTENSION_NAME" || -z "$EXTENSION_PUBLISHER" || -z "$EXTENSION_VERSION" ]]; then
        print_error "package.json에서 필수 정보를 추출할 수 없습니다"
        print_error "  name: $EXTENSION_NAME, publisher: $EXTENSION_PUBLISHER, version: $EXTENSION_VERSION"
        return 1
    fi

    # 설치 경로 설정
    VSCODE_THEME_DIR="$VSCODE_EXTENSIONS_DIR/${EXTENSION_PUBLISHER}.${EXTENSION_NAME}-${EXTENSION_VERSION}"

    return 0
}

# ============================================================
# 기존 설치 정리
# ============================================================
cleanup_old_installations() {
    local old_simple_dir="$VSCODE_EXTENSIONS_DIR/glareguard-theme"
    local pattern="${EXTENSION_PUBLISHER}.${EXTENSION_NAME}-*"

    # 1. 잘못된 형식 (glareguard-theme) 정리
    if [[ -d "$old_simple_dir" ]]; then
        print_warning "잘못된 형식의 기존 설치 발견: $old_simple_dir"
        if backup_existing "$old_simple_dir" "vscode-old-format"; then
            print_success "기존 설치 백업 완료"
        else
            print_warning "기존 설치 백업 실패 (계속 진행)"
        fi
    fi

    # 2. 이전 버전 정리 (현재 버전 제외)
    for dir in "$VSCODE_EXTENSIONS_DIR"/${pattern}; do
        if [[ -d "$dir" && "$dir" != "$VSCODE_THEME_DIR" ]]; then
            print_warning "이전 버전 발견: $(basename "$dir")"
            if backup_existing "$dir" "vscode-old-version"; then
                print_success "이전 버전 백업 완료"
            else
                print_warning "이전 버전 백업 실패 (계속 진행)"
            fi
        fi
    done

    return 0
}

# ============================================================
# 메인 설치 함수
# ============================================================
install_vscode() {
    print_step "VS Code 테마 설치 중..."

    # 소스 디렉토리 확인
    if [[ ! -d "$VSCODE_SOURCE_DIR" ]]; then
        print_error "VS Code 테마 소스 디렉토리를 찾을 수 없습니다: $VSCODE_SOURCE_DIR"
        return "$EXIT_ERROR"
    fi

    # 확장 정보 추출 (package.json에서 동적으로)
    if ! get_extension_info; then
        return "$EXIT_ERROR"
    fi
    print_info "설치 경로: $VSCODE_THEME_DIR"

    # VS Code 설치 여부 확인 (경고만)
    if ! command -v code &>/dev/null; then
        print_warning "VS Code가 설치되어 있지 않거나 PATH에 없습니다"
        print_info "테마 파일은 설치되지만, VS Code에서 인식하지 못할 수 있습니다"
    fi

    # 대상 디렉토리 생성
    if ! create_dir_if_needed "$VSCODE_EXTENSIONS_DIR"; then
        return "$EXIT_PERMISSION_ERROR"
    fi

    # 기존 잘못된 설치 및 이전 버전 정리
    cleanup_old_installations

    # 기존 테마 백업 (동일 버전 재설치 시)
    if [[ -d "$VSCODE_THEME_DIR" ]]; then
        if ! backup_existing "$VSCODE_THEME_DIR" "vscode"; then
            print_error "백업 실패로 VS Code 테마 설치를 중단합니다"
            return "$EXIT_ERROR"
        fi
    fi

    # 테마 디렉토리 생성
    if ! create_dir_if_needed "$VSCODE_THEME_DIR"; then
        return "$EXIT_PERMISSION_ERROR"
    fi

    # themes 서브디렉토리 생성
    if ! create_dir_if_needed "$VSCODE_THEME_DIR/themes"; then
        return "$EXIT_PERMISSION_ERROR"
    fi

    local install_count=0
    local critical_error=false
    local theme_count=0

    # package.json 복사 (필수 파일)
    if [[ -f "$VSCODE_SOURCE_DIR/package.json" ]]; then
        if copy_file "$VSCODE_SOURCE_DIR/package.json" "$VSCODE_THEME_DIR/package.json"; then
            install_count=$((install_count + 1))
        else
            print_error "package.json 복사 실패 - VS Code에서 테마를 인식할 수 없습니다"
            critical_error=true
        fi
    else
        print_error "package.json 파일 없음 - VS Code에서 테마를 인식할 수 없습니다"
        critical_error=true
    fi

    # README.md 복사 (선택 파일)
    if [[ -f "$VSCODE_SOURCE_DIR/README.md" ]]; then
        if copy_file "$VSCODE_SOURCE_DIR/README.md" "$VSCODE_THEME_DIR/README.md"; then
            install_count=$((install_count + 1))
        fi
    fi

    # 다크 테마 복사
    local dark_theme="$VSCODE_SOURCE_DIR/themes/glareguard-dark-color-theme.json"
    if [[ -f "$dark_theme" ]]; then
        if copy_file "$dark_theme" "$VSCODE_THEME_DIR/themes/glareguard-dark-color-theme.json"; then
            install_count=$((install_count + 1))
            theme_count=$((theme_count + 1))
        fi
    else
        print_warning "다크 테마 파일 없음: $dark_theme"
    fi

    # 라이트 테마 복사
    local light_theme="$VSCODE_SOURCE_DIR/themes/glareguard-light-color-theme.json"
    if [[ -f "$light_theme" ]]; then
        if copy_file "$light_theme" "$VSCODE_THEME_DIR/themes/glareguard-light-color-theme.json"; then
            install_count=$((install_count + 1))
            theme_count=$((theme_count + 1))
        fi
    else
        print_warning "라이트 테마 파일 없음: $light_theme"
    fi

    # 결과 출력
    if [[ "$critical_error" == "true" ]]; then
        print_error "VS Code 테마 설치 실패 (필수 파일 누락)"
        return "$EXIT_ERROR"
    elif [[ $theme_count -eq 0 ]]; then
        print_error "VS Code 테마 설치 실패 (테마 파일 없음)"
        return "$EXIT_ERROR"
    else
        print_success "VS Code 테마 설치 완료 (${install_count}개 파일, 테마 ${theme_count}개)"
        echo ""
        print_info "테마를 적용하려면:"
        echo "    1. VS Code를 재시작하세요"
        echo "    2. Cmd+Shift+P (또는 Ctrl+Shift+P)"
        echo "    3. 'Preferences: Color Theme' 선택"
        echo "    4. 'GlareGuard Dark' 또는 'GlareGuard Light' 선택"
        echo ""
        return "$EXIT_SUCCESS"
    fi
}

# ============================================================
# 직접 실행 시
# ============================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_vscode
fi
