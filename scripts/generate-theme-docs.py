#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
SWATCH_DIR = DOCS_DIR / "swatches"

HEX_RE = re.compile(r"^#(?P<rgb>[0-9a-fA-F]{6})(?P<a>[0-9a-fA-F]{2})?$")


@dataclasses.dataclass(frozen=True)
class RGBA:
    r: int
    g: int
    b: int
    a: float  # 0..1

    def clamp(self) -> "RGBA":
        r = max(0, min(255, int(self.r)))
        g = max(0, min(255, int(self.g)))
        b = max(0, min(255, int(self.b)))
        a = max(0.0, min(1.0, float(self.a)))
        return RGBA(r=r, g=g, b=b, a=a)


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def normalize_hex(value: str) -> str | None:
    value = value.strip()
    match = HEX_RE.match(value)
    if not match:
        return None
    rgb = match.group("rgb").upper()
    a = match.group("a")
    if a is None:
        return f"#{rgb}"
    return f"#{rgb}{a.upper()}"


def hex_to_rgba(value: str) -> RGBA:
    value = value.strip()
    match = HEX_RE.match(value)
    if not match:
        die(f"invalid hex color: {value!r}")
    rgb = match.group("rgb")
    a = match.group("a")
    r = int(rgb[0:2], 16)
    g = int(rgb[2:4], 16)
    b = int(rgb[4:6], 16)
    alpha = 1.0 if a is None else int(a, 16) / 255.0
    return RGBA(r=r, g=g, b=b, a=alpha).clamp()


def rgba_to_hex(rgba: RGBA) -> str:
    rgba = rgba.clamp()
    rgb = f"#{rgba.r:02X}{rgba.g:02X}{rgba.b:02X}"
    if rgba.a >= 0.999:
        return rgb
    return f"{rgb}{round(rgba.a * 255):02X}"


def xcode_rgba_string_to_hex(value: str) -> str | None:
    parts = value.strip().split()
    if len(parts) != 4:
        return None
    try:
        r_f, g_f, b_f, a_f = (float(p) for p in parts)
    except ValueError:
        return None
    rgba = RGBA(
        r=round(r_f * 255),
        g=round(g_f * 255),
        b=round(b_f * 255),
        a=a_f,
    )
    return rgba_to_hex(rgba)


def write_text_if_changed(path: Path, content: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def svg_swatch(rgba: RGBA, *, size: int = 18) -> str:
    rgba = rgba.clamp()
    border = "#2A3346"
    fill = f"rgb({rgba.r} {rgba.g} {rgba.b})"
    fill_opacity = f"{rgba.a:.6f}".rstrip("0").rstrip(".")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">\n'
        "  <defs>\n"
        '    <pattern id="checker" width="6" height="6" patternUnits="userSpaceOnUse">\n'
        '      <rect width="6" height="6" fill="#FFFFFF"/>\n'
        '      <rect width="3" height="3" fill="#D0D0D0"/>\n'
        '      <rect x="3" y="3" width="3" height="3" fill="#D0D0D0"/>\n'
        "    </pattern>\n"
        "  </defs>\n"
        f'  <rect x="0.5" y="0.5" width="{size - 1}" height="{size - 1}" fill="url(#checker)" stroke="{border}"/>\n'
        f'  <rect x="1" y="1" width="{size - 2}" height="{size - 2}" fill="{fill}" fill-opacity="{fill_opacity}"/>\n'
        "</svg>\n"
    )


def swatch_rel_img(hex_color: str, *, size: int = 16) -> str:
    file_name = hex_color.lstrip("#").lower() + ".svg"
    return f'<img src="swatches/{file_name}" width="{size}" height="{size}" alt="{hex_color}" />'


def iter_hex_strings(obj: Any) -> Iterable[str]:
    if isinstance(obj, str):
        normalized = normalize_hex(obj)
        if normalized:
            yield normalized
        return
    if isinstance(obj, dict):
        for v in obj.values():
            yield from iter_hex_strings(v)
        return
    if isinstance(obj, list):
        for v in obj:
            yield from iter_hex_strings(v)
        return


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"failed to parse JSON: {path} ({e})")


