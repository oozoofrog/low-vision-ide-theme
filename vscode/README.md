# GlareGuard (VS Code Theme)

녹내장 사용자에게 흔한 **대비 민감도 저하**, **눈부심(글레어)**, **시각 피로**를 고려해 만든 VS Code 다크 테마입니다.

## 설치

### 방법 1: VSIX 패키지로 설치 (권장)

1. 패키지 도구 설치
   ```bash
   npm install -g @vscode/vsce
   ```

2. VSIX 파일 생성
   ```bash
   cd /path/to/glareguard-theme
   vsce package
   ```

3. VS Code에 설치
   - **CLI**: `code --install-extension glareguard-theme-0.1.0.vsix`
   - **GUI**: VS Code → 확장(Extensions) → ⋯ → VSIX에서 설치...

4. VS Code 재시작 후 `Preferences: Color Theme`에서 `GlareGuard Dark` 또는 `GlareGuard Light` 선택

### 방법 2: 폴더 복사로 설치

1. 이 폴더를 아래 경로로 복사 (폴더명: `glareguard-theme`)
   - macOS/Linux: `~/.vscode/extensions/glareguard-theme`
   - Windows: `%USERPROFILE%\.vscode\extensions\glareguard-theme`

2. VS Code 재시작

3. `Preferences: Color Theme`에서 `GlareGuard Dark` 또는 `GlareGuard Light` 선택

## 설계 메모

- 배경은 완전 검정이 아닌 차콜 톤으로 눈부심을 줄였습니다.
- 선택/검색/브래킷 매칭은 과도한 배경 강조 대신 **테두리/밑줄 중심**으로 식별성을 보강합니다.
- 오류/경고/정보/힌트는 색만이 아니라(가능한 범위에서) UI 하이라이트로도 구분되도록 구성했습니다.
