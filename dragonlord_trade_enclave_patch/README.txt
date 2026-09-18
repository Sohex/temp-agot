Dragonlord Regime - Trade Enclave War
=====================================

Purpose
-------
Adds a fifth Dragonlord Council war policy: Trade Enclave War.

Flow
----
1. Convene the Dragonlord Council.
2. Choose War.
3. Choose "Trade Enclave War".
4. Select an independent ruler in diplomatic range whose realm contains at
   least one coastal county.
5. Pass the council motion normally.
6. The normal one-year, single-use Dragonlord war authorization is granted.
7. Declare "Trade Enclave War" against the approved ruler.
8. Choose ONE coastal county in that ruler's realm as the war target.
9. Victory transfers only that county directly to the First Lord.

Deliberate limits
-----------------
- Exactly one county.
- County must be coastal.
- No mine requirement.
- No automatic culture or faith conversion.
- No special trade-income modifier.
- No conversion of the defeated realm into a Free Trade City.
- Uses a dedicated CB group, so authorization does NOT reopen ordinary county
  conquest or Dragon Conquest CBs.

UI note
-------
This patch deliberately does not replace Dragonlord Regime's ~2,700-line
council GUI file. Instead it adds the fifth selector as a tiny overlay beneath
the native four war buttons. This greatly reduces compatibility risk when the
base mod updates.

At normal UI scale the button should sit beneath Slave Raid. If a custom UI
scale or another UI mod displaces it, the mechanics are unaffected; only the
overlay position would need adjustment.

Installation
------------
Copy BOTH:
  dragonlord_trade_enclave_patch.mod
  dragonlord_trade_enclave_patch/

to:
  Documents/Paradox Interactive/Crusader Kings III/mod/

Enable it and load it AFTER:
  AGOT Dragonlord Regime

For this playset, putting it late (after the Dragonlord/Ancient Birthright
compatibility patch) is safest.


v1.1 UI fix
-----------
v1.0's standalone selector could be hidden behind the full-screen council
planner. v1.1 moves it to CK3's top UI layer and anchors it to screen center.

A fallback minor decision, "Propose a Trade Enclave War", is also included.
It opens the ordinary Dragonlord Council planner directly with Trade Enclave
War selected. The actual vote, cooldown, authorization, and CB remain the same;
the fallback does not grant a free authorization or bypass the council.

v1.2 native council UI integration
----------------------------------
The fifth war selector is now merged into Dragonlord Regime's native
gui/custom_gui/dragonlord_council_agenda.gui rather than displayed as a
standalone overlay. This fixes the selector failing to appear while retaining
the existing target-pool, vote, authorization, fallback decision, and CB logic.

The native four description rows are reduced from 54px to 44px and the war
column spacing from 8px to 4px so all five war types fit in the existing
590px column without changing the rest of the council layout.
