#!/usr/bin/env python3
"""Recompose the checked Figure 1 native scenes into optional vertical layouts.

This script never interprets or redraws molecular structures, spectrum peaks,
calibration data or concentration bars. It copies semantic SVG groups verbatim
(apart from increasing small ordinary text), and draws only inter-module arrows.
The source builder must supply the nine semantic groups listed in SCENES.
Each supplies data-layout-bounds="x y width height" in its own SVG coordinates.
Source ancestor placement transforms are intentionally not transplanted.

The complete vertical version is intentionally a tall supplemental layout. The
separate two-card PB version is the more practical single-column illustration.
"""
from __future__ import annotations

import argparse
import copy
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
TAG = lambda name: "{" + SVG + "}" + name
INK = "#333B43"
MUTED = "#667078"
TEAL = "#0B675E"

# Scene-local coordinates. Builder-supplied data-layout-bounds takes priority.
SCENES = {
    "chem-A": (42, 58, 728, 534),
    "chem-B": (830, 58, 728, 534),
    "apparatus": (42, 643, 445, 249),
    "ms1": (527, 643, 437, 249),
    "msms": (1004, 643, 554, 249),
    "diagnostic-inset": (1040, 935, 518, 174),
    "calibration": (555, 944, 405, 192),
    "concentration-bars": (99, 947, 368, 190),
    "quantitation-heading": (42, 928, 600, 35),
}


def mul(a, b):
    """Multiply two SVG affine matrices, a after b."""
    aa, ab, ac, ad, ae, af = a
    ba, bb, bc, bd, be, bf = b
    return (
        aa * ba + ac * bb, ab * ba + ad * bb,
        aa * bc + ac * bd, ab * bc + ad * bd,
        aa * be + ac * bf + ae, ab * be + ad * bf + af,
    )


