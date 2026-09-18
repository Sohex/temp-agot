No Cultural Tradition Cooldown
==============================

Purpose
-------
Removes ONLY the culture-scoped `tradition_cooldown` variable when you choose
the "Clear Cultural Tradition Cooldown" decision.

It does NOT change:
- tradition establishment time
- prestige costs
- tradition slot limits
- culture-head requirements
- any individual tradition

Why a decision instead of overriding common/scripted_rules/00_rules.txt?
-----------------------------------------------------------------------
AGOT/LoV currently gates tradition changes in `can_add_tradition` by checking
for the culture variable `tradition_cooldown`. Overriding that whole scripted
rules file is needlessly conflict-prone in a large mod stack.

This mod instead removes the exact variable through a zero-cost player-only
decision that appears only while the cooldown exists.

Installation
------------
Copy BOTH:
  no_cultural_tradition_cooldown.mod
  no_cultural_tradition_cooldown/

into:
  Documents/Paradox Interactive/Crusader Kings III/mod/

Enable it in the launcher. Load order should not matter, but putting it late
in the playset is harmless.