def parse_plist_value(elem: ET.Element) -> Any:
    tag = elem.tag
    if tag == "string":
        return elem.text or ""
    if tag == "integer":
        return int((elem.text or "0").strip())
    if tag == "real":
        return float((elem.text or "0").strip())
    if tag == "true":
        return True
    if tag == "false":
        return False
    if tag == "dict":
        return parse_plist_dict(elem)
    if tag == "array":
        return [parse_plist_value(child) for child in list(elem)]
    return elem.text


def parse_plist_dict(dict_elem: ET.Element) -> dict[str, Any]:
    children = list(dict_elem)
    result: dict[str, Any] = {}
    i = 0
    while i < len(children):
        key_elem = children[i]
        if key_elem.tag != "key":
            i += 1
            continue
        key = key_elem.text or ""
        if i + 1 >= len(children):
            break
        value_elem = children[i + 1]
        result[key] = parse_plist_value(value_elem)
        i += 2
    return result


def load_xcode_theme(path: Path) -> dict[str, Any]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        die(f"failed to parse Xcode plist: {path} ({e})")
    root = tree.getroot()
    dict_elem = root.find("dict")
    if dict_elem is None:
        die(f"invalid Xcode theme plist (missing dict): {path}")
    return parse_plist_dict(dict_elem)


def load_ghostty_theme(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {"palette": {}}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = (p.strip() for p in line.split("=", 1))
        if key == "palette":
            m = re.match(r"^(?P<idx>\d+)\s*=\s*(?P<color>#?[0-9a-fA-F]{6,8})$", value)
            if not m:
                continue
            idx = int(m.group("idx"))
            color = normalize_hex(m.group("color") if m.group("color").startswith("#") else f"#{m.group('color')}")
            if color:
                data["palette"][idx] = color
            continue
        normalized = normalize_hex(value)
        if normalized:
            data[key] = normalized
        else:
            data[key] = value
    return data


def flatten_semantic_token_colors(obj: Any) -> list[tuple[str, dict[str, Any] | str]]:
    if not isinstance(obj, dict):
        return []
    out: list[tuple[str, dict[str, Any] | str]] = []
    for k, v in obj.items():
        if isinstance(v, str) or isinstance(v, dict):
            out.append((k, v))
    return out


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def md_table(rows: list[list[str]], headers: list[str]) -> str:
    cols = len(headers)
    if any(len(r) != cols for r in rows):
        die("md_table: row/column mismatch")
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * cols) + " |"]
    out.extend("| " + " | ".join(r) + " |" for r in rows)
    return "\n".join(out)


