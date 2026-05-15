# ============================================================
# PCVR Studios — game_builder.py
# Atlas Nexus Game Builder  v1.0
# Copyright © PCVR Studios. All rights reserved.
# Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4
#
# Fluent builder API for creating Atlas Nexus Engine arcade
# games that run natively in Pythonista 3 on iPhone and iPad.
#
# "Build fast. Fly faster."
# ============================================================
"""
Atlas Nexus Game Builder — zero-dependency Pythonista 3 game scaffolder.

Quick Start::

    game = (GameBuilder('Galactic Fury')
            .screen_size(380, 680)
            .starfield(count=115, layers=3)
            .player(health=100, speed=220, lives=3, bombs=3)
            .enemy('fighter', health=30,  speed=80,  score=100)
            .enemy('cruiser', health=80,  speed=45,  score=300)
            .boss_every(5, health=500, score=2000)
            .power_up('weapon_upgrade', chance=0.20)
            .power_up('shield',         chance=0.15)
            .power_up('health',         chance=0.12)
            .hud(score=True, wave=True, health=True)
            .wave_difficulty(base_enemies=5, scale_per_wave=2)
            .build())

    game.run()

Presets (ready to run)::

    preset_skyburner().build().run()
    preset_blitz().build().run()
    preset_survival().build().run()

Compatible with Pythonista 3 on iOS (iPhone and iPad).
Falls back to a printed config summary in non-Pythonista environments.
Zero external dependencies.
"""

import math
import random
import time

# ── Pythonista imports (graceful fallback for desktop / CI) ──────────────────

try:
    import ui
    _UI_AVAILABLE = True
except ImportError:
    _UI_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION OBJECTS
# ─────────────────────────────────────────────────────────────────────────────

class PlayerConfig:
    """Configuration for the player ship."""

    def __init__(self, health=100, speed=200, lives=3, bombs=3,
                 color='#5b8dee', width=30, height=30,
                 weapon_tiers=None):
        self.health       = int(health)
        self.speed        = float(speed)
        self.lives        = int(lives)
        self.bombs        = int(bombs)
        self.color        = color
        self.width        = int(width)
        self.height       = int(height)
        self.weapon_tiers = list(weapon_tiers or
                                 ['single', 'double', 'spread', 'missile'])

    def __repr__(self):
        return (f'PlayerConfig(health={self.health}, speed={self.speed}, '
                f'lives={self.lives})')


class EnemyConfig:
    """Configuration for a single enemy type."""

    def __init__(self, name, health, speed, score,
                 color='#cc3333', width=28, height=28, fire_rate=1.5):
        self.name      = str(name)
        self.health    = int(health)
        self.speed     = float(speed)
        self.score     = int(score)
        self.color     = color
        self.width     = int(width)
        self.height    = int(height)
        self.fire_rate = float(fire_rate)

    def __repr__(self):
        return (f'EnemyConfig(name={self.name!r}, health={self.health}, '
                f'speed={self.speed}, score={self.score})')


class BossConfig:
    """Configuration for boss enemies."""

    def __init__(self, health=500, score=2000, every_n_waves=5,
                 color='#ff6600', width=60, height=50,
                 phases=3, rage_threshold=0.3):
        self.health         = int(health)
        self.score          = int(score)
        self.every_n_waves  = int(every_n_waves)
        self.color          = color
        self.width          = int(width)
        self.height         = int(height)
        self.phases         = int(phases)
        self.rage_threshold = float(rage_threshold)

    def __repr__(self):
        return (f'BossConfig(health={self.health}, score={self.score}, '
                f'every={self.every_n_waves} waves)')


class StarfieldConfig:
    """Configuration for the parallax starfield."""

    def __init__(self, count=115, layers=3,
                 min_speed=20.0, max_speed=80.0, colors=None):
        self.count     = int(count)
        self.layers    = int(layers)
        self.min_speed = float(min_speed)
        self.max_speed = float(max_speed)
        self.colors    = list(colors or ['white', '#aaaaaa', '#666666'])

    def __repr__(self):
        return f'StarfieldConfig(count={self.count}, layers={self.layers})'


class PowerUpConfig:
    """Configuration for a single power-up drop type."""

    VALID_TYPES = frozenset({'weapon_upgrade', 'shield', 'health', 'bomb', 'speed'})

    def __init__(self, power_type, chance=0.15, color='#ffdd00'):
        if power_type not in self.VALID_TYPES:
            raise ValueError(
                f'Unknown power-up type {power_type!r}. '
                f'Valid: {sorted(self.VALID_TYPES)}'
            )
        self.power_type = power_type
        self.chance     = max(0.0, min(1.0, float(chance)))
        self.color      = color

    def __repr__(self):
        return (f'PowerUpConfig(type={self.power_type!r}, '
                f'chance={self.chance:.0%})')


class HUDConfig:
    """Which HUD elements are displayed."""

    def __init__(self, score=True, high_score=True, wave=True,
                 health=True, shield=True, lives=True,
                 bombs=True, multiplier=True, combo=True,
                 boss_health=True):
        self.score       = bool(score)
        self.high_score  = bool(high_score)
        self.wave        = bool(wave)
        self.health      = bool(health)
        self.shield      = bool(shield)
        self.lives       = bool(lives)
        self.bombs       = bool(bombs)
        self.multiplier  = bool(multiplier)
        self.combo       = bool(combo)
        self.boss_health = bool(boss_health)


class WaveDifficultyConfig:
    """Wave-to-wave scaling parameters."""

    def __init__(self, base_enemies=5, scale_per_wave=2,
                 speed_scale=1.05, health_scale=1.08):
        self.base_enemies   = int(base_enemies)
        self.scale_per_wave = int(scale_per_wave)
        self.speed_scale    = float(speed_scale)
        self.health_scale   = float(health_scale)


