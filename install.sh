#!/usr/bin/env bash
# GlareGuard Theme Installer
# 녹내장 사용자를 위한 IDE 테마 통합 설치 스크립트

set -euo pipefail

# ============================================================
# 초기 설정
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# 공통 함수 로드
source "$SCRIPTS_DIR/common.sh"

# 설치 플래그
INSTALL_VSCODE=false
INSTALL_GHOSTTY=false
INSTALL_XCODE=false
INTERACTIVE=true

# ============================================================
# 도움말
# ============================================================
show_help() {
    cat << EOF
${BOLD}GlareGuard Theme Installer${NC}
녹내장 사용자를 위한 IDE 테마

${BOLD}사용법:${NC}
    ./install.sh [옵션]

${BOLD}옵션:${NC}
    -h, --help       도움말 출력
    -a, --all        모든 플랫폼에 설치
    -v, --vscode     VS Code에 설치
    -g, --ghostty    Ghostty에 설치
    -x, --xcode      Xcode에 설치 (macOS 전용)
    --no-backup      기존 파일 백업 안 함

${BOLD}예시:${NC}
    ./install.sh              # 인터랙티브 메뉴
    ./install.sh --all        # 전체 설치
    ./install.sh -v -g        # VS Code와 Ghostty에 설치
    ./install.sh --vscode     # VS Code에만 설치

EOF
}

# ============================================================
# 인자 파싱
# ============================================================
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit "$EXIT_SUCCESS"
                ;;
            -a|--all)
                INSTALL_VSCODE=true
                INSTALL_GHOSTTY=true
                INSTALL_XCODE=true
                INTERACTIVE=false
                shift
                ;;
            -v|--vscode)
                INSTALL_VSCODE=true
                INTERACTIVE=false
                shift
                ;;
            -g|--ghostty)
                INSTALL_GHOSTTY=true
                INTERACTIVE=false
                shift
                ;;
            -x|--xcode)
                INSTALL_XCODE=true
                INTERACTIVE=false
                shift
                ;;
            --no-backup)
                export NO_BACKUP=true
                shift
                ;;
            *)
                print_error "알 수 없는 옵션: $1"
                echo ""
                show_help
                exit "$EXIT_INVALID_ARGS"
                ;;
        esac
    done
}

# ============================================================
# 인터랙티브 메뉴
# ============================================================
show_menu() {
    print_header

    local os_name
    os_name="$(check_os)"
    print_info "감지된 플랫폼: $os_name"
    echo ""

    echo "설치할 플랫폼을 선택하세요:"
    echo ""
    echo "  [1] VS Code"
    echo "  [2] Ghostty"
    if is_macos; then
        echo "  [3] Xcode"
        echo "  [4] 전체 설치"
    else
        echo "  [3] 전체 설치 (Xcode 제외)"
    fi
    echo "  [0] 취소"
    echo ""

    local choice
    echo -n "선택: "
    read -r choice

    case "$choice" in
        1)
            INSTALL_VSCODE=true
            ;;
        2)
            INSTALL_GHOSTTY=true
            ;;
        3)
            if is_macos; then
                INSTALL_XCODE=true
            else
                INSTALL_VSCODE=true
                INSTALL_GHOSTTY=true
            fi
            ;;
        4)
            if is_macos; then
                INSTALL_VSCODE=true
                INSTALL_GHOSTTY=true
                INSTALL_XCODE=true
            else
                print_error "잘못된 선택입니다"
                exit "$EXIT_INVALID_ARGS"
            fi
            ;;
        0)
            print_info "설치가 취소되었습니다"
            exit "$EXIT_SUCCESS"
            ;;
        *)
            print_error "잘못된 선택입니다"
            exit "$EXIT_INVALID_ARGS"
            ;;
    esac
}

# ============================================================
# 설치 실행
# ============================================================
run_installations() {
    local success_count=0
    local fail_count=0
    local skip_count=0

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # VS Code 설치
    if [[ "$INSTALL_VSCODE" == "true" ]]; then
        if source "$SCRIPTS_DIR/install-vscode.sh" && install_vscode; then
            ((success_count++))
        else
            ((fail_count++))
        fi
        echo ""
    fi

    # Ghostty 설치
    if [[ "$INSTALL_GHOSTTY" == "true" ]]; then
        if source "$SCRIPTS_DIR/install-ghostty.sh" && install_ghostty; then
            ((success_count++))
        else
            ((fail_count++))
        fi
        echo ""
    fi

    # Xcode 설치
    if [[ "$INSTALL_XCODE" == "true" ]]; then
        if ! is_macos; then
            print_warning "Xcode는 macOS에서만 설치할 수 있습니다 (건너뜀)"
            ((skip_count++))
        else
            if source "$SCRIPTS_DIR/install-xcode.sh" && install_xcode; then
                ((success_count++))
            else
                ((fail_count++))
            fi
        fi
        echo ""
    fi

    # 결과 요약
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BOLD}설치 결과 요약${NC}"
    echo ""

    if [[ $success_count -gt 0 ]]; then
        print_success "성공: $success_count개 플랫폼"
    fi
    if [[ $fail_count -gt 0 ]]; then
        print_error "실패: $fail_count개 플랫폼"
    fi
    if [[ $skip_count -gt 0 ]]; then
        print_warning "건너뜀: $skip_count개 플랫폼"
    fi
    echo ""

    if [[ $fail_count -gt 0 ]]; then
        return "$EXIT_ERROR"
    fi
    return "$EXIT_SUCCESS"
}

# ============================================================
# 메인
# ============================================================
main() {
    parse_args "$@"

    # 인터랙티브 모드
    if [[ "$INTERACTIVE" == "true" ]]; then
        show_menu
    else
        print_header
    fi

    # 선택된 플랫폼이 없으면 종료
    if [[ "$INSTALL_VSCODE" == "false" && "$INSTALL_GHOSTTY" == "false" && "$INSTALL_XCODE" == "false" ]]; then
        print_info "설치할 플랫폼이 선택되지 않았습니다"
        exit "$EXIT_SUCCESS"
    fi

    run_installations
}

main "$@"