def describe_vscode_key(key: str, *, language: str) -> str:
    ko_specific: dict[str, str] = {
        "editor.background": "에디터 배경",
        "editor.foreground": "에디터 기본 텍스트(코드 본문)",
        "editorCursor.foreground": "커서 색",
        "editor.selectionBackground": "선택 영역 배경",
        "editor.selectionHighlightBorder": "선택/하이라이트 테두리(보강용)",
        "editor.lineHighlightBackground": "현재 라인 배경",
        "editorLineNumber.foreground": "라인 넘버(비활성)",
        "editorLineNumber.activeForeground": "라인 넘버(활성 라인)",
        "editorError.foreground": "오류 표시(스퀴글 등)",
        "editorWarning.foreground": "경고 표시(스퀴글 등)",
        "editorInfo.foreground": "정보 표시",
        "editorHint.foreground": "힌트/성공 표시",
        "focusBorder": "포커스 테두리(입력/패널 등)",
        "widget.border": "위젯 테두리(공통)",
        "textLink.foreground": "링크 텍스트",
        "textLink.activeForeground": "활성 링크 텍스트",
    }
    en_specific: dict[str, str] = {
        "editor.background": "Editor background",
        "editor.foreground": "Default editor text (code body)",
        "editorCursor.foreground": "Cursor",
        "editor.selectionBackground": "Selection background",
        "editor.selectionHighlightBorder": "Selection/highlight border (reinforcement)",
        "editor.lineHighlightBackground": "Current line background",
        "editorLineNumber.foreground": "Line numbers (inactive)",
        "editorLineNumber.activeForeground": "Line numbers (active line)",
        "editorError.foreground": "Error decoration (squiggles, etc.)",
        "editorWarning.foreground": "Warning decoration (squiggles, etc.)",
        "editorInfo.foreground": "Info decoration",
        "editorHint.foreground": "Hint/success decoration",
        "focusBorder": "Focus border (inputs/panels)",
        "widget.border": "Widget border (common)",
        "textLink.foreground": "Link text",
        "textLink.activeForeground": "Active link text",
    }
    specific = ko_specific if language == "ko" else en_specific
    if key in specific:
        return specific[key]

    parts = key.split(".")
    if not parts:
        return ""
    area = parts[0]
    prop = ".".join(parts[1:]) if len(parts) > 1 else ""
    if language == "ko":
        area_ko = {
            "editor": "에디터",
            "sideBar": "사이드바",
            "activityBar": "액티비티 바",
            "activityBarBadge": "액티비티 바 배지",
            "badge": "배지",
            "breadcrumb": "브레드크럼",
            "editorGutter": "가터",
            "editorGroup": "에디터 그룹",
            "editorGroupHeader": "에디터 그룹 헤더",
            "editorHoverWidget": "호버",
            "editorSuggestWidget": "자동완성(제안)",
            "editorOverviewRuler": "오버뷰 룰러",
            "editorIndentGuide": "인덴트 가이드",
            "editorRuler": "룰러",
            "editorWhitespace": "공백 표시",
            "inputValidation": "입력 검증",
            "inputOption": "입력 옵션",
            "panelTitle": "패널 타이틀",
            "progressBar": "진행 바",
            "quickInput": "커맨드 팔레트",
            "quickInputList": "커맨드 팔레트 리스트",
            "scrollbarSlider": "스크롤바",
            "peekView": "피크 뷰",
            "peekViewEditor": "피크 에디터",
            "peekViewResult": "피크 결과",
            "peekViewTitle": "피크 타이틀",
            "sideBarSectionHeader": "사이드바 섹션 헤더",
            "statusBarItem": "상태바 아이템",
            "statusBar": "상태바",
            "tab": "탭",
            "panel": "패널",
            "list": "리스트",
            "input": "입력",
            "button": "버튼",
            "dropdown": "드롭다운",
            "notification": "알림",
            "notifications": "알림",
            "peekView": "피크 뷰",
            "diffEditor": "디프",
            "gitDecoration": "Git 데코레이션",
            "terminal": "터미널",
        }.get(area, area)
        return f"{area_ko} · {prop}" if prop else area_ko
    area_en = {
        "editor": "Editor",
        "sideBar": "Sidebar",
        "activityBar": "Activity Bar",
        "activityBarBadge": "Activity Bar badge",
        "badge": "Badge",
        "breadcrumb": "Breadcrumb",
        "editorGutter": "Gutter",
        "editorGroup": "Editor group",
        "editorGroupHeader": "Editor group header",
        "editorHoverWidget": "Hover",
        "editorSuggestWidget": "Suggestions",
        "editorOverviewRuler": "Overview ruler",
        "editorIndentGuide": "Indent guides",
        "editorRuler": "Ruler",
        "editorWhitespace": "Whitespace markers",
        "inputValidation": "Input validation",
        "inputOption": "Input option",
        "panelTitle": "Panel title",
        "progressBar": "Progress bar",
        "quickInput": "Command palette",
        "quickInputList": "Command palette list",
        "scrollbarSlider": "Scrollbar",
        "peekView": "Peek View",
        "peekViewEditor": "Peek editor",
        "peekViewResult": "Peek results",
        "peekViewTitle": "Peek title",
        "sideBarSectionHeader": "Sidebar section header",
        "statusBarItem": "Status Bar item",
        "statusBar": "Status Bar",
        "tab": "Tab",
        "panel": "Panel",
        "list": "List",
        "input": "Input",
        "button": "Button",
        "dropdown": "Dropdown",
        "notification": "Notification",
        "notifications": "Notifications",
        "peekView": "Peek View",
        "diffEditor": "Diff",
        "gitDecoration": "Git decoration",
        "terminal": "Terminal",
    }.get(area, area)
    return f"{area_en} · {prop}" if prop else area_en


