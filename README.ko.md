# themes

저시력(Low Vision) 사용자에게 흔한 **대비 민감도 저하**, **눈부심(글레어)**, **시각 피로**를 고려해 “장시간 코딩에서도 덜 피곤한” 테마를 IDE/에디터별로 제공하는 저장소입니다.

## 대상 사용자(Who this is for)
- 이 저장소의 “Low Vision/저시력”은 안경/렌즈/수술로도 완전 교정이 어려운 시기능 저하 전반을 넓게 가리키며, 개인마다 증상/선호가 크게 다를 수 있습니다.
- 특히 아래와 같은 특성이 있는 분들에게 도움을 목표로 합니다.
  - 대비 민감도 저하로 코드/UI 경계가 잘 안 보임
  - 눈부심/빛 번짐(글레어)으로 밝은 배경·고채도 강조가 피곤함
  - 장시간 작업 시 시각 피로가 빠르게 누적됨
- 포함될 수 있는 예: 녹내장, 황반변성, 당뇨망막병증, 백내장, 망막색소변성 등(진단명 자체보다 “보는 방식의 어려움”을 중심으로 설계합니다).
- 참고: 이 프로젝트는 의료 조언이 아니라 **UI/색상 설계** 관점의 오픈 소스 테마 모음입니다.

### 이 프로젝트에서의 ‘녹내장’ 위치
- 초기 설계/요구사항은 녹내장 사용자에게 흔한 문제(대비 민감도 저하, 글레어, 시각 피로)에서 출발했습니다.
- 현재는 동일한 어려움이 다른 저시력 상태에서도 넓게 나타날 수 있다는 전제 아래, 문서와 원칙을 **Low Vision 전반**으로 확장해 정리합니다.

## 디렉터리 구조
- VS Code: `vscode/`
- Ghostty: `ghostty/`
- Xcode: `xcode/`
- JetBrains(예정): `jetbrains/`
- Vim(예정): `vim/`
- Neovim(예정): `neovim/`
- Sublime Text(예정): `sublime-text/`

## 테마 원칙 (Low Vision IDE Theme Spec v1 요약)

### 1) 핵심 목표
- 가독성: 코드 읽기/탐색/오류 인지(진단 메시지)가 빠르고 덜 피곤해야 함
- 눈부심 억제: 과도한 백색/고채도/‘형광 느낌’ 최소화
- 정보 우선순위 명확화: 중요한 것만 눈에 띄고, 나머지도 충분히 읽히게
- 색에만 의존 금지: 굵기/밑줄/테두리/아이콘 등으로 의미를 이중화

### 2) 대비(Contrast) 권장 기준
- 기본 텍스트(코드 본문): 가능하면 `7:1` 이상 목표
- 보조 텍스트(주석/라인넘버/가터): 최소 `4.5:1`, 가능하면 `5.5:1+`
- 선택 영역(selection):
  - 배경 대비는 `1.4~2.2:1` 정도로 “보이되 과하게 번쩍이지 않게”
  - 대신 얇은 `border`/하이라이트로 식별성 보강
- 포커스/활성 상태(탭/리스트/입력 포커스): 색 + 테두리(또는 굵기)로 이중화

