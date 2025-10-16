"""Verify complete pattern library"""
import sys
sys.path.insert(0, 'backend/app/services/enhanced_analytical_engines')

from pattern_library import PatternLibrary

pl = PatternLibrary()

print(f"Total patterns: {len(pl.patterns)}")

pattern_ids = [p['id'] for p in pl.patterns]
print(f"\nPattern IDs: {', '.join(sorted(pattern_ids))}")

# Count by segment
segments = {}
for p in pl.patterns:
    for seg in p['segments_involved']:
        segments[seg] = segments.get(seg, 0) + 1

print(f"\nPatterns per segment:")
for seg, count in sorted(segments.items()):
    print(f"  {seg}: {count}")

# Count by type
types = {}
for p in pl.patterns:
    ptype = p['type']
    types[ptype] = types.get(ptype, 0) + 1

print(f"\nPatterns by type:")
for ptype, count in sorted(types.items()):
    print(f"  {ptype}: {count}")

print(f"\nFirst pattern: {pl.patterns[0]['id']} - {pl.patterns[0]['name']}")
print(f"Last pattern: {pl.patterns[-1]['id']} - {pl.patterns[-1]['name']}")

