"""Prepare tracked, source-preserved Mendeley review benchmarks as CSV.

This script only reads the checked-in XLSX files. It performs no network access,
sentiment prediction, translation, or review-text rewriting.
"""

from __future__ import annotations

import csv
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VA_SOURCE = ROOT / "Datasets/VirtualAssistantDevices/raw/Virtual_Assistant_Devices_Dataset.xlsx"
VA_OUTPUT = ROOT / "Datasets/VirtualAssistantDevices/processed/virtual_assistant_reviews.csv"
BANGLA_SOURCE = ROOT / "Datasets/BanglaEcomReviewCorpus/raw/BanglaEcomReviewCorpus.xlsx"
BANGLA_OUTPUT = ROOT / "Datasets/BanglaEcomReviewCorpus/processed/bangla_ecom_reviews.csv"
SUMMARY = ROOT / "Datasets/external_benchmark_preparation_summary.json"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _column_number(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref).group(0)
    value = 0
    for char in letters:
        value = value * 26 + ord(char) - ord("A") + 1
    return value


def read_first_sheet(path: Path) -> list[dict[int, str]]:
    """Read worksheet cell values with the Python standard library only."""
    with zipfile.ZipFile(path) as book:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in book.namelist():
            shared_xml = ET.fromstring(book.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(text.text or "" for text in item.findall(".//m:t", NS))
                for item in shared_xml.findall("m:si", NS)
            ]

        workbook = ET.fromstring(book.read("xl/workbook.xml"))
        first_sheet = workbook.find("m:sheets/m:sheet", NS)
        relationship_id = first_sheet.attrib[f"{{{REL_NS}}}id"]
        relationships = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        target = next(
            relation.attrib["Target"]
            for relation in relationships
            if relation.attrib["Id"] == relationship_id
        )
        sheet_path = target.lstrip("/")
        if not sheet_path.startswith("xl/"):
            sheet_path = posixpath.normpath(posixpath.join("xl", sheet_path))

        sheet = ET.fromstring(book.read(sheet_path))
        parsed: list[dict[int, str]] = []
        for row in sheet.findall(".//m:sheetData/m:row", NS):
            cells: dict[int, str] = {}
            for cell in row.findall("m:c", NS):
                col = _column_number(cell.attrib["r"])
                cell_type = cell.attrib.get("t")
                value = cell.find("m:v", NS)
                if cell_type == "inlineStr":
                    text = "".join(
                        item.text or "" for item in cell.findall(".//m:t", NS)
                    )
                elif value is not None:
                    text = value.text or ""
                    if cell_type == "s":
                        text = shared_strings[int(text)]
                else:
                    text = ""
                cells[col] = text
            parsed.append(cells)
        return parsed


def _text(row: dict[int, str], col: int) -> str:
    return (row.get(col) or "").strip()


def _review_text(row: dict[int, str], col: int) -> str:
    """Trim workbook padding at line ends while retaining review wording."""
    value = (row.get(col) or "").strip()
    return "\n".join(line.rstrip() for line in value.splitlines())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_virtual_assistant() -> dict:
    rows = read_first_sheet(VA_SOURCE)
    if not rows:
        raise ValueError(f"No worksheet rows found in {VA_SOURCE}")

    # In the source workbook, product/manufacturer/platform cells are populated
    # at the beginning of a contiguous group and left blank on following rows.
    previous = ["", "", ""]
    counts: Counter[str] = Counter()
    device_platforms: dict[str, Counter[str]] = defaultdict(Counter)
    output_rows: list[dict[str, str]] = []
    for source_row_number, row in enumerate(rows[1:], start=2):
        for index, col in enumerate((1, 2, 3)):
            value = _text(row, col) or previous[index]
            previous[index] = value

        product, brand, platform = previous
        title, review = _text(row, 4), _review_text(row, 5)
        sentiment = _text(row, 6).upper()
        aspects = [_text(row, col) for col in range(7, 12)]
        aspects = [aspect for aspect in aspects if aspect]
        if not review or sentiment not in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
            continue
        if not product or not platform:
            raise ValueError(f"Missing product/platform at source row {source_row_number}")

        output_rows.append(
            {
                "external_id": f"VAD-{source_row_number:04d}",
                "source_platform": platform,
                "platform": {"BestBuy": "bestbuy", "Ebay": "ebay"}.get(
                    platform, platform.lower()
                ),
                "product_name": product,
                "category": "Smart Home Devices",
                "manufacturer": brand,
                "headline": title,
                "review_text": review,
                "ground_truth_sentiment": sentiment,
                "annotated_aspects": " | ".join(aspects),
            }
        )
        counts[sentiment] += 1
        device_platforms[product][platform] += 1

    VA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0]) if output_rows else []
    with VA_OUTPUT.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)

    return {
        "dataset_id": "VIRTUAL-ASSISTANT-DEVICES-2023",
        "source_file": str(VA_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": _sha256(VA_SOURCE),
        "prepared_file": str(VA_OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "prepared_sha256": _sha256(VA_OUTPUT),
        "review_count": len(output_rows),
        "platform_counts": dict(sorted(Counter(r["source_platform"] for r in output_rows).items())),
        "sentiment_counts": dict(sorted(counts.items())),
        "products": len(device_platforms),
        "products_on_multiple_platforms": sum(len(sources) > 1 for sources in device_platforms.values()),
    }


def prepare_bangla_ecom() -> dict:
    rows = read_first_sheet(BANGLA_SOURCE)
    if not rows:
        raise ValueError(f"No worksheet rows found in {BANGLA_SOURCE}")

    output_rows: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    for source_row_number, row in enumerate(rows[1:], start=2):
        review = _review_text(row, 1)
        sentiment = _text(row, 2).upper()
        translation = _text(row, 3)
        if not review or sentiment not in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
            continue
        output_rows.append(
            {
                "dataset_record_id": f"BEC-{source_row_number:05d}",
                "review_text_bn": review,
                "english_translation": translation,
                "ground_truth_sentiment": sentiment,
                "source_platform": "not_recorded_per_row",
                "product_name": "not_provided",
            }
        )
        counts[sentiment] += 1

    BANGLA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0]) if output_rows else []
    with BANGLA_OUTPUT.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)

    return {
        "dataset_id": "BANGLA-ECOM-REVIEW-CORPUS-2025-V2",
        "source_file": str(BANGLA_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": _sha256(BANGLA_SOURCE),
        "prepared_file": str(BANGLA_OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "prepared_sha256": _sha256(BANGLA_OUTPUT),
        "review_count": len(output_rows),
        "sentiment_counts": dict(sorted(counts.items())),
        "rows_with_english_translation": sum(bool(row["english_translation"]) for row in output_rows),
        "platform_names_by_row": False,
        "product_ids_by_row": False,
    }


def main() -> None:
    summary = {"datasets": [prepare_virtual_assistant(), prepare_bangla_ecom()]}
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
