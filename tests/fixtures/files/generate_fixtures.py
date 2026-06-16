"""Generate binary test fixtures for upload scenarios. Run once or via session fixture."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent

# Minimal 1x1 PNG
_MINIMAL_PNG = bytes(
    [
        0x89,
        0x50,
        0x4E,
        0x47,
        0x0D,
        0x0A,
        0x1A,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x0D,
        0x49,
        0x48,
        0x44,
        0x52,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x01,
        0x08,
        0x06,
        0x00,
        0x00,
        0x00,
        0x1F,
        0x15,
        0xC4,
        0x89,
        0x00,
        0x00,
        0x00,
        0x0A,
        0x49,
        0x44,
        0x41,
        0x54,
        0x78,
        0x9C,
        0x63,
        0x00,
        0x01,
        0x00,
        0x00,
        0x05,
        0x00,
        0x01,
        0x0D,
        0x0A,
        0x2D,
        0xB4,
        0x00,
        0x00,
        0x00,
        0x00,
        0x49,
        0x45,
        0x4E,
        0x44,
        0xAE,
        0x42,
        0x60,
        0x82,
    ]
)

_MINIMAL_PDF = b"""%PDF-1.1
1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj
2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj
3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000052 00000 n 
0000000101 00000 n 
trailer<< /Root 1 0 R /Size 4 >>
startxref
178
%%EOF"""


def ensure_fixtures() -> dict[str, Path]:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    paths = {
        "valid_png": FIXTURES_DIR / "valid_property_photo.png",
        "valid_jpg": FIXTURES_DIR / "valid_property_photo.jpg",
        "invalid_photo_pdf": FIXTURES_DIR / "invalid_photo.pdf",
        "invalid_photo_gif": FIXTURES_DIR / "invalid_photo.gif",
        "valid_pdf": FIXTURES_DIR / "valid_document.pdf",
        "invalid_doc_mp4": FIXTURES_DIR / "invalid_document.mp4",
        "invalid_doc_zip": FIXTURES_DIR / "invalid_document.zip",
    }

    paths["valid_png"].write_bytes(_MINIMAL_PNG)
    paths["valid_jpg"].write_bytes(_MINIMAL_PNG)
    paths["invalid_photo_pdf"].write_bytes(_MINIMAL_PDF)
    paths["invalid_photo_gif"].write_bytes(b"GIF89a\x01\x00\x01\x00\x00\x00\x00!")
    paths["valid_pdf"].write_bytes(_MINIMAL_PDF)
    paths["invalid_doc_mp4"].write_bytes(b"\x00\x00\x00\x20ftypmp41")
    paths["invalid_doc_zip"].write_bytes(b"PK\x03\x04")

    oversized_photo = FIXTURES_DIR / "oversized_photo.png"
    if not oversized_photo.exists() or oversized_photo.stat().st_size < 10 * 1024 * 1024:
        with oversized_photo.open("wb") as handle:
            handle.seek(11 * 1024 * 1024 - 1)
            handle.write(b"\0")
    paths["oversized_photo"] = oversized_photo

    oversized_doc = FIXTURES_DIR / "oversized_document.pdf"
    if not oversized_doc.exists() or oversized_doc.stat().st_size < 10 * 1024 * 1024:
        with oversized_doc.open("wb") as handle:
            handle.write(_MINIMAL_PDF)
            handle.seek(11 * 1024 * 1024 - 1)
            handle.write(b"\0")
    paths["oversized_document"] = oversized_doc

    return paths


if __name__ == "__main__":
    ensure_fixtures()
    print(f"Fixtures ready in {FIXTURES_DIR}")
