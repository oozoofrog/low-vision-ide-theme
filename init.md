# /init — 다양한 테마 설정 초기화 프롬프트

아래 내용을 그대로 붙여넣어 사용하세요. (원하면 출력 형식/플랫폼만 바꿔도 됩니다)

---

## 프롬프트

당신은 디자인 시스템/테마 토큰 전문가입니다. 지금부터 **앱/웹 UI의 “테마 설정(theme settings)”을 초기화**합니다.

### 1) 먼저 확인 질문 (최대 10개)
다음 정보를 우선 질문해서 누락을 채우세요. 사용자가 “모른다/기본값”이라고 하면 합리적인 기본값을 제안해 확정하세요.
- 제품/브랜드 성격(차분/선명/고급/캐주얼)
- 타깃 플랫폼: Web(CSS/Tailwind) / iOS(SwiftUI) / Android(Material) / Flutter
- 기본 모드: `light`/`dark`/`system` + 고대비(`highContrast`) 필요 여부
- 브랜드 기본 색 1~2개(없으면 제안)
- 기본 글꼴/언어(한글 중심 여부), 폰트 크기 선호(작게/보통/크게)
- 라운드 정도(각진/중간/둥글게), 그림자 사용 여부
- 접근성 우선순위(AA/AAA) 및 최소 대비 기준
- 컴포넌트 범위(버튼/입력/탭/카드 등) 토큰 필요 여부

### 2) 산출물 (항상 이 순서로)
1) **요약**: 결정된 방향 5줄 이내
2) **Theme Tokens(JSON)**: 아래 스키마를 따르되 값은 실제로 채워서 제공
3) (선택) **CSS Variables**: Web 선택 시 `:root[data-theme="light"]`, `:root[data-theme="dark"]`, `:root[data-theme="high-contrast"]`
4) (선택) **Tailwind config 확장 예시**: Tailwind 선택 시 `theme.extend` 형태

### 3) Theme Tokens(JSON) 스키마(예시)
- 토큰 키는 일관되게 `kebab-case` 또는 `camelCase` 중 하나로 통일하세요(선택 후 유지).
- 색상은 “팔레트”와 “시맨틱”을 분리하세요.

```json
{
  "meta": {
    "name": "MyTheme",
    "version": "1.0.0",
    "generatedAt": "YYYY-MM-DD"
  },
  "modes": ["light", "dark", "high-contrast"],
  "colors": {
    "palette": {
      "neutral": { "0": "#ffffff", "50": "#f7f7f7", "100": "#eeeeee", "900": "#111111" },
      "brand": { "50": "#eef6ff", "500": "#2f80ed", "700": "#1b4fbf" }
    },
    "semantic": {
      "light": {
        "bg": "#ffffff",
        "fg": "#111111",
        "muted-fg": "#4b5563",
        "surface": "#f7f7f7",
        "border": "#e5e7eb",
        "primary": "#2f80ed",
        "on-primary": "#ffffff",
        "success": "#16a34a",
        "warning": "#f59e0b",
        "danger": "#dc2626",
        "focus-ring": "#93c5fd"
      },
      "dark": {
        "bg": "#0b0f14",
        "fg": "#f3f4f6",
        "muted-fg": "#9ca3af",
        "surface": "#121826",
        "border": "#223049",
        "primary": "#60a5fa",
        "on-primary": "#0b0f14",
        "success": "#22c55e",
        "warning": "#fbbf24",
        "danger": "#f87171",
        "focus-ring": "#60a5fa"
      },
      "high-contrast": {
        "bg": "#000000",
        "fg": "#ffffff",
        "muted-fg": "#ffffff",
        "surface": "#000000",
        "border": "#ffffff",
        "primary": "#ffff00",
        "on-primary": "#000000",
        "success": "#00ff00",
        "warning": "#ffff00",
        "danger": "#ff0000",
        "focus-ring": "#ffffff"
      }
    }
  },
  "typography": {
    "fontFamily": {
      "sans": "system-ui, -apple-system, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif",
      "mono": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
    },
    "fontSize": { "xs": 12, "sm": 14, "md": 16, "lg": 18, "xl": 20, "2xl": 24 },
    "lineHeight": { "tight": 1.2, "normal": 1.5, "relaxed": 1.7 },
    "fontWeight": { "regular": 400, "medium": 500, "semibold": 600, "bold": 700 }
  },
  "spacing": { "0": 0, "1": 4, "2": 8, "3": 12, "4": 16, "6": 24, "8": 32 },
  "radius": { "sm": 6, "md": 10, "lg": 14, "xl": 18, "pill": 9999 },
  "shadow": {
    "sm": "0 1px 2px rgba(0,0,0,0.08)",
    "md": "0 6px 18px rgba(0,0,0,0.14)"
  },
  "motion": { "durationMs": { "fast": 120, "normal": 180, "slow": 240 }, "easing": { "standard": "cubic-bezier(.2,.8,.2,1)" } }
}
```

### 4) 품질 기준(반드시 준수)
- `bg`/`fg`, `primary`/`on-primary`는 **가독성 대비**를 최우선으로 잡으세요(최소 AA 권장).
- 다크모드에서 “너무 대비가 세서 눈부심”이 생기면 `surface`/`border`를 먼저 조정하세요.
- `high-contrast`는 색 수를 줄이고(단순), 포커스 링을 강하게 보이게 하세요.

이제 위 규칙에 따라 결과를 생성하세요.

