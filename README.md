# FaceFusion RunPod - Ultimate Batch Processing

Dit project bevat scripts om FaceFusion op RunPod te draaien voor batch face-swap processing.

## Bestanden

- `README.md` - Deze handleiding
- `ultimaterunpod.py` - Python script voor batch processing
- `inputmedia/` - Map voor input bestanden
  - `refmodel.jpg` - Referentie gezicht (VERPLICHT)
  - Video's en foto's om te verwerken

## Vereisten

### InputMedia Map Structuur

```
facefusion-runpod/
├── README.md
├── ultimaterunpod.py
└── inputmedia/
    ├── refmodel.jpg (KRITIEK - exact deze naam!)
    ├── video1.mp4
    ├── video2.avi
    ├── photo1.jpg
    └── ...
```

### Ondersteunde Formaten

**Video's:** .mp4, .avi, .mov, .mkv, .flv, .webm
**Foto's:** .jpg, .jpeg, .png, .webp, .bmp, .tiff

### RefModel Vereisten

- Bestandsnaam: **exact** `refmodel.jpg` (kleine letters, geen spaties)
- Minimale resolutie: 100x100 pixels
- Helder, goed belicht gezicht
- Geen corrupte bestanden

## Gebruik

1. Clone deze repository op RunPod
2. Upload je inputmedia bestanden
3. Run `python ultimaterunpod.py`
4. Wacht op processing (2-4 uur voor ~1350 bestanden)
5. Download output.zip

## Kosten

RTX 5090: ~€0.90/uur
Geschatte tijd voor 1349 bestanden: 2-3 uur
Totale kosten: €2.70 - €5.00

## Output

Alle verwerkte bestanden komen in `workspace/output/`
- Elke file krijgt suffix `_swapped`
- Statistieken in `statistics.json`
- Volledige log in `fulllog.txt`

## Support

Geschreven voor Samuel Torenstra - Januari 2026
