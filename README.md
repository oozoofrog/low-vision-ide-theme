# Low Vision IDE Themes

This repository delivers IDE/editor themes for **Low Vision** users who often face reduced contrast sensitivity, glare sensitivity, and eye fatigue—prioritizing readability and ease of navigation/error recognition during long coding sessions.

> The original Korean reference lives in `README.ko.md`; this file serves as the English-first documentation.

## Directory layout
- VS Code: `vscode/`
- Ghostty: `ghostty/`
- Xcode: `xcode/`
- JetBrains (planned): `jetbrains/`
- Vim (planned): `vim/`
- Neovim (planned): `neovim/`
- Sublime Text (planned): `sublime-text/`

## Who this is for
- “Low Vision” here is used broadly: visual function that remains reduced even after standard correction, with large person-to-person variation.
- The design focuses on common interaction pain points:
  - reduced contrast sensitivity (UI boundaries and code structure are harder to parse)
  - glare/halation sensitivity (bright backgrounds and punchy accents feel harsh)
  - faster visual fatigue during prolonged work
- Examples that may fall under this umbrella include glaucoma, age-related macular degeneration, diabetic retinopathy, cataracts, retinitis pigmentosa, and more.
- Note: This is not medical advice—this is an open-source set of themes and design principles.

### Where “glaucoma” fits
- The initial design notes and constraints started from glaucoma-driven use cases (contrast sensitivity loss, glare, fatigue).
- The current documentation generalizes those requirements to Low Vision more broadly.

## Theme Principles (Low Vision IDE Theme Spec v1 summary)

### 1) Core objectives
- **Readability first:** Code reading, navigation, and diagnostic awareness must be fast and less tiring.
- **Glare suppression:** Minimize aggressive whites, oversaturated hues, and fluorescent impressions.
- **Clear information hierarchy:** Let only the most critical items stand out while keeping the rest legible.
- **Don’t rely on color alone:** Reinforce meaning through weight/underline/borders/icons in addition to color.

### 2) Contrast guidelines
- **Base text (code body):** Aim for a contrast ratio of 7:1 or higher whenever possible.
- **Secondary text (comments, line numbers, gutter):** Minimum of 4.5:1; target 5.5:1+ if feasible.
- **Selection ranges:**
  - Keep background contrast in the 1.4:1 to 2.2:1 range so selections are visible without flashy brightness.
  - Add a fine selection border or highlight to improve recognition.
- **Focused/active states (tabs, lists, inputs):** Combine color with borders or weight changes for redundancy.

### 3) Palette recipe
- **Fix the background first**
  - Dark: prefer slightly lightened charcoal over pure black (`#0F1115` to `#151923`).
  - Light: avoid stark white; opt for off-white/cream tones such as `#F6F7FA` or `#E8E4DF`.
- **Limit text hierarchy to 3–4 levels**
  - `FG` (main text) / `FG_DIM` (secondary) / `COMMENT` / `DISABLED`
- **Limit accent colors to 2–3 desaturated hues**
  - Warm (yellow/amber): cursor, current search result, warnings.
  - Cool (blue/teal): links/info, selection borders, keyword variants.
  - Red: errors.
- **Keep comments/line numbers readable:** Do not push them too dim—ensure adequate contrast.
- **Double-up meaning using color + shape**
  - Errors: red + underline + left gutter icon + subtle line background when possible.
  - Selections: combine background shift with a thin border.
  - Bracket matches: use a faint box + border.
  - Current search matches: prioritize border/underline emphasis instead of overpowering backgrounds.

### 4) Token coverage checklist (non-negotiable)
- **Editor:** background/foreground, current line background, selection background/border (if available), cursor, whitespace/indent guides, ruler.
- **Syntax:** keyword/type/function/variable/property/parameter, string/number, operator/punctuation, comment.
- **Gutter:** line numbers/active line number, breakpoint, git diff indicators (added/modified/removed).
- **Search:** general matches, current match (emphasize border for current match).
- **Brackets:** matching, invalid/unmatched.
- **Diagnostics:** error/warning/info/hint (text + squiggles + gutter icons + panel/line highlights if supported).
- **Diff:** added/modified/removed (prefer background + border combinations).
- **UI:** sidebar/panel/tabs/status bar/tooltips/completion/command palette, focus borders.

## Provided themes (summary)
- **VS Code**
  - Dark: `vscode/themes/glareguard-dark-color-theme.json`
  - Light: `vscode/themes/glareguard-light-color-theme.json`
- **Ghostty**
  - Dark: `ghostty/glareguard-dark`
  - Light: `ghostty/glareguard-light`
- **Xcode**
  - Dark: `xcode/GlareGuard Dark.xccolortheme`
  - Light: `xcode/GlareGuard Light.xccolortheme`

