# 스크립트 가이드 (Shell)

이 저장소의 `.sh` 스크립트는 “테마를 설치하는 반복 작업”과 “테마 문서를 자동 생성/검증하는 작업”을 사람 손에서 떼어내기 위해 존재합니다.  
직접 파일을 복사/이동하는 과정에서 생기기 쉬운 실수(경로 오타, 덮어쓰기, 기존 파일 유실)를 줄이려는 목적입니다.

## 빠른 시작

```bash
# 1) 설치(대화형 메뉴)
./install.sh

# 2) 전체 설치(비대화형)
./install.sh --all

# 3) 백업 없이 설치(덮어쓰기/이동 없이 진행)
./install.sh --all --no-backup

# 4) 문서 자동 생성(색상 문서/스와치)
./scripts/generate-theme-docs.sh

# 5) 생성 결과가 최신인지 검증(CI/프리훅용)
./scripts/generate-theme-docs.sh --check
```

## 공통 동작(중요)

### 실행 환경

- 대부분의 스크립트는 `bash`를 전제로 작성되어 있습니다. (`#!/usr/bin/env bash`)
- 설치 스크립트는 현재 작업 디렉토리와 무관하게 “스크립트 위치”를 기준으로 프로젝트 루트를 찾아 동작합니다.

### 실패 동작(`set -euo pipefail`)

설치 관련 스크립트는 기본적으로 `set -euo pipefail`을 사용합니다.

- `-e`: 명령이 실패하면 즉시 종료
- `-u`: 정의되지 않은 변수를 사용하면 종료
- `pipefail`: 파이프라인 중간 실패도 실패로 처리

트러블슈팅 중 “갑자기 중간에서 멈추는 것처럼 보이는” 현상은 보통 이 설정 때문에 발생합니다.

### 백업 정책(기본: 켜짐)

파일/디렉토리를 덮어쓰기 전에, 기존 항목을 아래로 **이동(mv)** 해서 백업합니다.

- 백업 위치: `~/.glareguard-backup/<타임스탬프>/<platform>/...`
  - 예: `~/.glareguard-backup/20251216-103012/vscode/oozoofrog.glareguard-theme-0.1.0`

백업을 끄려면:

- `./install.sh --no-backup`
- 또는 환경변수: `NO_BACKUP=true ./install.sh --all`

### 종료 코드

공통 종료 코드는 `scripts/common.sh`에 정의되어 있습니다.

- `0`: 성공
- `1`: 일반 오류
- `2`: 잘못된 인자
- `3`: 지원하지 않는 OS
- `4`: 권한 문제(디렉토리 생성 등)

## 스크립트별 문서

### `install.sh` — 통합 설치 엔트리포인트

**Why (언제 쓰나)**  
VS Code / Ghostty / Xcode 테마 설치를 한 번에 처리하고, 백업/결과 요약까지 포함한 “사용자용” 설치 진입점이 필요할 때 사용합니다.

**What (실행 예시)**  

```bash
# 대화형(메뉴 선택)
./install.sh

# 전체 설치
./install.sh --all

# VS Code만 설치
./install.sh --vscode

# Ghostty + VS Code 설치
./install.sh -g -v

# 백업 없이(기존 파일 이동/보관 없이) 설치
./install.sh --all --no-backup
```

**주의사항/트러블슈팅**

- “대화형 메뉴”는 터미널 입력이 필요합니다. CI 같은 비대화형 환경에서는 `--all`/`--vscode` 같은 플래그를 사용하세요.
- Xcode 설치는 macOS에서만 동작합니다. (`--xcode` 선택 시 다른 OS에서는 건너뜀 처리)

---

### `scripts/install-vscode.sh` — VS Code 테마 설치

**Why (언제 쓰나)**  
VS Code용 테마(확장 형태)를 로컬 확장 디렉토리에 설치해서, VS Code에서 `GlareGuard Dark/Light`를 선택 가능하게 만들 때 사용합니다.  
`install.sh --vscode`가 내부에서 이 스크립트를 로드/호출합니다.

**What (실행 예시)**  

```bash
# 단독 실행(직접 호출도 가능)
./scripts/install-vscode.sh

# 통합 설치에서 호출(권장)
./install.sh --vscode
```

설치 대상 디렉토리(동적으로 결정):

- `~/.vscode/extensions/<publisher>.<name>-<version>`
- 현재 리포지토리 기준 예: `~/.vscode/extensions/oozoofrog.glareguard-theme-0.1.0`

**주의사항/트러블슈팅**

- `jq`가 있으면 `vscode/package.json`을 안전하게 파싱합니다. `jq`가 없으면 `grep/sed`로 파싱하며, `package.json` 포맷이 바뀌면 실패할 수 있습니다.
- 이전 버전(예: `oozoofrog.glareguard-theme-*`)이나 잘못된 설치(`~/.vscode/extensions/glareguard-theme`)가 있으면 백업 후 정리합니다.
- `code` 커맨드(VS Code CLI)가 없어도 파일은 설치되지만, VS Code가 즉시 인식하지 못할 수 있습니다. 설치 후 VS Code를 재시작하세요.

---

### `scripts/install-ghostty.sh` — Ghostty 테마 설치

