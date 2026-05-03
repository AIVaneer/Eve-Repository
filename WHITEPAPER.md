# PCVR Studios — White Paper

**Version 2.0 · March 2026**

---

Portable Computer Virtual Reality (PCVR) is a VR-integrated, resource-light gaming platform that merges the nostalgia of classic 2D platformers with immersive virtual reality. Designed for devices like the Oculus Quest 3, PCVR aims to deliver accessible gameplay that minimizes hardware strain while offering a unique incentive model: players earn PCVR Coin rewards as they complete in-game tasks. PCVR Coin is the studio's native cryptocurrency, live and tradeable on the Cronos blockchain.

By incorporating a communal "mining pool" mechanism, multiple players contributing simultaneously can enhance their collective earning potential, fostering a community-driven environment. This integration of crypto micro-rewards into VR gameplay offers a tangible value proposition while preserving the fundamental fun and simplicity of classic 2D gaming.

Since the original white paper, PCVR Studios has shipped multiple playable titles across iOS and VR, launched a custom in-house game engine (the Atlas Nexus Engine), and graduated the PCVR token from concept to a live, tradeable asset.




PCVR envisions a future where VR gaming is not just about immersion and entertainment, but also about cultivating a community that benefits collectively. Instead of focusing on realistic graphics or complex mechanics, PCVR emphasizes minimalism: simple shapes, 2D sprites, and flat colors rendered in a 3D VR setting. This approach ensures broader device compatibility, lower power consumption, and a more inclusive gaming experience.




1. Simplicity and Accessibility:
Provide a low-barrier entry into VR gaming, enabling players of all skill levels to enjoy a familiar style of gameplay.

2. Value-Added Gaming:
Introduce PCVR Coin micro-rewards to give casual gaming sessions a tangible financial aspect.

3. Community-Oriented Ecosystem:
Encourage multiplayer sessions where player activity aggregates into a shared "mining pool," rewarding cooperation.

4. Educational Bridge to Cryptocurrency:
Offer a gentle introduction to crypto and blockchain concepts through practical, hands-on rewards using PCVR Coin.

5. Cross-Platform Game Development:
Demonstrate the studio's capability by shipping games on iOS (via Pythonista 3) and VR (Oculus Quest 3), powered by custom in-house engines.




2D Platformer in a VR Space:
PCVR takes the essence of classic side-scrollers—jumping, collecting coins, avoiding simple obstacles—and projects it onto a virtual plane that players view through their VR headset. Although the character and level elements are inherently 2D, the VR perspective provides depth and presence. The player feels as though they're standing in front of a giant, interactive arcade machine.

Level Design:
• Basic Layout: Short, looping levels with platforms, moving obstacles, and collectible coins.
• Incremental Challenges: Subsequent levels can increase difficulty slightly, ensuring longevity and player retention without overwhelming complexity.
• Visual Style: Geometric shapes, flat-colored sprites, and minimal particle effects keep rendering costs low.

Control and Interaction:
• VR Input: Players can use VR controllers or hand tracking (if supported) to navigate UI menus, select levels, or manipulate certain in-game elements.
• Movement Input: Traditional character movement can be mapped to a VR controller's thumbstick, ensuring intuitive and familiar controls.
• Head Tracking: Players can lean forward or look around the virtual "screen" to gain better vantage points, adding a subtle layer of immersion.




Games Library:
PCVR Studios now has three released titles spanning iOS and VR. All games are open-source and available on GitHub.

SkyBurner Ultimate (Flagship Title):
Platform: Pythonista 3 / iOS (iPhone & iPad)
Engine: Atlas Nexus Engine v1.0 (custom, in-house)
Language: 100% Python — zero external assets
Repository: https://github.com/AIVaneer/SkyBurner-Ultimate-pythonista-game-

SkyBurner Ultimate is a high-octane, vertical-scrolling arcade space-shooter built entirely in Python. Developed by PCVR Studios and powered by the custom Atlas Nexus Engine, the game runs on Pythonista 3 for iPhone and iPad, delivering stunning vector-art visuals at full frame-rate on any modern iOS device. Three clean Python files (atlas_nexus.py, entities.py, skyburner.py) power the entire experience — every sprite, explosion, and star is drawn with Python's built-in modules.

