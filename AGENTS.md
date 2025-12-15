# themes — AGENTS.md

## Reply Language
- 모든 응답은 한국어로 작성

## 프로젝트 목적
- 녹내장 사용자에게 흔한 `대비 민감도 저하`, `눈부심(글레어)`, `시각 피로`를 고려한 IDE 테마를 설계/구현한다.
- 장시간 코딩에서도 읽기/탐색/오류 인지가 쉬운 색/토큰 구성을 우선한다.

## 핵심 설계 원칙(필수)
- 가독성 최우선: “예쁜 테마”보다 “덜 피곤한 테마”를 우선한다.
- 눈부심 억제: 과도한 백색/고채도/형광 느낌을 피한다(채도보다 명도 대비로 강조).
- 정보 우선순위 명확화: 중요한 것만 눈에 띄게, 나머지도 충분히 읽히게.
- 색에만 의존 금지: 굵기/밑줄/테두리/박스 하이라이트/아이콘 등으로 의미를 이중화한다.

## 대비(Contrast) 권장 기준
- 기본 텍스트(코드 본문): 가능하면 `7:1` 이상 목표
- 보조 텍스트(주석/라인넘버/가터): 최소 `4.5:1`, 가능하면 `5.5:1+`
- 선택 영역(selection): 배경 대비는 `1.4~2.2:1` 정도로 “보이되 과하게 번쩍이지 않게”
  - 대신 얇은 `selection border`(또는 하이라이트)를 추가해 식별성을 보강한다.
- 포커스/활성 상태(탭/리스트/입력 포커스): 색 + 테두리(또는 굵기)로 이중화한다.

## 팔레트 설계 레시피(권장)
- 배경부터 고정
  - 다크 테마: 완전 검정보다 약간 올린 차콜 권장(예: `#0F1115 ~ #151923`)
- 텍스트 계층은 3~4단으로 제한
  - `FG(본문)` / `FG_DIM(보조)` / `COMMENT` / `DISABLED`
- 강조색(Accent)은 2~3개로 제한(저채도)
  - Warm(노랑/호박): 커서, 현재 검색 결과, 주의
  - Cool(파랑/청록): 링크/정보, 선택 테두리, 키워드 계열
  - Red: 오류
- 주석/라인넘버를 “너무 죽이지 않기”: 주석도 읽히는 대비를 확보한다.

## 반드시 커버할 토큰 체크리스트(IDE 공통)
- Editor: background/foreground, current line background, selection background/border(가능하면), cursor, whitespace/indent guides/ruler
- Syntax: keyword/type/function/variable/property/parameter, string/number, operator/punctuation, comment
- Gutter: line numbers/active line number, breakpoint, git changes(added/modified/removed)
- Search: match, current match(‘현재’ 강조는 border 중심)
- Brackets: matching, invalid/unmatched
- Diagnostics: error/warning/info/hint(텍스트 + squiggle + gutter 아이콘 + 라인/패널 하이라이트까지)
- Diff: added/modified/removed(background + border 조합 권장)
- UI: sidebar/panel/tabs/status bar/hover(tooltips)/completion/command palette, focusBorder

## 예시 팔레트 초안 (Dark / Reduced-Glare)
- Base
  - Background: `#0F1115`
  - Foreground(본문): `#E6E8EE`
  - Dim: `#B8C0D4`
  - Comment: `#8A93A6`
  - Gutter: `#808AA0`
  - UI Surface: `#121724`
  - Border/Separator: `#2A3346`
- Interaction
  - Selection Background: `#263042`
  - Selection Border: `#4AB3FF`
  - Current Line Background: `#171D2B`
  - Cursor: `#F2D06B`
  - Focus Ring: `#4AB3FF`
- Diagnostics
  - Error: `#FF5C5C`
  - Warning: `#FFB020`
  - Info: `#4AB3FF`
  - Hint/Success: `#4AD295`
- Diff(권장 조합)
  - Added: `#1D3B2E` + border `#4AD295`
  - Removed: `#3B1D1D` + border `#FF5C5C`
  - Modified: `#2C2F45` + border `#4AB3FF`

## 구현 시 주의(권장)
- “텍스트 색”과 “밑줄/테두리 색”을 분리한다.
  - 밑줄/테두리는 조금 더 진하게, 텍스트는 눈부심 덜하게
- 선택/검색 현재 매치/브래킷 매칭은 `배경 과다 강조` 대신 `border/underline` 중심으로 설계한다.
- 오류/경고는 색 + 모양(밑줄/아이콘/테두리/라인 하이라이트)을 동시에 사용한다.