## Color reference (auto-generated)
- Docs: `docs/theme-colors.md` (EN), `docs/theme-colors.ko.md` (KO)
- Update: `python3 scripts/generate-theme-docs.py` (CI-friendly: `python3 scripts/generate-theme-docs.py --check`)

## 8. Endpoint list / Request-response examples

### Endpoint list
This repository does not expose network APIs. Instead, we document the *input (configuration)* → *result (theme applied)* flow for each platform.

### Request / response examples
- **Ghostty**
  - Request: edit `~/.config/ghostty/config` with `theme = glareguard-dark`.
  - Response: Ghostty loads `~/.config/ghostty/themes/glareguard-dark` and applies the background/foreground/ANSI palette.
- **VS Code**
  - Request: open the Command Palette → `Preferences: Color Theme` → select `GlareGuard Dark` or `GlareGuard Light`.
  - Response: VS Code applies the theme defined in `vscode/package.json` under `contributes.themes[*]` to the editor and UI.
- **Xcode**
  - Request: copy `.xccolortheme` files into `~/Library/Developer/Xcode/UserData/FontAndColorThemes/` and choose the theme via the Themes preferences.
  - Response: Xcode reads values such as `DVTSourceTextSyntaxColors` from the plist and colors the editor/console accordingly.

## 9. Configuration and environment

### Environment variables
- Not used.

### Config files
- **VS Code**
  - Theme package: `vscode/package.json`
  - Theme definitions: `vscode/themes/*.json`
- **Ghostty**
  - Theme files: `~/.config/ghostty/themes/*` (e.g., `glareguard-dark`)
  - Settings file: `~/.config/ghostty/config` (e.g., `theme = glareguard-dark`)
- **Xcode**
  - Theme location: `~/Library/Developer/Xcode/UserData/FontAndColorThemes/*.xccolortheme`

### Dev vs. production
- **VS Code**
  - Dev (local testing): copy `vscode/` into `~/.vscode/extensions/<folder>/`.
  - Production (packaging): bundle as a Marketplace extension (currently local installs are the focus).
- **Ghostty / Xcode**
  - Apply by copying the same files into the user's config paths; no separate build.

## 10. Known limitations and future plans

### Current constraints
- Only VS Code, Ghostty, and Xcode currently provide both light and dark variants.
- Not every platform may cover every token from the “must-have token checklist” due to API differences.
- Contrast goals are followed manually; there is no automated measurement pipeline yet.

### Intentional scope limits
- While we aim for color + shape redundancy, we do not force UI effects that a platform cannot render.
- Prioritize reducing fatigue/readability issues over pursuing trendy color harmonies.

### Roadmap
- Add JetBrains, Vim, Neovim, and Sublime Text themes with light/dark pairs.
- Introduce dedicated high-contrast variants (contrast-first mode).
- Automate contrast measurement and regression checks when colors change.
- Generate palettes/token mappings from a single source to reduce duplication.

## 11. Contributing guide

### Code conventions
- Every new theme must come with a light/dark pair.
- File/name conventions (recommended):
  - VS Code: `vscode/themes/glareguard-{light|dark}-color-theme.json`
  - Ghostty: `ghostty/glareguard-{light|dark}`
  - Xcode: `xcode/GlareGuard {Light|Dark}.xccolortheme`
- Put readability, glare suppression, and information hierarchy ahead of purely “pretty” palettes.

### PR process
1. Add light/dark theme files to the target IDE folder.
2. Update the IDE’s `README.md` with installation instructions.
3. Update the root `README.md` summary to list the new files.

### Testing methods
- **VS Code:** validate JSON (`python3 -m json.tool vscode/themes/*.json >/dev/null`).
- **Xcode:** lint plists (`plutil -lint xcode/*.xccolortheme`).
- **Ghostty:** copy themes into `~/.config/ghostty/themes/` and verify visually.

### Analysis process (recommended for new IDEs)
#### Phase 1: Bird’s-eye View
1. Review the IDE’s theme documentation/schema samples.
2. Identify the UI surface coverage of the existing theme files.
3. Establish the minimal scaffolding that works.
4. Document the required color/token inputs.

#### Phase 2: Architecture understanding
1. Separate UI chrome vs. syntax tokens.
2. Map key interaction tokens: selection, focus, diagnostics, diffs.
3. Identify shape-based emphasis options (underline/border/box).
4. Clarify installation paths or settings keys.

#### Phase 3: Deep dive
1. Ensure every “must-cover token” exists.
2. Check that comments/line numbers/gutter maintain readable contrast.
3. Confirm selections/search matches/bracket highlights avoid blinding backgrounds.
4. Verify diagnostics use color + shape differentiation.

#### Phase 4: Documentation
1. Update the root `README.md` template sections with summaries/installation/examples.
2. Add request/response (config → applied) examples.
3. Refresh known limitations and roadmap entries.
4. Review for duplication and naming consistency before merging.
