"""Build static contribution calendars from the generated snake SVGs."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

svgNamespace = "http://www.w3.org/2000/svg"
ET.register_namespace("", svgNamespace)


def buildCalendar(sourcePath, outputPath, darkMode):
    sourceRoot = ET.parse(sourcePath).getroot()
    sourceCss = sourceRoot.find(f"{svgNamespaceTag}style").text
    palette = dict(re.findall(r"--(c[0-4]|ce):([^;}]+)", sourceCss))
    cellColors = dict(re.findall(
        r"\.c\.(c[0-9a-z]+)\{fill:var\(--(c[0-4])\)", sourceCss
    ))
    background = "#0d1117" if darkMode else "#ffffff"
    foreground = "#c9d1d9" if darkMode else "#24292f"
    border = "#30363d" if darkMode else "#d0d7de"
    root = ET.Element(f"{svgNamespaceTag}svg", {
        "viewBox": "0 0 910 190", "width": "910", "height": "190",
        "role": "img", "aria-labelledby": "title description",
    })
    ET.SubElement(root, f"{svgNamespaceTag}title", {"id": "title"}).text = (
        "Fayz Liaqat's public GitHub contribution activity"
    )
    ET.SubElement(root, f"{svgNamespaceTag}desc", {"id": "description"}).text = (
        "Static contribution levels from the same rolling calendar used by "
        "the contribution snake. Regenerated with the daily snake workflow."
    )
    ET.SubElement(root, f"{svgNamespaceTag}rect", {
        "width": "909", "height": "189", "x": "0.5", "y": "0.5",
        "rx": "10", "fill": background, "stroke": border,
    })

    def addText(x, y, value, size=12):
        ET.SubElement(root, f"{svgNamespaceTag}text", {
            "x": str(x), "y": str(y), "fill": foreground,
            "font-family": "Arial, sans-serif", "font-size": str(size),
        }).text = value

    addText(32, 26, "Public contribution activity", 16)
    cells = [
        cell for cell in sourceRoot.iter(f"{svgNamespaceTag}rect")
        if "c" in cell.get("class", "").split()
    ]
    if not cells or len(palette) < 5 or not cellColors:
        raise ValueError("Generated snake SVG does not contain the expected calendar")
    for cell in cells:
        classes = cell.get("class", "").split()
        colorKey = next((cellColors[c] for c in classes if c in cellColors), "ce")
        ET.SubElement(root, f"{svgNamespaceTag}rect", {
            "x": str(float(cell.get("x")) + 32),
            "y": str(float(cell.get("y")) + 42),
            "width": "12", "height": "12", "rx": "2",
            "fill": palette[colorKey],
        })
    addText(32, 174, "Updates daily from the public contribution calendar")
    addText(720, 174, "Less")
    for level in range(5):
        ET.SubElement(root, f"{svgNamespaceTag}rect", {
            "x": str(752 + level * 16), "y": "163",
            "width": "12", "height": "12", "rx": "2",
            "fill": palette[f"c{level}"],
        })
    addText(837, 174, "More")
    ET.ElementTree(root).write(outputPath, encoding="unicode", xml_declaration=False)


svgNamespaceTag = "{" + svgNamespace + "}"
if __name__ == "__main__":
    for darkMode in (False, True):
        suffix = "-dark" if darkMode else ""
        buildCalendar(
            Path(f"dist/github-snake{suffix}.svg"),
            Path(f"dist/github-activity{suffix}.svg"),
            darkMode,
        )