• 4 Weapon Tiers: Single laser → Dual cannon → Triple spread → Homing missiles.
• 3 Enemy Types: Fighter, Cruiser, and Boss (appears every 5th wave).
• Multi-Phase Bosses: Entry → Attack 1 → Attack 2 → Rage mode.
• Combo System: Chain kills to build streaks and boost multiplier up to ×8.
• 5 Power-Ups: Weapon upgrade, shield boost, health pack, extra bomb, speed burst.
• 115-Star Parallax Starfield: Gorgeous scrolling space backdrop for full immersion.
• Full HUD: Score, high-score, health bar, shield bar, lives, bomb count, wave indicator, boss health bar.
• Touch Controls: Drag to move, tap to bomb — auto-fire lets you focus on dodging.

Downloads (via Discord):
• Game Download: https://discord.com/channels/1316937801995911198/1484003872178573495/1484552464639332605
• Music Download: https://discord.com/channels/1316937801995911198/1484003872178573495/1484595490828845229

Warp Protocol:
Platform: Pythonista 3 / iOS (iPhone & iPad)
Engine: Custom Python engine
Language: 100% Python
Repository: https://github.com/AIVaneer/Eve-Repository

Warp Protocol is a fast-paced arcade shooter with a cinematic intro sequence, dynamic starfield, enemy archetypes (standard, seeker, bomber), power-ups, bull-mode triple fire, and progressive difficulty scaling. Like SkyBurner Ultimate, it runs entirely within Pythonista 3 with zero external dependencies.

Downloads (via Discord):
• Game Download: https://discord.com/channels/1316937801995911198/1484003872178573495/1484175284419690687
• Music Download: https://discord.com/channels/1316937801995911198/1484003872178573495/1484175284419690687

PCVR Game Shell:
Platform: Oculus Quest 3
Engine: Unity 3D + Oculus XR Integration
License: MIT License (open-source)
Repository: https://github.com/AIVaneer/PCVR-game-shell-

The PCVR Game Shell is the foundational 2D VR game framework for the Oculus Quest 3. It provides the core virtual environment and character positioning that will underpin the full PCVR platform. Open-sourced under the MIT License to encourage community-driven innovation.

• Core Environment: A foundational virtual space designed for a seamless 2D VR experience.
• Character Positioning: Proper spatial placement and orientation for characters within the game.




Atlas Nexus Engine:
The Atlas Nexus Engine is PCVR Studios' custom, in-house game engine built entirely in Python. It powers SkyBurner Ultimate and serves as the foundation for future Pythonista-based titles. Current version: 1.0.0.

• Entity-Component System: Modular architecture for managing game objects, transforms, health, weapons, and shields.
• AABB Collision Detection: Efficient axis-aligned bounding box collision for all entities.
• Wave Management: Dynamic wave spawning with configurable enemy compositions and boss encounters.
• Score & Multiplier Tracking: Kill-streak combo system with multiplier decay and high-score persistence.
• Zero Dependencies: Runs entirely on Pythonista 3's built-in scene and ui modules — no external packages.




Unity Engine & Oculus Integration:
• Unity 3D: Provides a robust platform for rapid development, cross-platform deployment, and a blend of 2D and 3D assets.
• Oculus XR Integration: Manages headset tracking, controller input, and device optimization for Quest 3.
• 2D Packages: Unity's 2D toolset handles sprites, physics, and animations efficiently, ensuring a smooth experience.

Pythonista 3 / iOS (Mobile Games):
• 100% Python: All mobile titles are built with zero external dependencies using Pythonista 3's scene and ui modules.
• Vector-Art Rendering: Every visual element — sprites, explosions, starfields — is drawn programmatically using Python's built-in ui.Path system.
• Three-File Architecture: Games follow a clean structure (engine → entities → main scene), keeping codebases maintainable and extensible.

Networking & Multiplayer Infrastructure:
• Client-Server Model: Players connect to remote servers hosting sessions. A lightweight protocol ensures minimal latency and bandwidth usage.
• Instance Management: Multiple instances (game rooms) run concurrently, each supporting a group of players. When multiple players share an instance, their in-game activity contributes to a single mining pool calculation.
• Scalability: Server instances spin up or down based on demand. Load balancing distributes players evenly, ensuring stable performance as user numbers grow.

