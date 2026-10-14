# Fortress

My version of the Fortress defend level from Austin's FFA game ([austinrhermann/ffa-prototype](https://github.com/austinrhermann/ffa-prototype)), copied from its `main` branch on 2026-10-13 and changed since. Served at jamesnoellert.com/game.

## How it plays

The tower holds three defenders against waves of 20 Midas soldiers (8 on the field at once by default).

- **The Master**: Master rifle, laser pistol, 4 grenades, double health (200). Plays alone if nobody else joins.
- **The Apprentice**: laser pistol only. Works the computer in the tower room.
- **The Computer**: always an NPC. Fires the roof cannon by itself at the closest attacker it can aim at: a grenade-sized blast, then 10 s to recharge. It can't tilt down far enough to reach the foot of the fort.

Players: alone you're the Master. With a friend, the host picks Master or Apprentice and the friend gets the other. Everyone after the second joins the attackers as a Midas soldier (carbine and pistol). A dead attacker can press **E** to take over the NPC soldier closest to the gate, or waits for the next wave.

**The computer** (tower room, press **E** next to it): a map of the area with every attacker on it, and **Space** opens or closes the gate. The gate only breaks once: after that it stays down.

Other: white health boxes in the courtyard, on the wall walk, in the north building and in the tower room (attackers can't use them; they restock after each wave). Attackers move at 70% speed, carry Midas carbines and don't throw grenades. No spare guns lie around and nobody drops guns.
