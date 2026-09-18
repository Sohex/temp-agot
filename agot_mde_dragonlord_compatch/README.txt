AGOT - More Dragon Eggs + Dragonlord Regime Compatch
====================================================

Purpose
-------
Dragonlord Regime replaces gui/hud.gui after More Dragon Eggs, which removes
MDE's bottom_left_dragon_portrait instantiation.

This compatch uses Dragonlord Regime's HUD as the base and restores exactly
that MDE hook immediately before bottom_left_portrait, preserving both
Dragonlord's council-planner HUD states and MDE's intended draw order.

Load after:
  - AGOT More Dragon Eggs
  - AGOT Dragonlord Regime

For the supplied LoV playset, put it immediately after AGOT Dragonlord Regime.