Data Security & User Accounts:
• Account Creation: Users set up accounts to track their in-game progress and PCVR Coin earnings. OAuth or single-sign-on (SSO) integration can simplify onboarding.
• Data Storage: Gameplay data, transaction logs, and achievement records are stored in secure, encrypted databases. Regular backups and redundancy minimize data loss risks.
• Cheat & Fraud Prevention: Basic heuristics (time-to-complete levels, abnormal movement patterns) and server-side verifications flag potential misuse. Periodic audits ensure fairness in reward distribution.




PCVR Coin — Native Token & In-Game Rewards:

Token Details:
• Token Name: PCVR Coin
• Blockchain: Cronos
• Contract Address: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
• DexScreener: https://dexscreener.com/cronos/0x5a84Add7Ad701409F16C2c5B1CE213b024BCE68a
• Status: Live & Tradeable

PCVR Coin is the native cryptocurrency of the PCVR Studios ecosystem. The token has graduated from concept to a live, tradeable asset on the Cronos blockchain. Players earn PCVR Coin by achieving in-game milestones such as collecting a certain number of coins, completing a level, or reaching a weekly challenge goal. While individual payouts are small, they accumulate over time, offering a new layer of engagement.

Reward Mechanics:
• Individual Payouts: A single-player session yields PCVR Coin increments per achievement.
• Pooling Effect: In multiplayer sessions, the reward pool grows proportionally with the number of active players and their combined accomplishments. Rewards are then distributed based on each player's contribution, encouraging teamwork.

Back-End Integration:
• Cronos Network: PCVR Coin transactions are processed on the Cronos blockchain, offering fast confirmation times and low fees.
• Wallet Linking: Players connect a Cronos-compatible wallet during account setup to receive PCVR Coin payouts.
• Scheduled Settlements: Instead of paying out PCVR Coin instantly, the platform may accumulate player earnings and trigger payouts after a session or once a certain threshold is reached, reducing transaction overhead.
• Transparent Tracking: Players can view their PCVR Coin balance, transaction history, and share of pool rewards through an in-game dashboard or companion app. Live token price and charts are available on DexScreener.




Initial Funding Model:
During early phases, the PCVR Coin reward pool may be subsidized by project reserves or seed funding. As player numbers grow, sustainable models, such as a percentage of optional cosmetic item sales or sponsored events, can replenish the reward pool.

Long-Term Viability:
• In-Game Marketplace: Offer optional cosmetic skins, level packs, or soundtracks for purchase. A portion of these revenues can feed back into the PCVR Coin pool.
• Partnerships and Advertising: Non-intrusive product placements or partnerships with cryptocurrency exchanges could provide secondary revenue streams.
• Token Trading: With PCVR Coin now live on Cronos and listed on decentralized exchanges, players can trade their earned tokens freely, providing real liquidity and value.
• Economy Balancing: Dynamic adjustments to reward rates, achievement difficulty, or coin distributions ensure that the ecosystem remains fair, preventing inflation or exploitation.

Regulatory & Compliance Considerations:
• Financial Regulations: If required, obtain appropriate licensing for handling cryptocurrency and ensure compliance with local regulations.
• User Privacy: Adhere to data protection laws (e.g., GDPR) and ensure transparent communication about data usage and storage.




Initial Setup:
• Download & Install: Players download PCVR from the Oculus Store.
• Account Creation & Wallet Linking: On first launch, a guided tutorial helps users create an account and connect a Cronos-compatible wallet for PCVR Coin payouts.
• Tutorial Level: A simple introductory level teaches basic movement, coin collection, and explains how PCVR Coin rewards are earned.

Ongoing Player Engagement:
• Progression System: Players earn cosmetic badges or titles for accumulating certain amounts of PCVR Coin or completing weekly challenges.
• Seasonal Events & Leaderboards: Limited-time events (e.g., a holiday-themed level) and global leaderboards encourage repeat visits and community competition.
• Social Tools: Friend lists, party systems, and voice chat (if desired) help players coordinate, form groups, and earn PCVR Coin more effectively together.




