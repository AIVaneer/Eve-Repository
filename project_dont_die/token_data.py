# PCVR Coin — Live Token Data
# Run this to see all token info

TOKEN = {
    "name": "PCVR Coin",
    "symbol": "PCVR",
    "chain": "Cronos",
    "contract": "0x05c870C5C6E7AF4298976886471c69Fc722107e4",
    "pair": "0x5a84Add7Ad701409F16C2c5B1CE213b024BCE68a",
    "dex": "https://dexscreener.com/cronos/0x5a84Add7Ad701409F16C2c5B1CE213b024BCE68a",
    "explorer": "https://cronoscan.com/token/0x05c870C5C6E7AF4298976886471c69Fc722107e4",
    "web": "https://pcvr.lol",
    "discord": "https://discord.gg/E7bW3Zh4x",
    "twitter": "https://x.com/pcvr2024?s=21",
    "email": "contact@pcvr.lol",
    "repos": {
        "main": "https://github.com/AIVaneer/Eve-Repository",
        "skyburner": "https://github.com/AIVaneer/SkyBurner-Ultimate-pythonista-game-",
        "vr": "https://github.com/AIVaneer/PCVR-game-shell-"
    }
}

def show():
    t = TOKEN
    print(f"\n{'='*50}")
    print(f"  {t['name']} ({t['symbol']}) on {t['chain']}")
    print(f"{'='*50}")
    print(f"  Contract:  {t['contract']}")
    print(f"  Pair:      {t['pair']}")
    print(f"  DexScreen: {t['dex']}")
    print(f"  Explorer:  {t['explorer']}")
    print(f"  Website:   {t['web']}")
    print(f"  Discord:   {t['discord']}")
    print(f"  Twitter:   {t['twitter']}")
    print(f"  Email:     {t['email']}")
    print(f"  GitHub:    {t['repos']['main']}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    show()