class GameConfig:
    """Aggregated configuration produced by GameBuilder."""

    def __init__(self, title='PCVR Game'):
        self.title      = str(title)
        self.width      = 380
        self.height     = 680
        self.bg_color   = '#0d0f14'
        self.player     = PlayerConfig()
        self.starfield  = StarfieldConfig()
        self.enemies    = []                     # list[EnemyConfig]
        self.boss       = BossConfig()
        self.power_ups  = []                     # list[PowerUpConfig]
        self.hud        = HUDConfig()
        self.difficulty = WaveDifficultyConfig()
        self.max_waves  = 0                      # 0 = unlimited

    def validate(self):
        """Raise ValueError if the configuration is invalid."""
        errors = []
        if not self.title.strip():
            errors.append('Game title cannot be empty.')
        if self.width < 200 or self.height < 300:
            errors.append(
                f'Screen size {self.width}×{self.height} too small (min 200×300).'
            )
        if not self.enemies:
            errors.append('At least one enemy type must be defined.')
        if self.player.speed <= 0:
            errors.append('Player speed must be positive.')
        if self.player.health <= 0:
            errors.append('Player health must be positive.')
        total_chance = sum(p.chance for p in self.power_ups)
        if total_chance > 1.0:
            errors.append(
                f'Combined power-up drop chance {total_chance:.0%} exceeds 100%.'
            )
        if errors:
            raise ValueError(
                'GameConfig validation failed:\n  ' + '\n  '.join(errors)
            )
        return self


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

class _Star:
    """One star in the parallax starfield."""
    __slots__ = ('x', 'y', 'speed', 'size', 'color')

    def __init__(self, x, y, speed, size, color):
        self.x     = x
        self.y     = y
        self.speed = speed
        self.size  = size
        self.color = color


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def _txt(text, x, y, size=12, color='white', bold=False):
    """Draw a string inside a Pythonista ui draw() context."""
    font_name = ('<system-bold>', size) if bold else ('<system>', size)
    ui.draw_string(str(text), (x, y, 250, size + 6),
                   font=font_name, color=color)


# ─────────────────────────────────────────────────────────────────────────────
# GAME CANVAS  (Pythonista ui.View subclass)
# ─────────────────────────────────────────────────────────────────────────────