### 3) 팔레트 설계 레시피
- 배경부터 고정
  - 다크: 완전 검정보다 약간 올린 차콜 권장(예: `#0F1115 ~ #151923`)
  - 라이트: 순백(#FFFFFF) 대신 오프화이트/크림 톤(예: `#F6F7FA`, `#E8E4DF`) 권장
- 텍스트 계층은 3~4단으로 제한
  - `FG(본문)` / `FG_DIM(보조)` / `COMMENT` / `DISABLED`
- 강조색(Accent)은 2~3개로 제한(저채도)
  - Warm(노랑/호박): 커서, 현재 검색 결과, 주의
  - Cool(파랑/청록): 링크/정보, 선택 테두리, 키워드 계열
  - Red: 오류
- 주석/라인넘버를 “너무 죽이지 않기”: 주석도 읽히는 대비를 확보한다.
- 의미 전달을 색 + 모양으로 이중화
  - 오류: 빨강 + 밑줄 + 좌측 아이콘 + (가능하면) 라인 subtle background
  - 선택: background 변화 + 얇은 border
  - 브래킷 매칭: background box + border
  - 검색 ‘현재 매치’: border/underline 중심, 배경은 과하지 않게

### 4) 토큰 매핑 체크리스트(빠짐 방지)
- Editor: background/foreground, current line background, selection background/border(가능하면), cursor, whitespace/indent guides, ruler
- Syntax: keyword/type/function/variable/property/parameter, string/number, operator/punctuation, comment
- Gutter: line numbers/active line number, breakpoint, git changes(added/modified/removed)
- Search: match, current match(‘현재’ 강조는 border 중심)
- Brackets: matching, invalid/unmatched
- Diagnostics: error/warning/info/hint (텍스트 + squiggle + gutter 아이콘 + 패널/라인 하이라이트까지)
- Diff: added/modified/removed (background + border 조합 권장)
- UI: sidebar/panel/tabs/status bar/hover/tooltips/completion/command palette, focusBorder

## 제공 테마(요약)
- VS Code
  - Dark: `vscode/themes/glareguard-dark-color-theme.json`
  - Light: `vscode/themes/glareguard-light-color-theme.json`
- Ghostty
  - Dark: `ghostty/glareguard-dark`
  - Light: `ghostty/glareguard-light`
- Xcode
  - Dark: `xcode/GlareGuard Dark.xccolortheme`
  - Light: `xcode/GlareGuard Light.xccolortheme`

## 8. Endpoint list / Request/response examples

### Endpoint list
이 저장소는 네트워크 API를 제공하지 않으므로 “Endpoint”는 없습니다. 대신 **테마 적용 입력(설정) → 결과(적용됨)** 관점의 예시를 제공합니다.

### Request/response examples
- Ghostty (Request)
  - `~/.config/ghostty/config`:
    - `theme = glareguard-dark`
- Ghostty (Response)
  - Ghostty가 `~/.config/ghostty/themes/glareguard-dark`를 로드해 배경/전경/ANSI 팔레트를 적용
- VS Code (Request)
  - 커맨드 팔레트 → `Preferences: Color Theme` → `GlareGuard Dark` 또는 `GlareGuard Light` 선택
- VS Code (Response)
  - `vscode/package.json`의 `contributes.themes[*]`에 등록된 JSON 테마가 에디터/터미널 UI에 적용
- Xcode (Request)
  - `~/Library/Developer/Xcode/UserData/FontAndColorThemes/`에 `.xccolortheme` 복사 후 Themes에서 선택
- Xcode (Response)
  - Xcode가 해당 plist의 `DVTSourceTextSyntaxColors` 등 값을 사용해 편집기/콘솔 색상을 적용

## 9. Configuration and Environment

### Environment variables
- 사용하지 않음

### Config files
- VS Code
  - 테마 패키지: `vscode/package.json`
  - 테마 본문: `vscode/themes/*.json`
- Ghostty
  - 테마 파일: `~/.config/ghostty/themes/*` (예: `glareguard-dark`)
  - 설정 파일: `~/.config/ghostty/config` (예: `theme = glareguard-dark`)
- Xcode
  - 테마 위치: `~/Library/Developer/Xcode/UserData/FontAndColorThemes/*.xccolortheme`

### Dev/production differences
- VS Code
  - Dev(로컬 설치): `~/.vscode/extensions/<폴더명>`에 `vscode/` 내용을 복사해 테스트
  - Production(배포): Marketplace 확장 패키징/배포(현재는 로컬 설치 중심)
- Ghostty / Xcode
  - 동일한 파일을 사용자 설정 경로로 복사해 적용(별도 빌드 단계 없음)

## 10. Known Limitations and Future Plans

### Current version constraints
- 현재는 VS Code/Ghostty/Xcode만 라이트/다크 테마를 제공
- “토큰 매핑 체크리스트” 전 항목을 모든 플랫폼에서 1:1로 커버하지 못할 수 있음(플랫폼별 지원 범위 차이)
- 대비 비율은 목표/권장 기준을 따르되, 자동 측정 파이프라인은 아직 없음

### Intentional scope limits
- 시각적 의미 전달은 “색 + 모양” 이중화를 지향하지만, 플랫폼이 제공하지 않는 UI 요소까지 강제하지 않음
- 미세한 미학(트렌디한 컬러 하모니)보다 피로/가독성 문제를 우선함

### Roadmap (if any)
- JetBrains/Vim/Neovim/Sublime Text 테마 추가(라이트/다크 동시 제공)
- High-Contrast 변형 추가(대비 최우선 모드)
- 대비 자동 측정 및 리그레션 체크(색 변경 시 기준 충족 여부 확인)
- 팔레트/토큰 매핑을 단일 소스에서 생성하는 스캐폴딩(중복 감소)

## 11. Contributing Guide

### Code conventions
- 모든 새 테마는 `light`/`dark` 쌍으로 추가한다.
- 파일/이름 규칙(권장)
  - VS Code: `vscode/themes/glareguard-{light|dark}-color-theme.json`
  - Ghostty: `ghostty/glareguard-{light|dark}`
  - Xcode: `xcode/GlareGuard {Light|Dark}.xccolortheme`
- “예쁨”보다 **가독성/눈부심 억제/정보 우선순위** 원칙을 먼저 만족시킨다.

### PR process
1. 대상 IDE 폴더에 라이트/다크 테마 파일 추가
2. 설치 문서(해당 IDE 폴더의 `README.md`)에 적용 방법 업데이트
3. 루트 `README.md`의 “제공 테마(요약)”에 파일 경로 추가

### Testing methods
- VS Code: 테마 JSON 유효성 확인(예: `python3 -m json.tool vscode/themes/*.json >/dev/null`)
- Xcode: plist 유효성 확인(예: `plutil -lint xcode/*.xccolortheme`)
- Ghostty: 테마 파일을 `~/.config/ghostty/themes/`에 복사 후 실제 적용 확인

### Analysis Process (새 IDE 추가 시 권장 순서)
#### Phase 1: Bird's Eye View
1. IDE의 테마 문서/스키마/샘플 파일 확인
2. 테마 파일이 커버하는 UI 범위 파악
3. 최소 구동 가능한 스켈레톤 확정
4. 색상/토큰 입력 포맷 정리

#### Phase 2: Architecture Understanding
1. 편집기(UI) vs 코드(구문) 토큰 분리 여부 확인
2. 선택/포커스/진단/디프 등 핵심 상호작용 토큰 매핑
3. 플랫폼이 제공하는 “모양 기반” 강조(underline/border/box) 옵션 확인
4. 적용 경로(설치 위치/설정 키) 정리

#### Phase 3: Deep Dive
1. “반드시 커버할 토큰”을 기준으로 누락 항목 점검
2. 주석/라인넘버/가터 대비가 충분한지 점검
3. 선택/검색 현재 매치/브래킷 매칭이 과하게 번쩍이지 않는지 점검
4. 진단(오류/경고/정보/힌트)이 색 + 모양으로 구분되는지 점검

#### Phase 4: Documentation
1. 루트 `README.md`의 템플릿 섹션에 맞춰 요약/설치/예시 추가
2. Request/response 예시(설정 → 적용 결과) 추가
3. Known limitations/roadmap 갱신
4. 리뷰 후 정리(중복 제거, 경로/이름 통일)
