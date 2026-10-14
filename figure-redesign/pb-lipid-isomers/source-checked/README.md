# Figure 1 — source-checked revision

The sole reference is the original 677 × 661 A/B schematic reattached and confirmed by the user. The uploaded 2014 PDF is not used to change this schematic's structures or assignments.

| Edition | PNG | Editable SVG | Intended placement |
|---|---|---|---|
| Complete A+B | [4800 × 3600](figure1-AB.png) | [SVG](figure1-AB.svg) | Double-column figure |
| PB/CID only, horizontal | [4800 × 1830](figure1A-PB.png) | [SVG](figure1A-PB.svg) | Wide review-triptych panel |
| PB/CID only, single column | [600 dpi at 88 mm](figure1A-PB-single-column.png) | [SVG](figure1A-PB-single-column.svg) | Narrow review-triptych panel |
| Complete A+B, vertical | [600 dpi at 88 mm](figure1-AB-single-column.png) | [SVG](figure1-AB-single-column.svg) | Tall supplement; 315.8 mm high at 88 mm width |

The PB-only editions carry panel letter **B** for the requested review-triptych use. They contain only the original Figure 1A PB/CID content; they include neither apparatus nor quantitation objects.

## Changes and checks

- Directly transcribed visible bond/atom geometry replaces the earlier generic carbon-chain generator. Wave continuation strokes remain unspecified; no hidden carbons are added from a mass-balance assumption.
- Four oxetane rings retain the two regioisomer orientations, oxygen positions, gem-dimethyl connections, and source CID assignments: m1/n1 aldehyde diagnostic products; m2/n2 dimethylalkene diagnostic products, with the matching neutral counterparts.
- Source peak order and height relation **m1 < m2 < n1 < n2** restored in overview and zoom. The paired 26 Da labels and acetone PB +58 Da are retained.
- Intensity ratio `(I_m1 + I_m2)/(I_n1 + I_n2)` stays distinct from the calibrated `C_A/C_B` relation. No direct equality is introduced.
- A is deep teal; B red-orange. Apparatus, axes and ordinary arrows are dark gray. Purple 254 nm irradiation points at the nanoESI capillary reaction region; HV and MS inlet remain in their source relationships.
- Quantitation-heading clearance, diagnostic zoom guides, card strokes and padding are revised. Neutral fragments are moved clear of side-arrow heads. Small ordinary labels are enlarged for print.

Checks include independent visual comparison with the confirmed source, SVG joint/ring/substituent assertions, label/peak relationship checks, PNG decoding, native-vector isolation of PB-only output, and identity checks on the eight transplanted scenes in the single-column compositions. SVGs contain native vector/text objects with no embedded raster image.

This is a redraw of a low-resolution schematic: coordinates and schematic plot heights are graphical reconstructions of its visible content, not newly measured experimental data. Wavy continuation marks do not specify full molecular formulae. Choose the double-column complete edition or the dedicated single-column editions rather than shrinking the wide figure to single-column width. Specific journal typography and final physical placement still determine the final print size.

## Rebuild

Install Pillow and CairoSVG in Python, then run `python build.py` and `python compose_single_column.py` from this directory. `source_chem.py` contains the reviewed semantic source geometry. See `master_layout_manifest.json` and `QA.json` for the source mapping and verification scope.
