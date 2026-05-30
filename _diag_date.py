import sys
sys.path.insert(0, 'src')
from pathlib import Path
from media_manager.exiftool import read_exiftool_metadata, DATE_TAG_PRIORITY

test_dirs = [Path(r'G:\Bilder_unsortiert'), Path(r'G:\Medienspeicher')]
stats = {'exif_found': 0, 'date_found': 0, 'no_exif': 0, 'no_date': 0}
date_sources = {}

for d in test_dirs:
    if not d.exists():
        continue
    count = 0
    for f in d.rglob('*.jpg'):
        if count >= 50:
            break
        meta, success, err_type, err_msg = read_exiftool_metadata(f)
        if success and meta:
            stats['exif_found'] += 1
            found_date = False
            for key, val in meta.items():
                if 'date' in key.lower() or 'time' in key.lower():
                    if val and str(val).strip():
                        if not found_date:
                            stats['date_found'] += 1
                            found_date = True
                        src = key
                        if src not in date_sources:
                            date_sources[src] = 0
                        date_sources[src] += 1
            if not found_date:
                stats['no_date'] += 1
                print(f"  NO DATE: {f.name} - {len(meta)} tags: {list(meta.keys())[:5]}")
        else:
            stats['no_exif'] += 1
            print(f"  NO EXIF: {f.name} - {err_type}: {err_msg}")
        count += 1
    if count >= 50:
        break

total = stats['exif_found'] + stats['no_exif']
print()
print("=== DATE DIAGNOSTICS ===")
print(f"Files tested: {total}")
pct_exif = stats['exif_found'] * 100 // max(total, 1)
print(f"EXIF found: {stats['exif_found']}/{total} ({pct_exif}%)")
pct_date = stats['date_found'] * 100 // max(stats['exif_found'], 1)
print(f"Date in EXIF: {stats['date_found']}/{stats['exif_found']} ({pct_date}%)")
print(f"No date in EXIF: {stats['no_date']}")
print(f"No EXIF at all: {stats['no_exif']}")
print()
print("Date sources found (top 15):")
for src, cnt in sorted(date_sources.items(), key=lambda x: -x[1])[:15]:
    print(f"  {src}: {cnt}x")
print()
print(f"DATE_TAG_PRIORITY currently has {len(DATE_TAG_PRIORITY)} entries:")
for i, tag in enumerate(DATE_TAG_PRIORITY):
    print(f"  [{i}] {tag}")
print()
print("DATE_TAG_PRIORITY tags presence in actual data:")
found_keys = set(date_sources.keys())
for tag in DATE_TAG_PRIORITY:
    if tag in found_keys:
        print(f"  FOUND: {tag} ({date_sources[tag]}x)")
    else:
        print(f"  MISSING: {tag}")
print()
print("Tags found in data but NOT in DATE_TAG_PRIORITY:")
for tag in sorted(found_keys - set(DATE_TAG_PRIORITY)):
    print(f"  NOT IN LIST: {tag} ({date_sources[tag]}x)")
