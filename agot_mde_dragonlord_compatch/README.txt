AGOT - More Dragon Eggs + Dragonlord Regime Compatch
====================================================

Purpose
-------
1. Restore More Dragon Eggs' bottom-left dragon portrait hook after Dragonlord
   Regime's HUD override.

2. Repair Dragonlord Regime's full common/on_action/yearly_on_actions.txt
   override. Its vanilla-derived copy drops AGOT/LoV maintenance hooks,
   including agot_yearly_dragon_pulse -> agot_yearly_dragon_aging, the path that
   develops dragon personality traits between ages 3 and 14. The compatch uses
   the audited LoV/AGOT yearly file as its base and reapplies Dragonlord's three
   intentional government-specific edits.

3. Add a one-time player decision, Repair Dragon Personalities, for saves that
   spent time under the broken yearly pulse.

Repair targets
--------------
  Ages 0-2: unchanged
  Ages 3-5: 1 personality trait
  Ages 6-9: 2 personality traits
  Age 10+:  3 personality traits

When canon-dragon scripted trait development is enabled, dragons currently
marked for that scripted development are excluded from the repair.

Load after:
  - AGOT More Dragon Eggs
  - Legacy of Valyria - AGOT 0.5.2.1 Compatch (Beta)
  - AGOT Dragonlord Regime

For the supplied LoV playset, keep this immediately after AGOT Dragonlord Regime.
