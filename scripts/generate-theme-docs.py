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


def generate_docs(*, language: str, sources: dict[str, Any], usage_by_color: dict[str, list[str]]) -> str:
    if language == "ko":
        title = "GlareGuard 테마 색상 레퍼런스"
        generated = "자동 생성 문서 — 수동 편집하지 말고 `python3 scripts/generate-theme-docs.py`로 갱신하세요."
        palette_title = "전체 팔레트(플랫폼 합집합)"
        variant_title = "테마 변형"
        platform_vscode = "VS Code"
        platform_ghostty = "Ghostty"
        platform_xcode = "Xcode"
        details_all = "전체 목록 보기"
    else:
        title = "GlareGuard Theme Color Reference"
        generated = "Auto-generated — do not edit by hand; run `python3 scripts/generate-theme-docs.py` to update."
        palette_title = "Global palette (union across platforms)"
        variant_title = "Theme variants"
        platform_vscode = "VS Code"
        platform_ghostty = "Ghostty"
        platform_xcode = "Xcode"
        details_all = "Show full list"

    lines: list[str] = [f"# {title}", "", generated, ""]

    all_colors = sorted(usage_by_color.keys())
    palette_rows: list[list[str]] = []
    for c in all_colors:
        usages = usage_by_color[c]
        sample = ", ".join(usages[:4]) + (f" (+{len(usages) - 4})" if len(usages) > 4 else "")
        palette_rows.append([swatch_rel_img(c), f"`{c}`", f"`{len(usages)}`", md_escape(sample)])
    lines.extend([f"## {palette_title}", "", md_table(palette_rows, ["", "Hex", "Count", "Examples"]), ""])

    lines.append(f"## {variant_title}")
    lines.append("")

    for variant_key in ["dark", "light"]:
        variant = sources[variant_key]
        lines.append(f"### {variant['name']}")
        lines.append("")

        # VS Code
        vscode = variant["vscode"]
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
                ui_rows.append([swatch_rel_img(normalize_hex(v) or v), f"`{k}`", f"`{normalize_hex(v)}`"])
        lines.extend([f"#### {platform_vscode}", "", md_table(ui_rows, ["", "Key", "Value"]), ""])

        all_ui_rows: list[list[str]] = []
        for k in sorted(vscode["colors"].keys()):
            v = vscode["colors"][k]
            if isinstance(v, str) and normalize_hex(v):
                v_norm = normalize_hex(v) or v
                all_ui_rows.append([swatch_rel_img(v_norm), f"`{k}`", f"`{v_norm}`"])
        lines.extend(
            [
                f"<details><summary>{details_all} (UI colors)</summary>",
                "",
                md_table(all_ui_rows, ["", "Key", "Value"]),
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
            semantic_rows.append(
                [
                    swatch_rel_img(fg_norm) if fg_norm else "",
                    f"`{md_escape(k)}`",
                    f"`{fg_norm}`" if fg_norm else "",
                ]
            )
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

        # Ghostty
        ghostty = variant["ghostty"]
        ghost_base_keys = [
            "background",
            "foreground",
            "cursor-color",
            "cursor-text",
            "selection-background",
            "selection-foreground",
            "bold-color",
            "split-divider-color",
        ]
        ghost_rows: list[list[str]] = []
        for k in ghost_base_keys:
            v = ghostty.get(k)
            if isinstance(v, str) and normalize_hex(v):
                v_norm = normalize_hex(v) or v
                ghost_rows.append([swatch_rel_img(v_norm), f"`{k}`", f"`{v_norm}`"])
        lines.extend([f"#### {platform_ghostty}", "", md_table(ghost_rows, ["", "Key", "Value"]), ""])

        palette_rows_ghost: list[list[str]] = []
        palette = ghostty.get("palette", {})
        if isinstance(palette, dict):
            for idx in range(16):
                v = palette.get(idx)
                if isinstance(v, str) and normalize_hex(v):
                    v_norm = normalize_hex(v) or v
                    palette_rows_ghost.append([f"`{idx}`", swatch_rel_img(v_norm), f"`{v_norm}`"])
        lines.extend(
            [
                f"<details><summary>{details_all} (ANSI 16 palette)</summary>",
                "",
                md_table(palette_rows_ghost, ["Index", "", "Value"]),
                "",
                "</details>",
                "",
            ]
        )

        # Xcode
        xcode = variant["xcode"]
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
                x_rows.append([swatch_rel_img(hx), f"`{k}`", f"`{hx}`", f"`{raw_str}`"])
        lines.extend([f"#### {platform_xcode}", "", md_table(x_rows, ["", "Key", "Hex", "RGBA(0..1)"]), ""])

        syntax = xcode.get("DVTSourceTextSyntaxColors", {})
        syntax_rows: list[list[str]] = []
        if isinstance(syntax, dict):
            for k in sorted(syntax.keys()):
                raw = syntax[k]
                raw_str = raw if isinstance(raw, str) else None
                hx = xcode_rgba_string_to_hex(raw_str) if raw_str else None
                if hx:
                    syntax_rows.append([swatch_rel_img(hx), f"`{k}`", f"`{hx}`", f"`{raw_str}`"])
        lines.extend(
            [
                f"<details><summary>{details_all} (Syntax colors)</summary>",
                "",
                md_table(syntax_rows, ["", "Key", "Hex", "RGBA(0..1)"]),
                "",
                "</details>",
                "",
            ]
        )

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
    outputs.append((DOCS_DIR / "theme-colors.md", generate_docs(language="en", sources=sources, usage_by_color=usage_by_color)))
    outputs.append((DOCS_DIR / "theme-colors.ko.md", generate_docs(language="ko", sources=sources, usage_by_color=usage_by_color)))

    changed_any = swatch_changed
    for path, content in outputs:
        changed_any |= write_text_if_changed(path, content)

    if args.check and changed_any:
        die("generated files are out of date; run: python3 scripts/generate-theme-docs.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