Roadmap Milestones

1. Concept Development (Completed)
• Define the project vision and core features (e.g., VR, crypto rewards, PCVR Coin).
• Progress: 100%

2. Community & Ecosystem Building (Ongoing)
• Launch website (PCVR.lol).
• Promote idea and attract interest (e.g., engaging mining companies and investors).
• Discord and Twitter/X communities active and growing.
• Progress: 75%

3. Prototype Development (In Progress)
• Basic VR setup in Unity (completed).
• Create a demo with 2D gameplay in VR.
• SkyBurner Ultimate and Warp Protocol shipped on iOS via Pythonista 3.
• Atlas Nexus Engine v1.0 released.
• Progress: 60%

4. Token Launch (Completed)
• PCVR Coin created and deployed on Cronos blockchain.
• Token graduated and live on decentralized exchanges.
• Tokenomics and distribution plan completed.
• Progress: 100%

5. Key Features (In Progress)
• Build full gameplay mechanics with PCVR Coin integration.
• Add multiplayer mining pool functionality.
• Optimize VR performance for the Oculus Quest.
• Integrate in-game PCVR Coin reward payouts.
• Current reward model: Direct developer-to-player payouts via wallet QR scan on the Cronos blockchain — no third parties.
• Target reward model: Fully integrated in-app system where players earn and receive PCVR Coin automatically within a single app experience.

6. Launch & Scaling (Not Started)
• Release beta version to early adopters.
• Scale community and partnerships.
• Finalize full public release.
• Progress: 0%

Estimated overall the project is approximately 50% complete with the overall roadmap. Foundational work is done (vision, community-building, basic VR setup), two fully playable iOS titles have been shipped (SkyBurner Ultimate and Warp Protocol), the Atlas Nexus Engine is live, and the PCVR Coin token has graduated to a tradeable asset on Cronos. The next focus areas are building the key features: in-game PCVR Coin rewards, multiplayer mining pools, and VR performance optimization.




Portable Computer Virtual Reality (PCVR) represents a novel intersection of VR technology, retro-style gaming, and cryptocurrency micro-rewards. By embracing simplicity, fostering community-driven gameplay sessions, and providing tangible incentives through PCVR Coin, PCVR aims to redefine how players perceive value in virtual environments. This low-barrier approach appeals to casual gamers, crypto enthusiasts, and curious newcomers, positioning PCVR as a pioneering platform in a rapidly evolving digital entertainment landscape.

With the release of SkyBurner Ultimate, Warp Protocol, and the open-source PCVR Game Shell, the studio has moved beyond concept into execution — shipping real games, building a custom engine, and growing an active community. The PCVR Coin token is now live and tradeable on the Cronos blockchain. The foundation is built. The next phase brings it all together.

This document will continue to evolve as new features are implemented, market conditions change, and community feedback shapes the future of PCVR.




Links & Resources:

Website: https://pcvr.lol
Discord: https://discord.gg/E7bW3Zh4x
Twitter / X: https://x.com/pcvr2024?s=21
Contact: contact@pcvr.lol
PCVR Coin (DexScreener): https://dexscreener.com/cronos/0x5a84Add7Ad701409F16C2c5B1CE213b024BCE68a
PCVR Coin Contract (Cronos): 0x05c870C5C6E7AF4298976886471c69Fc722107e4

GitHub Repositories:
• Eve-Repository (PCVR Games Hub): https://github.com/AIVaneer/Eve-Repository
• SkyBurner Ultimate: https://github.com/AIVaneer/SkyBurner-Ultimate-pythonista-game-
• PCVR Game Shell: https://github.com/AIVaneer/PCVR-game-shell-

Game Downloads (via Discord):
• SkyBurner Ultimate — Game: https://discord.com/channels/1316937801995911198/1484003872178573495/1484552464639332605
• SkyBurner Ultimate — Music: https://discord.com/channels/1316937801995911198/1484003872178573495/1484595490828845229
• Warp Protocol — Game & Music: https://discord.com/channels/1316937801995911198/1484003872178573495/1484175284419690687


