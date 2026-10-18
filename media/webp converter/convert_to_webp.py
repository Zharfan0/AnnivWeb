#!/usr/bin/env python3
"""
Konversi foto ke WebP untuk website anniversary (gratis, tanpa batas jumlah).

Cara pakai:
  1. Pasang Python 3 (python.org) lalu jalankan sekali:   pip install pillow
     (untuk foto iPhone berformat HEIC, tambahkan:        pip install pillow-heif)
  2. Taruh semua foto asli di folder  foto-asli/  (sebelahan dengan file ini).
  3. Jalankan:   python convert_to_webp.py
  4. Hasilnya ada di folder  media/  siap diunggah.

Opsi (boleh diubah):
  python convert_to_webp.py --lebar 1000 --kualitas 78
  python convert_to_webp.py --nomor          # beri nama foto-001.webp, foto-002.webp, ...
  python convert_to_webp.py --input foto-asli --output media

Catatan:
  - Foto diputar sesuai orientasi aslinya, lalu data EXIF (termasuk LOKASI GPS) DIHAPUS.
    Ini penting karena repo GitHub Pages bersifat publik.
  - Foto yang lebih kecil dari lebar target tidak dibesarkan.
  - File asli tidak diubah.
"""
import argparse, re, sys
from pathlib import Path
from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    pass

EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".bmp", ".tif", ".tiff"}

def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "foto"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="foto-asli")
    p.add_argument("--output", default="media")
    p.add_argument("--lebar", type=int, default=1000, help="lebar maksimum (px)")
    p.add_argument("--kualitas", type=int, default=78, help="kualitas WebP 1-100")
    p.add_argument("--nomor", action="store_true", help="beri nama berurutan foto-001.webp, dst")
    a = p.parse_args()

    src, dst = Path(a.input), Path(a.output)
    if not src.is_dir():
        sys.exit(f"Folder '{src}' tidak ditemukan. Buat folder itu dan isi dengan foto asli.")
    dst.mkdir(parents=True, exist_ok=True)

    files = sorted(f for f in src.iterdir() if f.suffix.lower() in EXT)
    if not files:
        sys.exit(f"Tidak ada foto di '{src}'.")

    total_in = total_out = 0
    used = set()
    for i, f in enumerate(files, 1):
        base = f"foto-{i:03d}" if a.nomor else slug(f.stem)
        name, k = base, 2
        while name in used:
            name, k = f"{base}-{k}", k + 1
        used.add(name)
        out = dst / f"{name}.webp"
        try:
            im = ImageOps.exif_transpose(Image.open(f))
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGB")
            if im.width > a.lebar:
                im = im.resize((a.lebar, round(im.height * a.lebar / im.width)), Image.LANCZOS)
            im.save(out, "WEBP", quality=a.kualitas, method=6)  # tanpa exif -> metadata terhapus
        except Exception as e:
            print(f"GAGAL  {f.name}: {e}")
            continue
        total_in += f.stat().st_size
        total_out += out.stat().st_size
        print(f"{f.name:35s} -> {out.name:30s} {out.stat().st_size/1024:7.0f} KB")

    print(f"\nSelesai: {len(used)} foto. {total_in/1e6:.1f} MB -> {total_out/1e6:.1f} MB")

if __name__ == "__main__":
    main()