def describe_ghostty_key(key: str, *, language: str) -> str:
    ko: dict[str, str] = {
        "background": "터미널 배경",
        "foreground": "터미널 기본 텍스트",
        "cursor-color": "커서",
        "cursor-text": "커서 위 텍스트",
        "selection-background": "선택 영역 배경",
        "selection-foreground": "선택 영역 텍스트",
        "bold-color": "굵은 텍스트(볼드) 색",
        "split-divider-color": "분할 경계선",
        "unfocused-split-fill": "비활성 split 배경(보조)",
        "minimum-contrast": "최소 대비(렌더링 정책)",
        "palette": "ANSI 16색 팔레트",
    }
    en: dict[str, str] = {
        "background": "Terminal background",
        "foreground": "Default terminal text",
        "cursor-color": "Cursor",
        "cursor-text": "Text under cursor",
        "selection-background": "Selection background",
        "selection-foreground": "Selection text",
        "bold-color": "Bold text color",
        "split-divider-color": "Split divider",
        "unfocused-split-fill": "Unfocused split fill (secondary)",
        "minimum-contrast": "Minimum contrast (rendering policy)",
        "palette": "ANSI 16-color palette",
    }
    return (ko if language == "ko" else en).get(key, "")


def describe_xcode_key(key: str, *, language: str) -> str:
    ko: dict[str, str] = {
        "DVTSourceTextBackground": "소스 에디터 배경",
        "DVTSourceTextSelectionColor": "소스 에디터 선택 영역",
        "DVTSourceTextInsertionPointColor": "삽입점(커서)",
        "DVTSourceTextCurrentLineHighlightColor": "현재 라인 하이라이트",
        "DVTSourceTextBlockDimBackgroundColor": "블록 dim 배경(보조 영역)",
        "DVTSourceTextInvisiblesColor": "공백/보이지 않는 문자",
        "DVTConsoleTextBackgroundColor": "콘솔 배경",
        "DVTConsoleTextSelectionColor": "콘솔 선택 영역",
        "DVTConsoleTextInsertionPointColor": "콘솔 커서",
    }
    en: dict[str, str] = {
        "DVTSourceTextBackground": "Source editor background",
        "DVTSourceTextSelectionColor": "Source editor selection",
        "DVTSourceTextInsertionPointColor": "Insertion point (cursor)",
        "DVTSourceTextCurrentLineHighlightColor": "Current line highlight",
        "DVTSourceTextBlockDimBackgroundColor": "Block dim background (secondary)",
        "DVTSourceTextInvisiblesColor": "Invisibles (whitespace markers)",
        "DVTConsoleTextBackgroundColor": "Console background",
        "DVTConsoleTextSelectionColor": "Console selection",
        "DVTConsoleTextInsertionPointColor": "Console cursor",
    }
    return (ko if language == "ko" else en).get(key, "")


def describe_xcode_syntax_key(key: str, *, language: str) -> str:
    if not key.startswith("xcode.syntax."):
        return ""
    tail = key.removeprefix("xcode.syntax.")
    ko_map: dict[str, str] = {
        "plain": "일반 텍스트",
        "comment": "주석",
        "comment.doc": "문서 주석",
        "comment.doc.keyword": "문서 주석 키워드",
        "keyword": "키워드",
        "string": "문자열",
        "character": "문자",
        "number": "숫자",
        "preprocessor": "전처리기",
        "regex": "정규식",
        "regex.capturename": "정규식 캡처 이름",
        "regex.charname": "정규식 문자 이름",
        "regex.number": "정규식 숫자",
        "regex.other": "정규식 기타",
        "attribute": "어트리뷰트",
        "mark": "마크/섹션",
        "markup.code": "마크업 코드",
        "url": "URL",
        "declaration.other": "선언(기타)",
        "declaration.type": "선언(타입)",
        "identifier.class": "식별자(클래스)",
        "identifier.class.system": "식별자(시스템 클래스)",
        "identifier.constant": "식별자(상수)",
        "identifier.constant.system": "식별자(시스템 상수)",
        "identifier.function": "식별자(함수)",
        "identifier.function.system": "식별자(시스템 함수)",
        "identifier.macro": "식별자(매크로)",
        "identifier.macro.system": "식별자(시스템 매크로)",
        "identifier.type": "식별자(타입)",
        "identifier.type.system": "식별자(시스템 타입)",
        "identifier.variable": "식별자(변수)",
        "identifier.variable.system": "식별자(시스템 변수)",
    }
    en_map: dict[str, str] = {
        "plain": "Plain text",
        "comment": "Comment",
        "comment.doc": "Doc comment",
        "comment.doc.keyword": "Doc comment keyword",
        "keyword": "Keyword",
        "string": "String",
        "character": "Character",
        "number": "Number",
        "preprocessor": "Preprocessor",
        "regex": "Regex",
        "regex.capturename": "Regex capture name",
        "regex.charname": "Regex character name",
        "regex.number": "Regex number",
        "regex.other": "Regex other",
        "attribute": "Attribute",
        "mark": "Mark/section",
        "markup.code": "Markup code",
        "url": "URL",
        "declaration.other": "Declaration (other)",
        "declaration.type": "Declaration (type)",
        "identifier.class": "Identifier (class)",
        "identifier.class.system": "Identifier (system class)",
        "identifier.constant": "Identifier (constant)",
        "identifier.constant.system": "Identifier (system constant)",
        "identifier.function": "Identifier (function)",
        "identifier.function.system": "Identifier (system function)",
        "identifier.macro": "Identifier (macro)",
        "identifier.macro.system": "Identifier (system macro)",
        "identifier.type": "Identifier (type)",
        "identifier.type.system": "Identifier (system type)",
        "identifier.variable": "Identifier (variable)",
        "identifier.variable.system": "Identifier (system variable)",
    }
    return (ko_map if language == "ko" else en_map).get(tail, tail)