© PCVR STUDIOS 2026 · Atlas Nexus Engine v1.0 · PCVR Coin on Cronos

---

# 🆕 Version 2.1 Additions — New Since 2.0

**Version 2.1 · May 2026**

> This section documents what PCVR Studios has built since White Paper 2.0 was published in March 2026. All previous sections remain intact and authoritative — this is an evolution, not a rewrite.

---

## 1. PCVR EdTech — Code Raiders (NEW PRODUCT LINE)

PCVR Studios has expanded beyond pure VR gaming into **gamified education**. **Code Raiders** is a story-driven Python-learning game that teaches real coding through broken-code repair missions.

- **Repository:** https://github.com/AIVaneer/PCVR-EdTech
- **Live URL:** https://aivaneer.github.io/PCVR-EdTech/
- **Hosting:** GitHub Pages (zero-cost, instant deploy)
- **Tech:** Self-contained HTML/CSS/JS — no backend, no dependencies
- **Status:** Levels 1–7 shipped, Portal V3 live

### Campaign Structure
Release model: **three levels per Monday batch**.

| World | Theme | Levels | Status |
|---|---|---|---|
| 1 | Matrix Green World | 1, 2, 3 | ✅ Active |
| 2 | Fire Cave World | 4, 5, 6 | 🔜 Planned/Building |
| 3 | Ice Castle World | 7, 8, 9 | 🔜 Planned |
| 4 | Space Portal World | 10, 11, 12 | 🔜 Planned |

### Why This Matters
- Free user acquisition funnel into the PCVR ecosystem
- Onboards new players to the brand before they touch the token
- Educational bridge — students learn Python while exposed to PCVR Coin concepts

---

## 2. Portal V3 — Console-Style Launcher

The Code Raiders Portal Hub has evolved from a simple navigation page into a full **console interface + game launcher**.

The Portal functions as the central operating system for the PCVR ecosystem, unifying learning, gameplay, and future token utility into a single user interface.

### Core Sections
- **Continue Journey** — Smart progression routing
- **PCVR Radio** — Built-in streaming audio system
- **PCVR Arcade** — Embedded game launcher
- **Learning Worlds** — Code Raiders campaign access
- **Boss + Cinematics** — Story moments
- **Systems + Tools** — Player utilities
- **Atlas Core** — Reserved gateway (private system, high-level reference only)

### Smart Continue System
Tracks player progression locally using browser storage:
- XP tracking
- Last-level memory
- Per-level completion flags
- Dynamic progress bar
- Auto-routing to next mission, with fallback to last saved state

---

## 3. PCVR Arcade System

Level 10+ experiences are full games — not coding lessons. They launch inside an embedded **iframe modal arcade**, never as page redirects.

This design ensures all gameplay remains inside the PCVR environment, enabling future integration of rewards, progression systems, and token utility without external dependency.

### Initial Arcade Lineup
- SkyBurner (HTML port for browser play)
- Levels 11–16 (boss battles, cinematic challenges)

### Design Principles
- iframe modal launcher with close button
- Mobile-friendly
- App-launcher feel
- Games stay sandboxed inside the portal — players never leave the ecosystem

---

## 4. PCVR Radio System

The portal now ships with a built-in **SomaFM streaming radio**, turning the learning experience into an ambient session.

### Features
- Play / Pause
- Next station / Shuffle
- Volume control with persistent state
- Animated equalizer
- Station memory across sessions

This adds session length, immersion, and a "command-center" feel to every visit.

---

## 5. Studio Operations Repo — AIVaneer-PCVR-Studios

A new central HQ repository consolidates studio assets:

- **Repo:** https://github.com/AIVaneer/AIVaneer-PCVR-Studios
- **Eve DeFi Toolkit v10** — 20+ Python modules for market data, risk analytics, whale tracking, automation, multichain support, and smart integrations
- **Project Don't Die** — Token economy survival tools (treasury, burn schedules, staking pools)
- **SkyBurner Ultimate** — Full source under `skyburner/` with the Atlas Nexus Engine
- **Web Dashboard** — Self-contained HTML dashboard, GitHub Pages compatible
- **CI/CD** — flake8 + pytest workflows on Python 3.10–3.12

