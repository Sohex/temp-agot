# AGOT - Occult Stack Compatch v0.2.0

A deliberately narrow compatibility layer for this playset.

## What it fixes

1. **More Dragon Eggs + More Dragon Events yearly on-action collision**
   Both mods use the same `mde_yearly_on_actions.txt` pathname. With More Dragon
   Events later in load order, MDE's canon-clutch yearly registration disappears.
   This patch re-adds only the lost MDE on-actions from a unique late-loading file.

2. **More Dragon Eggs gene controls + More Dragon Events expanded dragon traits**
   Both mods define `agot_give_random_physical_traits`. This patch keeps More Dragon
   Events' expanded trait pool and rarity rules, while applying MDE's configurable
   positive / negative / neutral gene-frequency weights to that pool.

3. **Secrets of the Higher Mysteries + Legacy of Valyria magical POIs**
   SoHM uses a hardcoded magic-site whitelist. This patch preserves its original
   sites and adds a curated set of LoV volcanic / dragon-magic landmarks.

## What it intentionally does NOT replace

- `AGOT - MDE + LoV Updated Compatch` (3801630101): keep it enabled.
- `MDE + SoHM Dragon Portrait Updated Compatch` (3801630334): keep it enabled.
- Any HUD / inventory GUI.
- Magic of Westeros: no compatibility override was needed.
- Suggest Dragon Bonding: no compatibility override was needed.
- The deprecated MDE 0.5.2.1 fix (3788885215): do NOT enable it.

## Recommended relevant load order

The exact position of unrelated content mods is flexible. For the compatibility
cluster, keep the relative ordering:

1. A Game of Thrones
2. AGOT Submod Core
3. AGOT More Dragon Eggs
4. AGOT - More Dragon Events
5. Legacy of Valyria
6. Legacy of Valyria - AGOT 0.5.2.1 Compatch (Beta) (3788296332)
7. AGOT - MDE + LoV Updated Compatch (3801630101)
8. AGOT - Suggest Dragon Bonding
9. AGOT: Magic of Westeros
10. AGOT - Secrets of the Higher Mysteries
11. MDE + SoHM Dragon Portrait Updated Compatch (3801630334)
12. AGOT - Occult Stack Compatch (this mod) — LAST

Do not enable the older MDE/Higher Mysteries patch (3665748521).

## Install on Linux

Extract the archive contents directly into:

`~/.local/share/Paradox Interactive/Crusader Kings III/mod/`

You should end up with:

- `.../mod/agot_occult_stack_compatch.mod`
- `.../mod/agot_occult_stack_compatch/descriptor.mod`

Then enable **AGOT - Occult Stack Compatch** in the launcher and place it last
among the mods above.

## Validation notes

This patch is intentionally script-only. It does not include or modify graphics.

The trait merge classifies More Dragon Events' added congenital traits for MDE's
positive/negative gene selector as follows:

- Positive: agile, aerodynamic, glowing scales, large wingspan, thick scales
- Negative: obtuse, small wingspan, thin scales, withered wings
- Neutral: spindly (matching MDE's original treatment)

This is an integration decision rather than upstream behavior from either mod.