def transform_matrix(value):
    m = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"([A-Za-z]+)\s*\(([^)]*)\)", value or ""):
        p = [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", args)]
        if name == "translate":
            t = (1, 0, 0, 1, p[0], p[1] if len(p) > 1 else 0)
        elif name == "scale":
            t = (p[0], 0, 0, p[1] if len(p) > 1 else p[0], 0, 0)
        elif name == "matrix":
            if len(p) != 6:
                raise ValueError("Malformed SVG matrix")
            t = tuple(p)
        elif name == "rotate":
            a = math.radians(p[0]); c, s = math.cos(a), math.sin(a)
            t = (c, s, -s, c, 0, 0)
            if len(p) == 3:
                t = mul(mul((1, 0, 0, 1, p[1], p[2]), t), (1, 0, 0, 1, -p[1], -p[2]))
        else:
            raise ValueError(f"Unsupported source transform: {name}")
        m = mul(m, t)
    return m


def matrix_attr(m):
    return "matrix(" + " ".join(f"{x:.8g}" for x in m) + ")"


def ancestor_matrix(element, parents):
    ancestors = []
    p = parents.get(element)
    while p is not None:
        ancestors.append(p); p = parents.get(p)
    m = (1, 0, 0, 1, 0, 0)
    for p in reversed(ancestors):
        m = mul(m, transform_matrix(p.get("transform")))
    return m


def ordinary_text_minimum(element, outer, minimum=22):
    """Increase tiny normal labels; preserve sub/superscript size and geometry."""
    def walk(el, matrix):
        matrix = mul(matrix, transform_matrix(el.get("transform")))
        if el.tag in (TAG("text"), TAG("tspan")) and el.get("font-size"):
            raw = el.get("font-size")
            if re.fullmatch(r"\d+(?:\.\d+)?", raw or ""):
                size = float(raw)
                text = "".join(el.itertext()).strip()
                is_index = (
                    el.get("baseline-shift") in ("sub", "super")
                    or el.get("data-index") == "true"
                    or (size <= 13 and re.fullmatch(r"[AB]|[mn][12]", text))
                )
                effective_scale = min(math.hypot(matrix[0], matrix[1]), math.hypot(matrix[2], matrix[3]))
                if not is_index and effective_scale > 0 and size * effective_scale < minimum:
                    el.set("font-size", f"{minimum / effective_scale:.4f}")
        for child in el:
            walk(child, matrix)
    walk(element, outer)


class Compose:
    def __init__(self, source: Path, width=780):
        self.tree = ET.parse(source)
        self.source = self.tree.getroot()
        self.parents = {child: parent for parent in self.source.iter() for child in parent}
        self.ids = {el.get("id"): el for el in self.source.iter() if el.get("id")}
        missing = sorted(set(SCENES) - set(self.ids))
        if missing:
            raise ValueError("Missing semantic source groups: " + ", ".join(missing))
        self.width = width
        self.margin = 32
        self.usable = width - 2 * self.margin
        self.scale = self.usable / max(self.bounds("chem-A")[2], self.bounds("chem-B")[2])
        self.root = ET.Element(TAG("svg"), {
            "width": str(width), "height": "1", "viewBox": f"0 0 {width} 1",
            "font-family": "Arial,Helvetica,sans-serif",
            "stroke-linecap": "round", "stroke-linejoin": "round",
        })
        for child in self.source:
            if child.tag == TAG("defs"):
                self.root.append(copy.deepcopy(child))
        defs = next((el for el in self.root if el.tag == TAG("defs")), None)
        if defs is None:
            defs = ET.SubElement(self.root, TAG("defs"))
        marker = ET.SubElement(defs, TAG("marker"), {
            "id": "column-arrow", "viewBox": "0 0 10 10", "refX": "8", "refY": "5",
            "markerWidth": "5", "markerHeight": "5", "orient": "auto",
        })
        ET.SubElement(marker, TAG("path"), {"d": "M0,0 L10,5 L0,10 Z", "fill": INK})
        self.background = ET.SubElement(self.root, TAG("rect"), {
            "x": "0", "y": "0", "width": str(width), "height": "1", "fill": "white",
        })
        self.positions = {}

    def bounds(self, name):
        el = self.ids[name]
        s = el.get("data-layout-bounds")
        if s:
            p = [float(x) for x in re.split(r"[,\s]+", s.strip())]
            if len(p) != 4 or min(p[2:]) <= 0:
                raise ValueError(f"Invalid data-layout-bounds on {name}")
            return tuple(p)
        return SCENES[name]

    def scene(self, name, y, scale=None):
        scale = self.scale if scale is None else scale
        sx, sy, sw, sh = self.bounds(name)
        width, height = sw * scale, sh * scale
        x = (self.width - width) / 2
        placement = (scale, 0, 0, scale, x - scale * sx, y - scale * sy)
        wrapper = ET.SubElement(self.root, TAG("g"), {
            "id": "column-" + name, "transform": matrix_attr(placement),
        })
        clone = copy.deepcopy(self.ids[name])
        clone.attrib.pop("data-layout-bounds", None)
        ordinary_text_minimum(clone, placement)
        wrapper.append(clone)
        self.positions[name] = (x, y, width, height)
        return y + height

    def text(self, text, y, size=25, color=INK, anchor="start", x=None):
        el = ET.SubElement(self.root, TAG("text"), {
            "x": str(self.margin if x is None else x), "y": str(y),
            "font-size": str(size), "fill": color, "font-weight": "700",
            "text-anchor": anchor,
        }); el.text = text

    def arrow(self, y1, y2):
        x = self.width / 2
        ET.SubElement(self.root, TAG("path"), {
            "d": f"M{x},{y1} L{x},{y2}", "fill": "none", "stroke": INK,
            "stroke-width": "2.8", "marker-end": "url(#column-arrow)",
        })

    def zoom_connectors(self, target_y):
        """Only zoom linkage is rebuilt; all four peak positions remain native."""
        ms = self.positions["msms"]
        inset_x, inset_y, inset_w, _ = self.positions["diagnostic-inset"]
        sx, sy, _, _ = self.bounds("msms")
        # Anchor metadata makes any source geometry revision explicit.
        element = self.ids["msms"]
        raw = element.get("data-diagnostic-anchor")
        if raw:
            points = [float(v) for v in re.split(r"[,\s]+", raw.strip())]
            if len(points) != 4:
                raise ValueError("data-diagnostic-anchor requires x1 y1 x2 y2")
        else:
            points = [1093, 843, 1181, 843]
        xa = ms[0] + (points[0] - sx) * self.scale
        xb = ms[0] + (points[2] - sx) * self.scale
        ya = ms[1] + (points[1] - sy) * self.scale
        yb = ms[1] + (points[3] - sy) * self.scale
        bottom = ms[1] + ms[3]
        # Route through outside gutters so neither connector crosses the title.
        routes = [
            f"M{xa:.4f},{ya:.4f} L{xa:.4f},{bottom+10:.4f} "
            f"L20,{bottom+10:.4f} L20,{target_y-12:.4f} "
            f"L{inset_x+10:.4f},{target_y:.4f}",
            f"M{xb:.4f},{yb:.4f} L{xb:.4f},{bottom+17:.4f} "
            f"L{self.width-20},{bottom+17:.4f} "
            f"L{self.width-20},{target_y-12:.4f} "
            f"L{inset_x+inset_w-10:.4f},{target_y:.4f}",
        ]
        for route in routes:
            ET.SubElement(self.root, TAG("path"), {
                "d": route,
                "fill": "none", "stroke": MUTED, "stroke-width": "1.4",
                "stroke-dasharray": "5 5",
            })

    def finish(self, filename, height):
        height = math.ceil(height)
        self.root.set("height", str(height)); self.root.set("viewBox", f"0 0 {self.width} {height}")
        self.background.set("height", str(height))
        filename.write_text(ET.tostring(self.root, encoding="unicode"), encoding="utf-8")
        import cairosvg
        # 600 dpi at the explicitly documented 88 mm journal-column width.
        png_width = round(88 / 25.4 * 600)
        cairosvg.svg2png(url=str(filename), write_to=str(filename.with_suffix(".png")),
                        output_width=png_width, output_height=round(height * png_width / self.width))
        cairosvg.svg2png(url=str(filename), write_to=str(filename.with_name(filename.stem + "-preview.png")),
                        output_width=self.width, output_height=height)
        return height


def compose_all(source, out):
    out.mkdir(parents=True, exist_ok=True)
    col = Compose(source)
    col.text("A", 38, size=30, color=TEAL)
    y = col.scene("chem-A", 57)
    y = col.scene("chem-B", y + 24)
    col.text("B", y + 54, size=30, color=TEAL)
    y += 74
    for i, name in enumerate(("apparatus", "ms1", "msms")):
        if i:
            col.arrow(y + 10, y + 37); y += 48
        y = col.scene(name, y)
    # Reuse exact native heading wording rather than creating a scientific title.
    heading = "".join(col.ids["quantitation-heading"].itertext()).strip()
    if not heading:
        raise ValueError("The native quantitation heading has no text")
    col.text(heading, y + 56, size=25)
    y += 78
    inset_start = y
    y = col.scene("diagnostic-inset", y)
    col.zoom_connectors(inset_start)
    col.arrow(y + 11, y + 40); y += 52
    y = col.scene("calibration", y)
    col.arrow(y + 11, y + 40); y += 52
    y = col.scene("concentration-bars", y)
    full_h = col.finish(out / "figure1-AB-single-column.svg", y + 34)

    pb = Compose(source)
    pb.text("B", 38, size=30, color=TEAL)
    y = pb.scene("chem-A", 57)
    y = pb.scene("chem-B", y + 24)
    pb_h = pb.finish(out / "figure1A-PB-single-column.svg", y + 34)
    report = (
        "Optional single-column layouts\n\n"
        "Source: checked native SVG semantic groups; molecular bonds, substitutions, "
        "CID structures, spectrum peaks, calibration line/points and bars are transplanted.\n"
        "Only inter-module flow arrows and zoom connectors are repositioned. Ordinary "
        "labels smaller than 22 px at 780 px width are enlarged; variable indices retain "
        "their native size.\n\n"
        f"Full A+B: 780 × {full_h} SVG units; physical size at 88 mm width is "
        f"88 × {full_h * 88 / 780:.1f} mm. This is a tall supplemental layout.\n"
        f"PB-only: 780 × {pb_h} SVG units; physical size at 88 mm width is "
        f"88 × {pb_h * 88 / 780:.1f} mm.\n"
        "PNG resolution: 600 dpi at 88 mm width.\n"
    )
    (out / "single-column-layout-notes.txt").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path(__file__).resolve().parent / "figure1-AB.svg")
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    compose_all(args.source, args.out)
