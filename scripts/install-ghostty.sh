#!/usr/bin/env bash
# GlareGuard Theme Installer - Ghostty
# Ghostty 터미널 테마 설치 스크립트

set -euo pipefail

# 공통 함수 로드
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ============================================================
# Ghostty 설치 설정
# ============================================================
# XDG 표준 경로 (Linux/macOS 공통)
GHOSTTY_THEMES_DIR="$HOME/.config/ghostty/themes"
# macOS Application Support 경로 (대안)
GHOSTTY_MACOS_ALT_DIR="$HOME/Library/Application Support/com.mitchellh.ghostty/themes"
GHOSTTY_SOURCE_DIR="$PROJECT_ROOT/ghostty"

# ============================================================
# 메인 설치 함수
# ============================================================
install_ghostty() {
    print_step "Ghostty 테마 설치 중..."

    # 소스 파일 확인
    if [[ ! -d "$GHOSTTY_SOURCE_DIR" ]]; then
        print_error "Ghostty 테마 소스 디렉토리를 찾을 수 없습니다: $GHOSTTY_SOURCE_DIR"
        return "$EXIT_ERROR"
    fi

    # 대상 디렉토리 생성
    if ! create_dir_if_needed "$GHOSTTY_THEMES_DIR"; then
        return "$EXIT_PERMISSION_ERROR"
    fi

    local install_count=0
    local dark_theme="$GHOSTTY_SOURCE_DIR/glareguard-dark"
    local light_theme="$GHOSTTY_SOURCE_DIR/glareguard-light"

    # 다크 테마 설치
    local dark_dest="$GHOSTTY_THEMES_DIR/glareguard-dark"
    if [[ -f "$dark_theme" ]]; then
        if ! backup_existing "$dark_dest" "ghostty"; then
            print_warning "백업 실패로 다크 테마 설치를 건너뜁니다"
        elif copy_file "$dark_theme" "$dark_dest"; then
            install_count=$((install_count + 1))
        fi
    else
        print_warning "다크 테마 파일 없음: $dark_theme"
    fi

    # 라이트 테마 설치
    local light_dest="$GHOSTTY_THEMES_DIR/glareguard-light"
    if [[ -f "$light_theme" ]]; then
        if ! backup_existing "$light_dest" "ghostty"; then
            print_warning "백업 실패로 라이트 테마 설치를 건너뜁니다"
        elif copy_file "$light_theme" "$light_dest"; then
            install_count=$((install_count + 1))
        fi
    else
        print_warning "라이트 테마 파일 없음: $light_theme"
    fi

    # macOS: Application Support 경로에도 설치 (해당 경로가 존재하는 경우)
    if is_macos && [[ -d "$(dirname "$GHOSTTY_MACOS_ALT_DIR")" ]]; then
        print_info "macOS Application Support 경로에도 설치 중..."
        create_dir_if_needed "$GHOSTTY_MACOS_ALT_DIR" || true
        if [[ -d "$GHOSTTY_MACOS_ALT_DIR" ]]; then
            # 다크 테마 (백업 후 복사)
            if [[ -f "$dark_theme" ]]; then
                backup_existing "$GHOSTTY_MACOS_ALT_DIR/glareguard-dark" "ghostty-macos" || true
                copy_file "$dark_theme" "$GHOSTTY_MACOS_ALT_DIR/glareguard-dark" || true
            fi
            # 라이트 테마 (백업 후 복사)
            if [[ -f "$light_theme" ]]; then
                backup_existing "$GHOSTTY_MACOS_ALT_DIR/glareguard-light" "ghostty-macos" || true
                copy_file "$light_theme" "$GHOSTTY_MACOS_ALT_DIR/glareguard-light" || true
            fi
        fi
    fi

    # 결과 출력
    if [[ $install_count -gt 0 ]]; then
        print_success "Ghostty 테마 설치 완료 (${install_count}개 파일)"
        echo ""
        print_info "테마를 적용하려면 ~/.config/ghostty/config에 아래를 추가하세요:"
        echo ""
        echo "    theme = glareguard-dark"
        echo ""
        echo "    또는 라이트 모드:"
        echo ""
        echo "    theme = glareguard-light"
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
    install_ghostty
fi