if _UI_AVAILABLE:
    class _GameCanvas(ui.View):
        """
        Custom drawing surface.  Holds a reference to the BuiltGame state
        object and redraws the full frame on every set_needs_display() call.
        """

        def __init__(self, game_state, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._gs = game_state

        def draw(self):
            gs  = self._gs
            cfg = gs.config
            w   = cfg.width
            h   = cfg.height

            # Background
            ui.set_color(cfg.bg_color)
            ui.fill_rect(0, 0, w, h)

            # Starfield
            for s in gs.stars:
                ui.set_color(s.color)
                sz = s.size
                ui.fill_rect(s.x - sz * 0.5, s.y - sz * 0.5, sz, sz)

            if gs.game_over:
                _draw_game_over(gs, w, h)
                return

            if gs.between_waves:
                _draw_wave_banner(gs, w, h)

            # Power-up drops
            for d in gs.drops:
                ui.set_color(d['color'])
                ui.fill_rect(d['x'] - 7, d['y'] - 7, 14, 14)

            # Enemy bullets
            ui.set_color('#ff5555')
            for b in gs.e_bullets:
                ui.fill_rect(b['x'] - 2, b['y'] - 5, 4, 10)

            # Enemies
            for e in gs.enemies:
                ui.set_color(e['color'])
                ew, eh = e['w'], e['h']
                ui.fill_rect(e['x'] - ew * 0.5, e['y'] - eh * 0.5, ew, eh)
                _draw_hp_bar(e['x'], e['y'] - eh * 0.5 - 7,
                             ew, e['hp'], e['max_hp'])

            # Boss
            if gs.boss:
                bss  = gs.boss
                bw, bh = bss['w'], bss['h']
                color = '#ff2200' if bss['rage'] else bss['color']
                ui.set_color(color)
                ui.fill_rect(bss['x'] - bw * 0.5,
                             bss['y'] - bh * 0.5, bw, bh)
                if cfg.hud.boss_health:
                    ratio = bss['hp'] / max(bss['max_hp'], 1)
                    bx = w * 0.1
                    ui.set_color('#222')
                    ui.fill_rect(bx, h - 22, w * 0.8, 9)
                    bar_c = '#ff6600' if bss['rage'] else '#5b8dee'
                    ui.set_color(bar_c)
                    ui.fill_rect(bx, h - 22, w * 0.8 * ratio, 9)

            # Player bullets
            for b in gs.bullets:
                if b.get('homing'):
                    ui.set_color('#ffaa00')
                    ui.fill_rect(b['x'] - 3, b['y'] - 9, 6, 14)
                else:
                    ui.set_color('#5b8dee')
                    ui.fill_rect(b['x'] - 2, b['y'] - 9, 4, 14)

            # Player ship
            pc = cfg.player
            px, py = gs.player_x, gs.player_y
            ui.set_color('#2a3347')
            ui.fill_rect(px - 16, py - 9, 32, 18)           # wings
            ui.set_color(pc.color)
            ui.fill_rect(px - 8, py - pc.height * 0.5,
                         16, pc.height)                       # body
            if gs.player_shield > 0:
                ui.set_color('rgba(91,141,238,0.25)')
                ui.fill_rect(px - 22, py - 24, 44, 44)       # shield glow

            # HUD
            _draw_hud(gs, cfg, w)

else:
    # Stub so the module still imports without Pythonista
    _GameCanvas = None


# ─────────────────────────────────────────────────────────────────────────────
# DRAW HELPERS (called from _GameCanvas.draw)
# ─────────────────────────────────────────────────────────────────────────────

def _draw_hp_bar(cx, top_y, bar_w, hp, max_hp):
    ratio = hp / max(max_hp, 1)
    ui.set_color('#333333')
    ui.fill_rect(cx - bar_w * 0.5, top_y, bar_w, 4)
    color = ('#3ecf8e' if ratio > 0.5
             else '#ffaa00' if ratio > 0.25
             else '#ff4444')
    ui.set_color(color)
    ui.fill_rect(cx - bar_w * 0.5, top_y, bar_w * ratio, 4)


def _draw_hud(gs, cfg, w):
    hud = cfg.hud
    if hud.score:
        _txt(f'SCORE  {gs.score:,}', 10, 10, 13)
    if hud.high_score:
        _txt(f'BEST  {gs.high_score:,}', w - 130, 10, 13)
    if hud.wave:
        label = f'WAVE {gs.wave}'
        if gs.is_boss_wave:
            label += '  \u26a1 BOSS'
        _txt(label, w * 0.5 - 50, 10, 13)
    if hud.health:
        ratio = gs.player_hp / cfg.player.health
        ui.set_color('#333333')
        ui.fill_rect(10, 38, 90, 7)
        hp_c = ('#3ecf8e' if ratio > 0.5
                else '#ffaa00' if ratio > 0.25
                else '#ff3333')
        ui.set_color(hp_c)
        ui.fill_rect(10, 38, 90 * ratio, 7)
    if hud.shield and gs.player_shield > 0:
        ui.set_color('#1a2233')
        ui.fill_rect(10, 49, 90, 5)
        ui.set_color('#5b8dee')
        ui.fill_rect(10, 49, 90 * gs.player_shield / 100.0, 5)
    if hud.lives:
        _txt(f'\u2665 x{gs.player_lives}', 10, 58, 12)
    if hud.bombs:
        _txt(f'\U0001f4a3 x{gs.player_bombs}', 10, 74, 12)
    if hud.multiplier and gs.multiplier > 1:
        _txt(f'\xd7{gs.multiplier}', w - 44, 36, 20,
             color='#ffdd00', bold=True)
    if hud.combo and gs.combo > 1:
        _txt(f'COMBO {gs.combo}', w - 90, 58, 12, color='#ff9900')


def _draw_wave_banner(gs, w, h):
    ui.set_color('rgba(0,0,0,0.55)')
    ui.fill_rect(0, h * 0.5 - 42, w, 84)
    _txt(f'WAVE {gs.wave} COMPLETE',
         w * 0.5 - 85, h * 0.5 - 22, 20,
         color='#3ecf8e', bold=True)
    secs = max(0.0, gs.between_timer)
    _txt(f'Next wave in {secs:.1f}s',
         w * 0.5 - 70, h * 0.5 + 8, 14, color='white')


def _draw_game_over(gs, w, h):
    ui.set_color('rgba(0,0,0,0.75)')
    ui.fill_rect(0, 0, w, h)
    _txt('GAME OVER', w * 0.5 - 70, h * 0.5 - 48,
         30, color='#ff4444', bold=True)
    _txt(f'SCORE   {gs.score:,}',      w * 0.5 - 60, h * 0.5 + 4,  18)
    _txt(f'BEST    {gs.high_score:,}', w * 0.5 - 60, h * 0.5 + 28, 18)
    _txt(f'WAVES   {gs.wave}',         w * 0.5 - 60, h * 0.5 + 52, 18)
    _txt('TAP TO RESTART',             w * 0.5 - 78, h * 0.5 + 92, 14,
         color='#5b8dee')


# ─────────────────────────────────────────────────────────────────────────────
# BUILT GAME  — runtime state and game loop
# ─────────────────────────────────────────────────────────────────────────────

class BuiltGame:
    """
    A fully configured game ready to run in Pythonista 3.

    Do not construct directly — use ``GameBuilder.build()``.
    Call ``run()`` to present the game view and start the loop.
    """

    def __init__(self, config):
        self.config = config

        # ── Runtime state (public so _GameCanvas can read them) ──
        self.stars          = []
        self.player_x       = config.width  / 2.0
        self.player_y       = config.height - 80.0
        self.player_hp      = float(config.player.health)
        self.player_shield  = 0.0
        self.player_lives   = config.player.lives
        self.player_bombs   = config.player.bombs
        self.weapon_level   = 1
        self.score          = 0
        self.high_score     = 0
        self.multiplier     = 1
        self.combo          = 0
        self.combo_timer    = 0.0
        self.mult_timer     = 0.0
        self.wave           = 1
        self.is_boss_wave   = False
        self.between_waves  = False
        self.between_timer  = 0.0
        self.enemies        = []
        self.bullets        = []
        self.e_bullets      = []
        self.drops          = []
        self.boss           = None
        self.game_over      = False

        # ── Private runtime ──
        self._touch_x      = self.player_x
        self._running      = False
        self._last_time    = 0.0
        self._fire_timer   = 0.0
        self._fire_rate    = 0.30
        self._speed_boost  = 0.0
        self._spawn_timer  = 0.0
        self._spawns       = []
        self._spawned      = 0
        self._canvas       = None
        self._root_view    = None
        self._WAVE_GAP     = 2.0

    # ── Public ───────────────────────────────────────────────────────────────

    def run(self):
        """Present the game in Pythonista 3 (fullscreen)."""
        if not _UI_AVAILABLE:
            print('[GameBuilder] ui module not available — headless summary:')
            self._headless_summary()
            return
        self._init()
        self._root_view.present('fullscreen')

    # ── Initialisation ───────────────────────────────────────────────────────

    def _init(self):
        cfg = self.config
        w, h = cfg.width, cfg.height

        # Root view (receives touch)
        root = ui.View(name=cfg.title,
                       background_color=cfg.bg_color,
                       frame=(0, 0, w, h))
        root.touch_began = self._on_touch_began
        root.touch_moved = self._on_touch_moved
        self._root_view  = root

        # Game canvas
        canvas = _GameCanvas(self, frame=(0, 0, w, h),
                             background_color=cfg.bg_color)
        root.add_subview(canvas)
        self._canvas = canvas

        self._reset_state()
        self._running = True
        ui.delay(self._loop, 1.0 / 60.0)

    def _reset_state(self):
        cfg = self.config
        self.stars         = self._build_stars()
        self.player_x      = cfg.width  / 2.0
        self.player_y      = cfg.height - 80.0
        self.player_hp     = float(cfg.player.health)
        self.player_shield = 0.0
        self.player_lives  = cfg.player.lives
        self.player_bombs  = cfg.player.bombs
        self.weapon_level  = 1
        self.score         = 0
        self.multiplier    = 1
        self.combo         = 0
        self.combo_timer   = 0.0
        self.mult_timer    = 0.0
        self.enemies       = []
        self.bullets       = []
        self.e_bullets     = []
        self.drops         = []
        self.boss          = None
        self.game_over     = False
        self._touch_x      = self.player_x
        self._fire_timer   = 0.0
        self._fire_rate    = 0.30
        self._speed_boost  = 0.0
        self._last_time    = time.time()
        self._start_wave(1)

    # ── Starfield ─────────────────────────────────────────────────────────────

    def _build_stars(self):
        cfg    = self.config.starfield
        w, h   = self.config.width, self.config.height
        stars  = []
        per    = max(1, cfg.count // max(1, cfg.layers))
        colors = cfg.colors or ['white', '#aaaaaa', '#666666']
        for layer in range(cfg.layers):
            color = colors[layer % len(colors)]
            speed = (cfg.min_speed +
                     (cfg.max_speed - cfg.min_speed) *
                     layer / max(1, cfg.layers - 1))
            size  = 1.0 + layer * 0.7
            for _ in range(per):
                stars.append(_Star(
                    x=random.uniform(0, w),
                    y=random.uniform(0, h),
                    speed=speed + random.uniform(-10, 10),
                    size=size,
                    color=color,
                ))
        return stars

    # ── Wave management ───────────────────────────────────────────────────────

    def _start_wave(self, wave_num):
        cfg = self.config
        self.wave         = wave_num
        self.is_boss_wave = (wave_num % cfg.boss.every_n_waves == 0)
        self.between_waves = False
        self._spawn_timer  = 0.0
        self._spawned      = 0
        self.boss          = None
        self._spawns       = self._build_spawns(wave_num)

    def _build_spawns(self, wave):
        cfg    = self.config
        diff   = cfg.difficulty
        spawns = []
        if self.is_boss_wave:
            spawns.append({'type': 'boss', 'delay': 1.0})
            escort = min(4, wave // cfg.boss.every_n_waves)
            for i in range(escort):
                spawns.append({'type': cfg.enemies[0].name,
                               'delay': 2.0 + i * 0.7})
        else:
            total = diff.base_enemies + (wave - 1) * diff.scale_per_wave
            t = 0.0
            for i in range(total):
                etype = cfg.enemies[i % len(cfg.enemies)]
                spawns.append({'type': etype.name, 'delay': t})
                t += 0.55 + (i % 3) * 0.2
        return spawns

    def _get_ecfg(self, name):
        for e in self.config.enemies:
            if e.name == name:
                return e
        return self.config.enemies[0]

    def _spawn(self, entry):
        cfg   = self.config
        diff  = cfg.difficulty
        w     = cfg.width
        scale = self.wave - 1

        if entry['type'] == 'boss':
            bc = cfg.boss
            hp = bc.health * (diff.health_scale ** (scale // bc.every_n_waves))
            self.boss = {
                'x': w / 2.0, 'y': 60.0,
                'vx': 65.0,   'vy': 0.0,
                'hp': hp,     'max_hp': hp,
                'rage': False,
                'color': bc.color,
                'w': bc.width, 'h': bc.height,
                'score': bc.score,
                'fire_t': 0.0,
            }
        else:
            ec  = self._get_ecfg(entry['type'])
            hp  = ec.health * (diff.health_scale ** scale)
            spd = ec.speed  * (diff.speed_scale  ** scale)
            self.enemies.append({
                'type':    ec.name,
                'x':       random.uniform(30, w - 30),
                'y':       -32.0,
                'vx':      random.uniform(-22, 22),
                'vy':      spd,
                'hp':      hp,
                'max_hp':  hp,
                'color':   ec.color,
                'w':       ec.width,
                'h':       ec.height,
                'score':   ec.score,
                'fire_t':  ec.fire_rate * random.uniform(0.5, 1.5),
            })

    # ── Game loop ─────────────────────────────────────────────────────────────

    def _loop(self):
        if not self._running:
            return
        now = time.time()
        dt  = _clamp(now - self._last_time, 0.001, 0.05)
        self._last_time = now

        if not self.game_over:
            self._update(dt)

        self._canvas.set_needs_display()

        if self._running:
            ui.delay(self._loop, 1.0 / 60.0)

    def _update(self, dt):
        cfg = self.config
        w, h = cfg.width, cfg.height

        # Stars
        for s in self.stars:
            s.y += s.speed * dt
            if s.y > h:
                s.y = -2.0
                s.x = random.uniform(0, w)

        # Between-wave countdown
        if self.between_waves:
            self.between_timer -= dt
            if self.between_timer <= 0:
                next_w = self.wave + 1
                if cfg.max_waves > 0 and next_w > cfg.max_waves:
                    self.game_over = True
                else:
                    self._start_wave(next_w)
            return

        # Timers
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0
        if self.mult_timer > 0:
            self.mult_timer -= dt
            if self.mult_timer <= 0:
                self.multiplier = max(1, self.multiplier - 1)
        if self._speed_boost > 0:
            self._speed_boost -= dt

        # Spawn enemies
        self._spawn_timer += dt
        while self._spawned < len(self._spawns):
            entry = self._spawns[self._spawned]
            if self._spawn_timer >= entry.get('delay', 0):
                self._spawn(entry)
                self._spawned += 1
            else:
                break

        # Player auto-fire
        self._fire_timer -= dt
        if self._fire_timer <= 0:
            self._fire_player()
            self._fire_timer = self._fire_rate

        # Move player toward touch x
        spd = cfg.player.speed * (1.5 if self._speed_boost > 0 else 1.0)
        dx  = self._touch_x - self.player_x
        if abs(dx) > 2:
            step = spd * dt
            self.player_x += _clamp(dx, -step, step)
        self.player_x = _clamp(self.player_x, 18, w - 18)

        # Move player bullets
        for b in self.bullets[:]:
            b['y'] -= 420 * dt
            if b['y'] < -12:
                self.bullets.remove(b)

        # Move enemy bullets
        for b in self.e_bullets[:]:
            b['x'] += b['vx'] * dt
            b['y'] += b['vy'] * dt
            if (b['y'] > h + 12 or b['x'] < -12 or b['x'] > w + 12):
                self.e_bullets.remove(b)

        # Move enemies
        for e in self.enemies[:]:
            e['x'] += e['vx'] * dt
            e['y'] += e['vy'] * dt
            if e['x'] < 15 or e['x'] > w - 15:
                e['vx'] *= -1
            if e['y'] > h + 44:
                if e in self.enemies:
                    self.enemies.remove(e)
                continue
            # Enemy fires
            e['fire_t'] -= dt
            if e['fire_t'] <= 0:
                ec = self._get_ecfg(e['type'])
                e['fire_t'] = ec.fire_rate * random.uniform(0.8, 1.3)
                self.e_bullets.append({
                    'x': e['x'], 'y': e['y'] + 16,
                    'vx': random.uniform(-30, 30), 'vy': 165,
                })

        # Move boss
        if self.boss:
            bss = self.boss
            bss['x'] += bss['vx'] * dt
            if bss['x'] < 44 or bss['x'] > w - 44:
                bss['vx'] *= -1
            bss['fire_t'] -= dt
            rate = 0.45 if bss['rage'] else 0.9
            if bss['fire_t'] <= 0:
                bss['fire_t'] = rate
                angles = [70, 90, 110] if bss['rage'] else [90]
                for ang in angles:
                    rad = math.radians(ang)
                    self.e_bullets.append({
                        'x': bss['x'], 'y': bss['y'] + 30,
                        'vx': math.cos(rad) * 130,
                        'vy': math.sin(rad) * 130,
                    })

        # Move drops
        for d in self.drops[:]:
            d['y'] += 62 * dt
            if d['y'] > h + 22:
                self.drops.remove(d)

        # Collisions: player bullets vs enemies
        for b in self.bullets[:]:
            hit = False
            for e in self.enemies[:]:
                if (abs(b['x'] - e['x']) < e['w'] * 0.5 + 4 and
                        abs(b['y'] - e['y']) < e['h'] * 0.5 + 4):
                    e['hp'] -= b.get('dmg', 10)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    hit = True
                    if e['hp'] <= 0:
                        self._kill_enemy(e, score=True)
                    break
            if not hit and self.boss and b in self.bullets:
                bss = self.boss
                if (abs(b['x'] - bss['x']) < bss['w'] * 0.5 + 4 and
                        abs(b['y'] - bss['y']) < bss['h'] * 0.5 + 4):
                    bss['hp'] -= b.get('dmg', 10)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    bc = cfg.boss
                    if not bss['rage'] and bss['hp'] < bss['max_hp'] * bc.rage_threshold:
                        bss['rage'] = True
                    if bss['hp'] <= 0:
                        self.score += int(bss['score'] * self.multiplier)
                        if self.score > self.high_score:
                            self.high_score = self.score
                        self.boss = None
                        self._check_wave_done()

        # Collisions: enemy bullets vs player
        px, py = self.player_x, self.player_y
        pw, ph = cfg.player.width, cfg.player.height
        for b in self.e_bullets[:]:
            if (abs(b['x'] - px) < pw * 0.5 + 4 and
                    abs(b['y'] - py) < ph * 0.5 + 4):
                self.e_bullets.remove(b)
                self._hit_player(10)

        # Enemies ramming player
        for e in self.enemies[:]:
            if (abs(e['x'] - px) < (e['w'] + pw) * 0.5 - 2 and
                    abs(e['y'] - py) < (e['h'] + ph) * 0.5 - 2):
                self.enemies.remove(e)
                self._hit_player(20)

        # Player picks up drops
        for d in self.drops[:]:
            if (abs(d['x'] - px) < pw * 0.5 + 14 and
                    abs(d['y'] - py) < ph * 0.5 + 14):
                self._apply_pickup(d['type'])
                self.drops.remove(d)

        # Wave completion check (non-boss)
        if not self.is_boss_wave:
            self._check_wave_done()

    # ── Combat helpers ────────────────────────────────────────────────────────

    def _kill_enemy(self, e, score):
        if e in self.enemies:
            self.enemies.remove(e)
        if score:
            self.combo      += 1
            self.combo_timer = 2.5
            if self.combo >= 5:
                self.multiplier  = min(8, self.multiplier + 1)
                self.mult_timer  = 5.0
                self.combo       = 0
            pts = int(e['score'] * self.multiplier)
            self.score += pts
            if self.score > self.high_score:
                self.high_score = self.score
            self._maybe_drop(e['x'], e['y'])
        self._check_wave_done()

    def _maybe_drop(self, x, y):
        pups = self.config.power_ups
        if not pups:
            return
        r = random.random()
        cumulative = 0.0
        for p in pups:
            cumulative += p.chance
            if r < cumulative:
                self.drops.append({'type': p.power_type,
                                   'x': x, 'y': y, 'color': p.color})
                break

    def _apply_pickup(self, ptype):
        cfg = self.config
        if ptype == 'weapon_upgrade':
            self.weapon_level = min(len(cfg.player.weapon_tiers),
                                    self.weapon_level + 1)
            self._fire_rate   = max(0.14, self._fire_rate - 0.04)
        elif ptype == 'shield':
            self.player_shield = min(100.0, self.player_shield + 50.0)
        elif ptype == 'health':
            self.player_hp = min(float(cfg.player.health),
                                 self.player_hp + 25.0)
        elif ptype == 'bomb':
            self.player_bombs = min(5, self.player_bombs + 1)
        elif ptype == 'speed':
            self._speed_boost = 5.0

    def _hit_player(self, dmg):
        if self.player_shield > 0:
            absorbed           = min(dmg, self.player_shield)
            self.player_shield -= absorbed
            dmg                -= absorbed
        self.player_hp -= dmg
        if self.player_hp <= 0:
            self.player_lives -= 1
            if self.player_lives <= 0:
                self.game_over = True
            else:
                self.player_hp     = float(self.config.player.health)
                self.player_shield = 0.0

    def _fire_player(self):
        cfg   = self.config
        tiers = cfg.player.weapon_tiers
        tier  = tiers[min(self.weapon_level - 1, len(tiers) - 1)]
        x, y  = self.player_x, self.player_y

        if tier == 'single':
            self.bullets.append({'x': x, 'y': y - 20, 'dmg': 10})
        elif tier == 'double':
            self.bullets.append({'x': x - 9,  'y': y - 20, 'dmg': 10})
            self.bullets.append({'x': x + 9,  'y': y - 20, 'dmg': 10})
        elif tier == 'spread':
            self.bullets.append({'x': x,      'y': y - 20, 'dmg': 10})
            self.bullets.append({'x': x - 13, 'y': y - 10, 'dmg': 8})
            self.bullets.append({'x': x + 13, 'y': y - 10, 'dmg': 8})
        elif tier == 'missile':
            self.bullets.append({'x': x, 'y': y - 20,
                                 'dmg': 25, 'homing': True})

    def _check_wave_done(self):
        if self.between_waves:
            return
        all_spawned = (self._spawned >= len(self._spawns))
        if self.is_boss_wave:
            done = all_spawned and self.boss is None and not self.enemies
        else:
            done = all_spawned and not self.enemies
        if done:
            self.between_waves = True
            self.between_timer = self._WAVE_GAP

    # ── Touch handling ────────────────────────────────────────────────────────

    def _on_touch_began(self, touch):
        if self.game_over:
            self._reset_state()
            return
        self._touch_x = touch.location.x

    def _on_touch_moved(self, touch):
        self._touch_x = touch.location.x

    # ── Headless fallback ─────────────────────────────────────────────────────

    def _headless_summary(self):
        cfg = self.config
        sep = '=' * 56
        print(sep)
        print(f'  {cfg.title}')
        print(f'  Atlas Nexus Game Builder v1.0 — PCVR Studios')
        print(sep)
        print(f'  Screen      : {cfg.width} \xd7 {cfg.height}')
        print(f'  Background  : {cfg.bg_color}')
        print(f'  Player      : HP={cfg.player.health}  '
              f'SPD={cfg.player.speed}  '
              f'Lives={cfg.player.lives}  '
              f'Bombs={cfg.player.bombs}')
        print(f'  Starfield   : {cfg.starfield.count} stars, '
              f'{cfg.starfield.layers} layers')
        print(f'  Enemy types : {len(cfg.enemies)}')
        for e in cfg.enemies:
            print(f'    \u2022 {e.name:<14} HP={e.health:<5} '
                  f'SPD={e.speed:<5} PTS={e.score}')
        print(f'  Boss        : HP={cfg.boss.health}  '
              f'PTS={cfg.boss.score}  '
              f'every {cfg.boss.every_n_waves} waves')
        print(f'  Power-Ups   : {len(cfg.power_ups)}')
        for p in cfg.power_ups:
            print(f'    \u2022 {p.power_type:<18} {p.chance:.0%} chance')
        print(f'  Difficulty  : '
              f'base={cfg.difficulty.base_enemies}  '
              f'+{cfg.difficulty.scale_per_wave}/wave')
        print(f'  Max waves   : '
              f'{"unlimited" if cfg.max_waves == 0 else cfg.max_waves}')
        print(sep)
        print('  [Launch in Pythonista 3 on iOS to play]')


# ─────────────────────────────────────────────────────────────────────────────
# GAME BUILDER  — fluent API
# ─────────────────────────────────────────────────────────────────────────────

class GameBuilder:
    """
    Fluent builder for Atlas Nexus Engine arcade games.

    All setter methods return ``self`` to enable method chaining.
    Call ``build()`` at the end to validate and produce a ``BuiltGame``.

    Example::

        game = (GameBuilder('Galactic Fury')
                .screen_size(380, 680)
                .bg_color('#0a0a12')
                .starfield(count=120, layers=3)
                .player(health=120, speed=220, lives=3, bombs=3)
                .enemy('scout',   health=25,  speed=100, score=80,
                       color='#44aaff')
                .enemy('gunship', health=70,  speed=55,  score=250,
                       color='#cc4422')
                .boss_every(5, health=600, score=2500)
                .power_up('weapon_upgrade', chance=0.20)
                .power_up('shield',         chance=0.15)
                .power_up('health',         chance=0.10)
                .hud(score=True, wave=True, health=True, lives=True)
                .wave_difficulty(base_enemies=4, scale_per_wave=2)
                .max_waves(30)
                .build())

        game.run()
    """

    def __init__(self, title='PCVR Game'):
        self._cfg = GameConfig(str(title))

    # ── Screen ───────────────────────────────────────────────────────────────

    def screen_size(self, width, height):
        """Set the game view dimensions in points."""
        self._cfg.width  = int(width)
        self._cfg.height = int(height)
        return self

    def bg_color(self, color):
        """Set background colour (CSS hex, e.g. ``'#0d0f14'``)."""
        self._cfg.bg_color = str(color)
        return self

    # ── Starfield ─────────────────────────────────────────────────────────────

    def starfield(self, count=115, layers=3,
                  min_speed=20.0, max_speed=80.0,
                  colors=None):
        """Configure the parallax starfield background."""
        self._cfg.starfield = StarfieldConfig(
            count=count, layers=layers,
            min_speed=min_speed, max_speed=max_speed,
            colors=colors,
        )
        return self

    # ── Player ───────────────────────────────────────────────────────────────

    def player(self, health=100, speed=200.0, lives=3, bombs=3,
               color='#5b8dee', width=30, height=30,
               weapon_tiers=None):
        """
        Configure the player ship.

        :param health:        Starting hit-points.
        :param speed:         Horizontal movement speed in points/second.
        :param lives:         Number of lives (respawns after death).
        :param bombs:         Starting bomb count.
        :param color:         Ship fill colour (CSS hex).
        :param width:         Collision & draw width in points.
        :param height:        Collision & draw height in points.
        :param weapon_tiers:  Ordered list of weapon tier names.
                              Valid names: ``'single'``, ``'double'``,
                              ``'spread'``, ``'missile'``.
        """
        self._cfg.player = PlayerConfig(
            health=health, speed=speed, lives=lives, bombs=bombs,
            color=color, width=width, height=height,
            weapon_tiers=weapon_tiers,
        )
        return self

    # ── Enemies ──────────────────────────────────────────────────────────────

    def enemy(self, name, health, speed, score,
              color='#cc3333', width=28, height=28,
              fire_rate=1.5):
        """
        Add an enemy type.  Call multiple times to add multiple types.

        :param name:      Unique identifier string (e.g. ``'fighter'``).
        :param health:    Starting hit-points.
        :param speed:     Downward movement speed in points/second.
        :param score:     Points awarded on kill.
        :param color:     Fill colour (CSS hex).
        :param width:     Collision & draw width in points.
        :param height:    Collision & draw height in points.
        :param fire_rate: Seconds between this enemy's shots.
        """
        self._cfg.enemies.append(
            EnemyConfig(name=name, health=health, speed=speed, score=score,
                        color=color, width=width, height=height,
                        fire_rate=fire_rate)
        )
        return self

    # ── Boss ─────────────────────────────────────────────────────────────────

    def boss_every(self, n_waves, health, score,
                   color='#ff6600', width=60, height=50,
                   phases=3, rage_threshold=0.3):
        """
        Configure bosses that appear every *n_waves* waves.

        :param n_waves:         Wave interval for boss appearance.
        :param health:          Starting hit-points.
        :param score:           Points awarded on boss kill.
        :param color:           Fill colour.
        :param width:           Collision & draw width.
        :param height:          Collision & draw height.
        :param phases:          Number of attack phases (cosmetic, for future use).
        :param rage_threshold:  HP fraction below which rage mode activates.
        """
        self._cfg.boss = BossConfig(
            health=health, score=score, every_n_waves=n_waves,
            color=color, width=width, height=height,
            phases=phases, rage_threshold=rage_threshold,
        )
        return self

    # ── Power-Ups ─────────────────────────────────────────────────────────────

    def power_up(self, power_type, chance=0.15, color='#ffdd00'):
        """
        Add a power-up drop type.

        :param power_type: One of ``'weapon_upgrade'``, ``'shield'``,
                           ``'health'``, ``'bomb'``, ``'speed'``.
        :param chance:     Per-kill spawn probability (0.0–1.0).
        :param color:      Drop indicator colour.
        """
        self._cfg.power_ups.append(
            PowerUpConfig(power_type=power_type, chance=chance, color=color)
        )
        return self

    # ── HUD ──────────────────────────────────────────────────────────────────

    def hud(self, score=True, high_score=True, wave=True,
            health=True, shield=True, lives=True,
            bombs=True, multiplier=True, combo=True,
            boss_health=True):
        """Select which HUD elements are displayed during play."""
        self._cfg.hud = HUDConfig(
            score=score, high_score=high_score, wave=wave,
            health=health, shield=shield, lives=lives,
            bombs=bombs, multiplier=multiplier,
            combo=combo, boss_health=boss_health,
        )
        return self

    # ── Wave difficulty ───────────────────────────────────────────────────────

    def wave_difficulty(self, base_enemies=5, scale_per_wave=2,
                        speed_scale=1.05, health_scale=1.08):
        """
        Control wave escalation.

        :param base_enemies:   Enemy count in wave 1.
        :param scale_per_wave: Additional enemies added per wave.
        :param speed_scale:    Multiplicative speed increase per wave.
        :param health_scale:   Multiplicative HP increase per wave.
        """
        self._cfg.difficulty = WaveDifficultyConfig(
            base_enemies=base_enemies,
            scale_per_wave=scale_per_wave,
            speed_scale=speed_scale,
            health_scale=health_scale,
        )
        return self

    # ── Max waves ─────────────────────────────────────────────────────────────

    def max_waves(self, n):
        """Set a wave limit (0 = unlimited)."""
        self._cfg.max_waves = max(0, int(n))
        return self

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self):
        """
        Validate the configuration and return a ``BuiltGame`` ready to run.

        :raises ValueError: If the configuration is invalid.
        """
        self._cfg.validate()
        return BuiltGame(self._cfg)

    # ── Utility ───────────────────────────────────────────────────────────────

    def summary(self):
        """Return a human-readable configuration summary string."""
        cfg = self._cfg
        lines = [
            f'GameBuilder Config — {cfg.title!r}',
            f'  Screen      : {cfg.width} \xd7 {cfg.height}',
            f'  Background  : {cfg.bg_color}',
            f'  Player      : HP={cfg.player.health}  '
            f'SPD={cfg.player.speed}  '
            f'Lives={cfg.player.lives}  '
            f'Bombs={cfg.player.bombs}',
            f'  Starfield   : {cfg.starfield.count} stars, '
            f'{cfg.starfield.layers} layers',
            f'  Enemy types : {len(cfg.enemies)}',
        ]
        for e in cfg.enemies:
            lines.append(f'    \u2022 {e.name:<14} HP={e.health:<5} '
                         f'SPD={e.speed:<5} PTS={e.score}')
        lines.append(f'  Boss        : HP={cfg.boss.health}  '
                     f'PTS={cfg.boss.score}  '
                     f'every {cfg.boss.every_n_waves} waves')
        lines.append(f'  Power-Ups   : {len(cfg.power_ups)}')
        for p in cfg.power_ups:
            lines.append(f'    \u2022 {p.power_type:<18} '
                         f'{p.chance:.0%} chance')
        lines.append(
            f'  Difficulty  : base={cfg.difficulty.base_enemies}  '
            f'+{cfg.difficulty.scale_per_wave}/wave'
        )
        lines.append(
            f'  Max waves   : '
            f'{"unlimited" if cfg.max_waves == 0 else cfg.max_waves}'
        )
        return '\n'.join(lines)

    def __repr__(self):
        return f'GameBuilder(title={self._cfg.title!r})'


# ─────────────────────────────────────────────────────────────────────────────
# BUILT-IN PRESETS
# ─────────────────────────────────────────────────────────────────────────────

def preset_skyburner():
    """
    Return a ``GameBuilder`` pre-configured to match SkyBurner Ultimate.

    Run with::

        preset_skyburner().build().run()
    """
    return (GameBuilder('SkyBurner Ultimate')
            .screen_size(380, 680)
            .bg_color('#0d0f14')
            .starfield(count=115, layers=3, min_speed=20, max_speed=80,
                       colors=['white', '#aaaaaa', '#666666'])
            .player(health=100, speed=220, lives=3, bombs=3,
                    color='#5b8dee',
                    weapon_tiers=['single', 'double', 'spread', 'missile'])
            .enemy('fighter', health=30,  speed=80,  score=100,
                   color='#cc3333', fire_rate=2.0)
            .enemy('cruiser', health=80,  speed=45,  score=300,
                   color='#994400', width=40, height=36, fire_rate=1.2)
            .boss_every(5, health=500, score=2000,
                        color='#ff6600', width=60, height=50,
                        phases=3, rage_threshold=0.30)
            .power_up('weapon_upgrade', chance=0.20, color='#5b8dee')
            .power_up('shield',         chance=0.15, color='#3399ff')
            .power_up('health',         chance=0.12, color='#3ecf8e')
            .power_up('bomb',           chance=0.08, color='#ff4444')
            .power_up('speed',          chance=0.06, color='#ffaa00')
            .hud(score=True, high_score=True, wave=True, health=True,
                 shield=True, lives=True, bombs=True,
                 multiplier=True, combo=True, boss_health=True)
            .wave_difficulty(base_enemies=5, scale_per_wave=2,
                             speed_scale=1.05, health_scale=1.08)
            .max_waves(0))


def preset_blitz():
    """
    Fast-paced preset: small enemies, high speed, infrequent bosses.

    Run with::

        preset_blitz().build().run()
    """
    return (GameBuilder('Blitz Mode')
            .screen_size(380, 680)
            .bg_color('#070712')
            .starfield(count=80, layers=2, min_speed=40, max_speed=120,
                       colors=['white', '#8888cc'])
            .player(health=80, speed=280, lives=2, bombs=2,
                    color='#3ecf8e',
                    weapon_tiers=['double', 'spread', 'missile'])
            .enemy('drone',  health=15,  speed=120, score=50,
                   color='#44bbff', width=20, height=20, fire_rate=1.0)
            .enemy('raider', health=35,  speed=90,  score=150,
                   color='#ff6644', width=26, height=24, fire_rate=0.8)
            .boss_every(10, health=300, score=1500,
                        color='#aa44ff', width=50, height=44,
                        rage_threshold=0.40)
            .power_up('weapon_upgrade', chance=0.25)
            .power_up('health',         chance=0.15)
            .hud(score=True, wave=True, health=True, lives=True)
            .wave_difficulty(base_enemies=8, scale_per_wave=3,
                             speed_scale=1.08, health_scale=1.05)
            .max_waves(0))


def preset_survival():
    """
    Survival preset: endless escalation, no power-ups, one life.

    Run with::

        preset_survival().build().run()
    """
    return (GameBuilder('Survival Mode')
            .screen_size(380, 680)
            .bg_color('#0d0a14')
            .starfield(count=60, layers=2)
            .player(health=150, speed=180, lives=1, bombs=5,
                    color='#ffaa00',
                    weapon_tiers=['single', 'double', 'spread', 'missile'])
            .enemy('grunt',   health=20,  speed=60,  score=80,
                   color='#cc3333')
            .enemy('soldier', health=60,  speed=40,  score=200,
                   color='#884422', width=32, height=30)
            .enemy('elite',   health=120, speed=70,  score=500,
                   color='#aa22aa', width=34, height=32, fire_rate=0.9)
            .boss_every(3, health=400, score=1800,
                        color='#ff3300', width=65, height=55,
                        phases=4, rage_threshold=0.25)
            .hud(score=True, wave=True, health=True, lives=True,
                 multiplier=True, combo=True)
            .wave_difficulty(base_enemies=6, scale_per_wave=3,
                             speed_scale=1.10, health_scale=1.12)
            .max_waves(0))


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('\n  \u00a9 PCVR Studios 2026')
    print('  Atlas Nexus Game Builder v1.0')
    print('  Contract: 0x05c870C5C6E7AF4298976886471c69Fc722107e4\n')

    _builder = preset_skyburner()
    print(_builder.summary())
    print()

    _game = _builder.build()
    _game.run()