**Why (언제 쓰나)**  
Ghostty의 테마 파일을 사용자 설정 경로에 설치해서 `theme = glareguard-dark` 같은 설정으로 적용할 수 있게 할 때 사용합니다.  
`install.sh --ghostty`가 내부에서 이 스크립트를 로드/호출합니다.

**What (실행 예시)**  

```bash
# 단독 실행
./scripts/install-ghostty.sh

# 통합 설치에서 호출(권장)
./install.sh --ghostty
```

설치 경로:

- 기본(XDG): `~/.config/ghostty/themes/`
  - `~/.config/ghostty/themes/glareguard-dark`
  - `~/.config/ghostty/themes/glareguard-light`
- macOS 대안 경로: `~/Library/Application Support/com.mitchellh.ghostty/themes/`
  - 단, `~/Library/Application Support/com.mitchellh.ghostty/`가 **이미 존재할 때만** 추가로 설치합니다.

적용 예시(사용자 설정 파일에 추가):

```ini
# ~/.config/ghostty/config
theme = glareguard-dark
```

**주의사항/트러블슈팅**

- macOS에서 Ghostty를 한 번도 실행하지 않아 `~/Library/Application Support/com.mitchellh.ghostty/`가 아직 없으면, 대안 경로 설치는 자동으로 생략될 수 있습니다.
- “테마가 보이지 않는다”면 먼저 `~/.config/ghostty/themes/`에 파일이 생성되었는지 확인하세요.

---

### `scripts/install-xcode.sh` — Xcode 테마 설치(macOS 전용)

**Why (언제 쓰나)**  
Xcode의 `FontAndColorThemes` 디렉토리에 `.xccolortheme` 파일을 설치해, Xcode 설정에서 테마를 선택할 수 있게 할 때 사용합니다.  
`install.sh --xcode`가 내부에서 이 스크립트를 로드/호출합니다.

**What (실행 예시)**  

```bash
# 단독 실행(macOS)
./scripts/install-xcode.sh

# 통합 설치에서 호출(권장)
./install.sh --xcode
```

설치 경로:

- `~/Library/Developer/Xcode/UserData/FontAndColorThemes/`
  - `GlareGuard Dark.xccolortheme`
  - `GlareGuard Light.xccolortheme`

**주의사항/트러블슈팅**

- macOS에서만 동작합니다. 다른 OS에서는 `EXIT_UNSUPPORTED_OS(3)`로 실패합니다.
- 설치 후 Xcode를 재시작해야 새 테마가 목록에 나타납니다.

---

### `scripts/check-colors.sh` — Ghostty ANSI 16색 시각 점검

**Why (언제 쓰나)**  
Ghostty 테마의 ANSI 16색(0–15)이 의도한 대로 보이는지, 대비/가독성 문제가 없는지 터미널에서 빠르게 확인할 때 사용합니다.

**What (실행 예시)**  

```bash
./scripts/check-colors.sh
```

**주의사항/트러블슈팅**

- ANSI escape를 그대로 출력합니다. ANSI 컬러를 지원하지 않는 환경(일부 로그 수집기/CI)에서는 깨져 보일 수 있습니다.
- 출력이 너무 길면 `less -R`로 스크롤하는 편이 편합니다.

```bash
./scripts/check-colors.sh | less -R
```

---

### `scripts/generate-theme-docs.sh` — 테마 문서 자동 생성/검증 래퍼

**Why (언제 쓰나)**  
테마 색상 문서(`docs/*.md`)와 스와치(`docs/swatches/*.svg`)를 “현재 테마 소스”로부터 다시 생성해서, 문서와 실제 테마가 어긋나지 않게 유지할 때 사용합니다.

**What (실행 예시)**  

```bash
# 문서/스와치 생성(변경분이 있으면 파일을 갱신)
./scripts/generate-theme-docs.sh

# 생성 결과가 최신인지 검증(최신이 아니면 실패)
./scripts/generate-theme-docs.sh --check
```

내부 동작:

- `python3 scripts/generate-theme-docs.py "$@"`를 실행하며, 인자를 그대로 전달합니다.
- `python3`가 없으면 즉시 실패합니다.

**주의사항/트러블슈팅**

- `--check`는 CI에서 “자동 생성 산출물이 커밋되어 있는지”를 검증하는 용도로 유용합니다.
- 실행 후 `docs/` 아래 파일이 변경되었다면, 생성된 파일을 함께 커밋하는 흐름을 권장합니다.

---

### `scripts/common.sh` — 공통 함수/상수 라이브러리(개발자용)

**Why (언제 쓰나)**  
설치 스크립트들이 공통으로 사용하는 출력 포맷, OS 감지, 백업/복사 유틸을 한 곳에 모아 중복과 불일치를 줄이기 위해 사용합니다.

**What (어떻게 쓰나)**  
직접 실행하는 용도가 아니라, 다른 스크립트에서 `source`로 불러 사용합니다.

```bash
source "$(dirname "$0")/common.sh"
```

**주의사항/트러블슈팅**

- 백업은 “복사”가 아니라 “이동(mv)”입니다. 설치 도중 실패했을 때 원래 위치가 비어 보이면, `~/.glareguard-backup/`에서 백업본을 확인하세요.
