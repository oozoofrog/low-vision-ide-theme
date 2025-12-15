#!/usr/bin/env bash
# GlareGuard Theme Installer - Xcode
# Xcode 테마 설치 스크립트 (macOS 전용)

set -euo pipefail

# 공통 함수 로드
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ============================================================
# Xcode 설치 설정
# ============================================================
XCODE_THEMES_DIR="$HOME/Library/Developer/Xcode/UserData/FontAndColorThemes"
XCODE_SOURCE_DIR="$PROJECT_ROOT/xcode"

# ============================================================
# 메인 설치 함수
# ============================================================
install_xcode() {
    print_step "Xcode 테마 설치 중..."

    # macOS 확인
    if ! is_macos; then
        print_error "Xcode 테마는 macOS에서만 설치할 수 있습니다"
        print_info "현재 OS: $(uname -s)"
        return "$EXIT_UNSUPPORTED_OS"
    fi

    # 소스 디렉토리 확인
    if [[ ! -d "$XCODE_SOURCE_DIR" ]]; then
        print_error "Xcode 테마 소스 디렉토리를 찾을 수 없습니다: $XCODE_SOURCE_DIR"
        return "$EXIT_ERROR"
    fi

    # 대상 디렉토리 생성
    if ! create_dir_if_needed "$XCODE_THEMES_DIR"; then
        return "$EXIT_PERMISSION_ERROR"
    fi

    local install_count=0

    # 다크 테마 설치
    local dark_theme="$XCODE_SOURCE_DIR/GlareGuard Dark.xccolortheme"
    local dark_dest="$XCODE_THEMES_DIR/GlareGuard Dark.xccolortheme"
    if [[ -f "$dark_theme" ]]; then
        if ! backup_existing "$dark_dest" "xcode"; then
            print_warning "백업 실패로 다크 테마 설치를 건너뜁니다"
        elif copy_file "$dark_theme" "$dark_dest"; then
            ((install_count++)) || true
        fi
    else
        print_warning "다크 테마 파일 없음: $dark_theme"
    fi

    # 라이트 테마 설치
    local light_theme="$XCODE_SOURCE_DIR/GlareGuard Light.xccolortheme"
    local light_dest="$XCODE_THEMES_DIR/GlareGuard Light.xccolortheme"
    if [[ -f "$light_theme" ]]; then
        if ! backup_existing "$light_dest" "xcode"; then
            print_warning "백업 실패로 라이트 테마 설치를 건너뜁니다"
        elif copy_file "$light_theme" "$light_dest"; then
            ((install_count++)) || true
        fi
    else
        print_warning "라이트 테마 파일 없음: $light_theme"
    fi

    # 결과 출력
    if [[ $install_count -gt 0 ]]; then
        print_success "Xcode 테마 설치 완료 ($install_count개 파일)"
        echo ""
        print_info "테마를 적용하려면:"
        echo "    1. Xcode를 재시작하세요"
        echo "    2. Settings (Cmd+,) -> Themes 탭으로 이동"
        echo "    3. 'GlareGuard Dark' 또는 'GlareGuard Light' 선택"
        echo ""
        return "$EXIT_SUCCESS"
    else
        print_error "설치된 테마 파일이 없습니다"
        return "$EXIT_ERROR"
    fi
}

# ============================================================
# 직접 실행 시
# ============================================================
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_xcode
fi
