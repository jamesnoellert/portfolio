# Fortress

My version of the Fortress defend level from Austin's FFA game ([austinrhermann/ffa-prototype](https://github.com/austinrhermann/ffa-prototype)), copied from its `main` branch on 2026-10-13 and changed since. Served at jamesnoellert.com/game.

## How it plays

The tower holds three defenders against waves of 20 Midas soldiers (8 on the field at once by default).

- **The Master**: Master rifle, laser pistol, 4 grenades, double health (200). Plays alone if nobody else joins.
- **The Apprentice**: laser pistol only. Works the computer in the tower room.
- **The Computer**: always an NPC. Fires the cannon on the wall over the gate by itself at the closest attacker it can aim at: a grenade-sized blast, then 10 s to recharge. It only faces out over the hills and can't tilt down far enough to reach the foot of the wall.

Attackers batter the gate (two doors at the courtyard end of the passage, swinging inward). Once it's open they come in and hunt the defenders anywhere in the fort. A defender who falls sits out the rest of the wave and comes back when it's cleared; if every defender is down at once, the fort falls.

Players: alone you're the Master. With a friend, the host picks Master or Apprentice and the friend gets the other. Everyone after the second joins the attackers as a Midas soldier (carbine and pistol). A dead attacker can press **E** to take over the NPC soldier closest to the gate, or waits for the next wave.

**The computer** (tower room, press **E** next to it): a map of the area with every attacker on it, and **Space** opens or closes the gate. The gate only breaks once: after that it stays open for good.

Other: white health boxes in the courtyard, on the wall walk, in the north building and in the tower room (attackers can't use them; they restock after each wave). Attackers move at 70% speed, carry Midas carbines and don't throw grenades. No spare guns lie around and nobody drops guns.

## The set

The level comes from James's render set export, turned into two files by `tools/build_fortress.py` (run it in Blender; the command is at the top of the script):

- `models/Fortress_v5.glb` is what you see: characters, render helpers and the render cannon removed, heavy plants simplified, objects merged by material, textures shrunk to JPEG, geometry Draco-compressed (63 MB down to about 6 MB).
- `models/Fortress_v5_col.glb` is what everything collides with, shoots at and walks on: simplified terrain and fort walls, the tower and its stairs exact, props as boxes, no plants, plus the closed gate as a box named `Front_Gate`.

When the level loads, the host builds a fine walking map of every floor inside the fort from the collision file; attackers plan their paths on it.