---

## 6. Project Don't Die — Token Economy Survival Plan

Published as a standalone document alongside the white paper:
**https://github.com/AIVaneer/Eve-Repository/blob/main/PROJECT_DONT_DIE.md**

Key additions to PCVR Coin economic policy since 2.0:

### The Loop
**Earn → Hold → Spend → Buy → Earn**

### 3-Month Smart Contract Lock (Planned)
- 90-day immutable lock
- Holders earn share of the **Earnings Vault** (real revenue, not minted tokens)
- 7-day gradual unlock to prevent cliff dumps
- Re-lock option for compounded participation

### Anti-Debasement Controls
- Daily emission caps
- Per-player reward limits + cooldowns
- 10–35% burn on every store purchase
- Earnings Vault funded only by real revenue
- Health Ratio monitoring (spent / emitted)
- Server-side validation + anomaly detection

### Access Tiers (Planned)
| Tier | Stake | Benefits |
|---|---|---|
| Bronze | 500 PCVR | Patch notes, Discord badge |
| Silver | 2,000 PCVR | Beta access, dev Q&A |
| Gold | 5,000 PCVR | Feature voting, game credits |
| Diamond | 15,000 PCVR | Direct dev access, custom title |
| Elite | 50,000 PCVR | Revenue share, co-design (100 slots) |

---

## 7. Internal Systems (Reference Only)

PCVR Studios operates additional internal infrastructure that is **intentionally not detailed in this public document**:

- **Atlas Infinity Core** — Private orchestration layer
- **PCVR Loader** — Internal Tiered loader/automation system
- **Backend automation pipelines** — Reserved for studio operations

These systems support studio velocity but are kept private for security, IP, and competitive reasons. They are referenced here for completeness only; implementation details are not published.

---

## 8. Updated Roadmap Snapshot

| Milestone | Status |
|---|---|
| Concept Development | ✅ 100% |
| Token Launch (PCVR Coin live on Cronos) | ✅ 100% |
| SkyBurner Ultimate (iOS) | ✅ Shipped |
| Warp Protocol (iOS) | ✅ Shipped |
| PCVR Game Shell (Quest 3) | ✅ Open-sourced |
| Atlas Nexus Engine v1.0 | ✅ Released |
| **PCVR EdTech / Code Raiders** | ✅ **Live (NEW)** |
| **Portal V3 Console System** | ✅ **Live (NEW)** |
| **Studio HQ repo** | ✅ **Live (NEW)** |
| **Project Don't Die framework** | ✅ **Documented (NEW)** |
| Community & Ecosystem | 🔄 Ongoing (~80%) |
| Full Mobile Multiplayer | 🔄 In Progress |
| Token Utility Phase | 🔜 Planned |
| Beta Launch | 🔜 Planned |
| Public Release | 🔜 Planned |

**Overall:** Studio has graduated from "concept + 2 games" to "live ecosystem with education arm, console portal, and token economy framework."

---

## 9. New Resources & Links

| Resource | URL |
|---|---|
| Studio HQ Repo | https://github.com/AIVaneer/AIVaneer-PCVR-Studios |
| Code Raiders (Live) | https://aivaneer.github.io/PCVR-EdTech/ |
| Code Raiders Repo | https://github.com/AIVaneer/PCVR-EdTech |
| Portal Hub (Live) | https://aivaneer.github.io/PCVR-EdTech/code-raiders/portal.html |
| Project Don't Die | https://github.com/AIVaneer/Eve-Repository/blob/main/PROJECT_DONT_DIE.md |

---

## 10. Closing Note for 2.1

PCVR Studios in March 2026 was a token + games studio. PCVR Studios in May 2026 is a **token + games + education + console-grade portal experience**. The mission has not changed — *"Always for good, never for bad"* — but the surface area has expanded dramatically.

This transition marks the beginning of PCVR as a platform, not just a product.

The next white paper milestone (3.0) will be reserved for major architectural shifts (full app shell, automated rewards, in-app token utility). Until then, 2.1 is the source of truth for everything new.

---

*White Paper 2.1 appended: 2026-05-03*
*Original 2.0 content above remains unchanged and authoritative.*