def generate_vscode_doc(*, language: str, sources: dict[str, Any]) -> str:
    if language == "ko":
        title = "VS Code — GlareGuard 테마 색상"
        generated = "자동 생성 문서 — 수동 편집하지 말고 `python3 scripts/generate-theme-docs.py`로 갱신하세요."
        details_all = "전체 목록 보기"
        col_desc = "설명"
        ui_summary_title = "UI (요약)"
    else:
        title = "VS Code — GlareGuard Theme Colors"
        generated = "Auto-generated — do not edit by hand; run `python3 scripts/generate-theme-docs.py` to update."
        details_all = "Show full list"
        col_desc = "Description"
        ui_summary_title = "UI (summary)"

    lines: list[str] = [f"# {title}", "", generated, ""]

    for variant_key in ["dark", "light"]:
        variant = sources[variant_key]
        vscode = variant["vscode"]
        lines.append(f"## {variant['name']}")
        lines.append("")

        ui_key_order = [
            "editor.background",
            "editor.foreground",
            "editorCursor.foreground",
            "editor.selectionBackground",
            "editor.selectionHighlightBorder",
            "editor.lineHighlightBackground",
            "editorLineNumber.foreground",
            "editorLineNumber.activeForeground",
            "editorError.foreground",
            "editorWarning.foreground",
            "editorInfo.foreground",
            "editorHint.foreground",
        ]
        ui_rows: list[list[str]] = []
        for k in ui_key_order:
            v = vscode["colors"].get(k)
            if isinstance(v, str) and normalize_hex(v):
                v_norm = normalize_hex(v) or v
                ui_rows.append([swatch_rel_img(v_norm), f"`{k}`", f"`{v_norm}`", md_escape(describe_vscode_key(k, language=language))])
        lines.extend([f"### {ui_summary_title}", "", md_table(ui_rows, ["", "Key", "Value", col_desc]), ""])

        all_ui_rows: list[list[str]] = []
        for k in sorted(vscode["colors"].keys()):
            v = vscode["colors"][k]
            if isinstance(v, str) and normalize_hex(v):
                v_norm = normalize_hex(v) or v
                all_ui_rows.append([swatch_rel_img(v_norm), f"`{k}`", f"`{v_norm}`", md_escape(describe_vscode_key(k, language=language))])
        lines.extend(
            [
                f"<details><summary>{details_all} (UI colors)</summary>",
                "",
                md_table(all_ui_rows, ["", "Key", "Value", col_desc]),
                "",
                "</details>",
                "",
            ]
        )

        token_rows: list[list[str]] = []
        for entry in vscode.get("tokenColors", []):
            settings = entry.get("settings", {}) if isinstance(entry, dict) else {}
            fg = settings.get("foreground")
            bg = settings.get("background")
            style = settings.get("fontStyle", "")
            name = entry.get("name", "") if isinstance(entry, dict) else ""
            scope = entry.get("scope", "") if isinstance(entry, dict) else ""
            if isinstance(scope, list):
                scope = ", ".join(str(s) for s in scope)
            fg_norm = normalize_hex(fg) if isinstance(fg, str) else None
            bg_norm = normalize_hex(bg) if isinstance(bg, str) else None
            token_rows.append(
                [
                    swatch_rel_img(fg_norm) if fg_norm else "",
                    f"`{md_escape(name)}`" if name else "",
                    f"`{md_escape(str(scope))}`" if scope else "",
                    f"`{fg_norm}`" if fg_norm else "",
                    f"`{bg_norm}`" if bg_norm else "",
                    f"`{md_escape(str(style))}`" if style else "",
                ]
            )
        lines.extend(
            [
                f"<details><summary>{details_all} (Token colors)</summary>",
                "",
                md_table(token_rows, ["", "Name", "Scope", "Foreground", "Background", "FontStyle"]),
                "",
                "</details>",
                "",
            ]
        )

        semantic_rows: list[list[str]] = []
        for k, v in flatten_semantic_token_colors(vscode.get("semanticTokenColors", {})):
            fg = v.get("foreground") if isinstance(v, dict) else v
            fg_norm = normalize_hex(fg) if isinstance(fg, str) else None
            semantic_rows.append([swatch_rel_img(fg_norm) if fg_norm else "", f"`{md_escape(k)}`", f"`{fg_norm}`" if fg_norm else ""])
        lines.extend(
            [
                f"<details><summary>{details_all} (Semantic token colors)</summary>",
                "",
                md_table(semantic_rows, ["", "Token", "Foreground"]),
                "",
                "</details>",
                "",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def generate_ghostty_doc(*, language: str, sources: dict[str, Any]) -> str:
    if language == "ko":
        title = "Ghostty — GlareGuard 테마 색상"
        generated = "자동 생성 문서 — 수동 편집하지 말고 `python3 scripts/generate-theme-docs.py`로 갱신하세요."
        details_all = "전체 목록 보기"
        col_desc = "설명"
    else:
        title = "Ghostty — GlareGuard Theme Colors"
        generated = "Auto-generated — do not edit by hand; run `python3 scripts/generate-theme-docs.py` to update."
        details_all = "Show full list"
        col_desc = "Description"

    lines: list[str] = [f"# {title}", "", generated, ""]

    for variant_key in ["dark", "light"]:
        variant = sources[variant_key]
        ghostty = variant["ghostty"]
        lines.append(f"## {variant['name']}")
        lines.append("")

        ghost_base_keys = [
            "background",
            "foreground",
            "cursor-color",
            "cursor-text",
            "selection-background",
            "selection-foreground",
            "bold-color",
            "split-divider-color",
            "unfocused-split-fill",
            "minimum-contrast",
        ]
        ghost_rows: list[list[str]] = []
        for k in ghost_base_keys:
            v = ghostty.get(k)
            if isinstance(v, str) and normalize_hex(v):
                v_norm = normalize_hex(v) or v
                ghost_rows.append([swatch_rel_img(v_norm), f"`{k}`", f"`{v_norm}`", md_escape(describe_ghostty_key(k, language=language))])
            elif v is not None and k == "minimum-contrast":
                ghost_rows.append(["", f"`{k}`", f"`{md_escape(str(v))}`", md_escape(describe_ghostty_key(k, language=language))])
        lines.extend(["### Base", "", md_table(ghost_rows, ["", "Key", "Value", col_desc]), ""])

        palette_rows_ghost: list[list[str]] = []
        palette = ghostty.get("palette", {})
        if isinstance(palette, dict):
            for idx in range(16):
                v = palette.get(idx)
                if isinstance(v, str) and normalize_hex(v):
                    v_norm = normalize_hex(v) or v
                    palette_rows_ghost.append([f"`{idx}`", swatch_rel_img(v_norm), f"`{v_norm}`", md_escape(describe_ghostty_key("palette", language=language))])
        lines.extend(
            [
                f"<details><summary>{details_all} (ANSI 16 palette)</summary>",
                "",
                md_table(palette_rows_ghost, ["Index", "", "Value", col_desc]),
                "",
                "</details>",
                "",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def generate_xcode_doc(*, language: str, sources: dict[str, Any]) -> str:
    if language == "ko":
        title = "Xcode — GlareGuard 테마 색상"
        generated = "자동 생성 문서 — 수동 편집하지 말고 `python3 scripts/generate-theme-docs.py`로 갱신하세요."
        details_all = "전체 목록 보기"
        col_desc = "설명"
    else:
        title = "Xcode — GlareGuard Theme Colors"
        generated = "Auto-generated — do not edit by hand; run `python3 scripts/generate-theme-docs.py` to update."
        details_all = "Show full list"
        col_desc = "Description"

    lines: list[str] = [f"# {title}", "", generated, ""]

    for variant_key in ["dark", "light"]:
        variant = sources[variant_key]
        xcode = variant["xcode"]
        lines.append(f"## {variant['name']}")
        lines.append("")

        xcode_key_order = [
            "DVTSourceTextBackground",
            "DVTSourceTextSelectionColor",
            "DVTSourceTextInsertionPointColor",
            "DVTSourceTextCurrentLineHighlightColor",
            "DVTSourceTextBlockDimBackgroundColor",
            "DVTSourceTextInvisiblesColor",
            "DVTConsoleTextBackgroundColor",
            "DVTConsoleTextSelectionColor",
            "DVTConsoleTextInsertionPointColor",
        ]
        x_rows: list[list[str]] = []
        for k in xcode_key_order:
            raw = xcode.get(k)
            raw_str = raw if isinstance(raw, str) else None
            hx = xcode_rgba_string_to_hex(raw_str) if raw_str else None
            if hx:
                x_rows.append([swatch_rel_img(hx), f"`{k}`", f"`{hx}`", f"`{raw_str}`", md_escape(describe_xcode_key(k, language=language))])
        lines.extend(["### Base", "", md_table(x_rows, ["", "Key", "Hex", "RGBA(0..1)", col_desc]), ""])

        syntax = xcode.get("DVTSourceTextSyntaxColors", {})
        syntax_rows: list[list[str]] = []
        if isinstance(syntax, dict):
            for k in sorted(syntax.keys()):
                raw = syntax[k]
                raw_str = raw if isinstance(raw, str) else None
                hx = xcode_rgba_string_to_hex(raw_str) if raw_str else None
                if hx:
                    syntax_rows.append([swatch_rel_img(hx), f"`{k}`", f"`{hx}`", f"`{raw_str}`", md_escape(describe_xcode_syntax_key(k, language=language))])
        lines.extend(
            [
                f"<details><summary>{details_all} (Syntax colors)</summary>",
                "",
                md_table(syntax_rows, ["", "Key", "Hex", "RGBA(0..1)", col_desc]),
                "",
                "</details>",
                "",
            ]
        )

    lines.append("")
    return "\n".join(lines)


def generate_index_doc(*, language: str) -> str:
    if language == "ko":
        title = "GlareGuard 테마 색상 문서"
        generated = "자동 생성 문서 — 수동 편집하지 말고 `python3 scripts/generate-theme-docs.py`로 갱신하세요."
        intro = "플랫폼별 색상 문서:"
        items = [
            ("VS Code", "vscode-colors.ko.md"),
            ("Ghostty", "ghostty-colors.ko.md"),
            ("Xcode", "xcode-colors.ko.md"),
        ]
    else:
        title = "GlareGuard Theme Color Docs"
        generated = "Auto-generated — do not edit by hand; run `python3 scripts/generate-theme-docs.py` to update."
        intro = "Platform-specific docs:"
        items = [
            ("VS Code", "vscode-colors.md"),
            ("Ghostty", "ghostty-colors.md"),
            ("Xcode", "xcode-colors.md"),
        ]

    lines: list[str] = [f"# {title}", "", generated, "", intro, ""]
    for name, file_name in items:
        lines.append(f"- {name}: [{file_name}]({file_name})")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate GitHub-friendly theme color documentation.")
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs are out of date.")
    args = parser.parse_args(argv)

    sources: dict[str, Any] = {}
    usage_by_color: dict[str, list[str]] = defaultdict(list)

    variants = {
        "dark": {
            "name": "GlareGuard Dark",
            "vscode": ROOT / "vscode/themes/glareguard-dark-color-theme.json",
            "ghostty": ROOT / "ghostty/glareguard-dark",
            "xcode": ROOT / "xcode/GlareGuard Dark.xccolortheme",
        },
        "light": {
            "name": "GlareGuard Light",
            "vscode": ROOT / "vscode/themes/glareguard-light-color-theme.json",
            "ghostty": ROOT / "ghostty/glareguard-light",
            "xcode": ROOT / "xcode/GlareGuard Light.xccolortheme",
        },
    }

    for key, paths in variants.items():
        vscode_json = load_json(paths["vscode"])
        xcode_plist = load_xcode_theme(paths["xcode"])
        ghostty_theme = load_ghostty_theme(paths["ghostty"])

        sources[key] = {
            "name": paths["name"],
            "vscode": {
                "colors": vscode_json.get("colors", {}),
                "tokenColors": vscode_json.get("tokenColors", []),
                "semanticTokenColors": vscode_json.get("semanticTokenColors", {}),
            },
            "xcode": xcode_plist,
            "ghostty": ghostty_theme,
        }

        # VS Code usage collection
        for k2, v2 in (vscode_json.get("colors", {}) or {}).items():
            if isinstance(v2, str):
                hx = normalize_hex(v2)
                if hx:
                    usage_by_color[hx].append(f"vscode:{key}:{k2}")

        for idx, entry in enumerate(vscode_json.get("tokenColors", []) or []):
            if not isinstance(entry, dict):
                continue
            scope = entry.get("scope")
            if isinstance(scope, list):
                scope_label = ", ".join(str(s) for s in scope)
            else:
                scope_label = str(scope) if scope else ""
            label = entry.get("name") or scope_label or f"tokenColors[{idx}]"
            settings = entry.get("settings", {}) if isinstance(entry.get("settings"), dict) else {}
            for field in ("foreground", "background"):
                v2 = settings.get(field)
                if isinstance(v2, str):
                    hx = normalize_hex(v2)
                    if hx:
                        usage_by_color[hx].append(f"vscode:{key}:{field}:{label}")

        for token, v2 in flatten_semantic_token_colors(vscode_json.get("semanticTokenColors", {})):
            fg = v2.get("foreground") if isinstance(v2, dict) else v2
            if isinstance(fg, str):
                hx = normalize_hex(fg)
                if hx:
                    usage_by_color[hx].append(f"vscode:{key}:semantic:{token}")

        # Ghostty usage collection
        for k2, v2 in ghostty_theme.items():
            if k2 == "palette" and isinstance(v2, dict):
                for idx, c in v2.items():
                    if isinstance(c, str):
                        hx = normalize_hex(c)
                        if hx:
                            usage_by_color[hx].append(f"ghostty:{key}:palette:{idx}")
                continue
            if isinstance(v2, str):
                hx = normalize_hex(v2)
                if hx:
                    usage_by_color[hx].append(f"ghostty:{key}:{k2}")

        # Xcode usage collection
        for k2, v2 in xcode_plist.items():
            if k2 == "DVTSourceTextSyntaxColors" and isinstance(v2, dict):
                for kk, vv in v2.items():
                    if isinstance(vv, str):
                        hx = xcode_rgba_string_to_hex(vv)
                        if hx:
                            usage_by_color[hx].append(f"xcode:{key}:syntax:{kk}")
                continue
            if isinstance(v2, str):
                hx = xcode_rgba_string_to_hex(v2)
                if hx:
                    usage_by_color[hx].append(f"xcode:{key}:{k2}")

    # Write swatches
    SWATCH_DIR.mkdir(parents=True, exist_ok=True)
    swatch_changed = False
    for hx in sorted(usage_by_color.keys()):
        rgba = hex_to_rgba(hx)
        file_path = SWATCH_DIR / (hx.lstrip("#").lower() + ".svg")
        swatch_changed |= write_text_if_changed(file_path, svg_swatch(rgba))

    outputs: list[tuple[Path, str]] = []
    outputs.append((DOCS_DIR / "theme-colors.md", generate_index_doc(language="en")))
    outputs.append((DOCS_DIR / "theme-colors.ko.md", generate_index_doc(language="ko")))

    outputs.append((DOCS_DIR / "vscode-colors.md", generate_vscode_doc(language="en", sources=sources)))
    outputs.append((DOCS_DIR / "vscode-colors.ko.md", generate_vscode_doc(language="ko", sources=sources)))

    outputs.append((DOCS_DIR / "ghostty-colors.md", generate_ghostty_doc(language="en", sources=sources)))
    outputs.append((DOCS_DIR / "ghostty-colors.ko.md", generate_ghostty_doc(language="ko", sources=sources)))

    outputs.append((DOCS_DIR / "xcode-colors.md", generate_xcode_doc(language="en", sources=sources)))
    outputs.append((DOCS_DIR / "xcode-colors.ko.md", generate_xcode_doc(language="ko", sources=sources)))

    changed_any = swatch_changed
    for path, content in outputs:
        changed_any |= write_text_if_changed(path, content)

    if args.check and changed_any:
        die("generated files are out of date; run: python3 scripts/generate-theme-docs.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
