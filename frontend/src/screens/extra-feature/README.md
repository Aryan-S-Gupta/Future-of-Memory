# 🧠 Peer-to-Peer Multiplayer Mode (Legacy Feature)

## Overview
This folder contains the **original peer-to-peer (P2P) multiplayer implementation** of the game.  
It was the **first version** of the multiplayer system developed before the current **Host vs Player** model was introduced.

In the peer-to-peer mode, all players directly connected and synchronized game state without relying on a central host controller.  
Although this design was later replaced for improved stability, scalability, and easier synchronization, it is preserved here as a **backup feature** in case of critical errors or fallback needs.

---

## Key Features
- **Direct Player Synchronization:**  
  Each client communicated directly with others, maintaining shared state consistency.

- **Distributed Control:**  
  No single host controlled the session — decisions and progress were collectively managed.

- **Low-Latency Interaction:**  
  Designed to minimize delay for small multiplayer groups.

- **Self-Contained Module:**  
  Can operate independently from the host-player system for testing or emergency fallback.


## Why It Was Replaced
While functional, during user testing it was observed that host vs player mode would enhance
colaboration 
---

## 🛠️ Usage
This module is **not part of the active build pipeline**.  
To enable it manually (for testing or fallback):

> ⚠️ **Note:**  
> This feature is **deprecated** and may not receive full compatibility support in future updates.

---

## 📁 Folder Contents
- `PeerGame.jsx` — main gameplay screen for P2P mode  
- `BackgroundScreenMulti.jsx` — handles room creation and connection between players  
- `README.md` — (this file) overview and documentation


## 💡 Notes
This version remains available for:
- Troubleshooting major multiplayer errors
- Reference for distributed synchronization logic
- Historical development record

If errors occur in the host-based system, this mode can serve as a **temporary fallback** to maintain gameplay continuity.
