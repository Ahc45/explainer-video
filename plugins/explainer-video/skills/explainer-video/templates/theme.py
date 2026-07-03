"""Theme system for the explainer pipeline.
Loads theme.json and provides branded, reusable Manim components:
intro card, outro card, watermark. Swap theme.json -> whole video restyles.
"""
from manim import *
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "theme.json")))

PAL = T["palette"]
BG = PAL["bg"]; PRIMARY = PAL["primary"]; SECONDARY = PAL["secondary"]
ACCENT = PAL["accent"]; DIM = PAL["dim"]; TXT = PAL["text"]
FONT = T["font"]
FS = T["font_sizes"]


ICON_DIR = os.path.join(os.path.dirname(HERE), "assets", "icons")


def icon(name, width=1.4):
    """Brand/tech-stack icon as an ImageMobject (see scripts/icon_fetch.mjs).
    Falls back to a labeled outline box if the PNG hasn't been fetched, so a
    missing icon degrades gracefully instead of crashing the render."""
    png = os.path.join(ICON_DIR, f"{name}.png")
    if os.path.exists(png):
        m = ImageMobject(png)
        m.scale_to_fit_width(width)
        return m
    # Fallback: outlined box with the name (keeps layout intact).
    r = RoundedRectangle(width=width, height=width, corner_radius=0.12,
                         stroke_color=PRIMARY, stroke_width=3, fill_color=BG, fill_opacity=1)
    t = Text(name, font=FONT, font_size=18, color=PRIMARY).scale_to_fit_width(min(width * 0.8, r.width * 0.8)).move_to(r)
    return VGroup(r, t)


def icon_node(name, label=None, width=1.4, fs=26, color=None):
    """An icon with a caption underneath — the workhorse node for architecture
    diagrams. Returns a Group (ImageMobject can't live in a VGroup, so use Group).
    Position the whole node with .move_to(...)."""
    ic = icon(name, width)
    parts = [ic]
    if label:
        t = Text(label, font=FONT, font_size=fs, color=color or TXT)
        t.next_to(ic, DOWN, buff=0.22)
        parts.append(t)
    return Group(*parts)


def watermark():
    """Brand logo for the corner of every scene."""
    if not T["watermark"]["enabled"]:
        return VGroup()
    
    # Check for image watermark first
    img_path = os.path.join(os.path.dirname(HERE), "assets", "watermark.jpg")
    if not os.path.exists(img_path):
        img_path = os.path.join(os.path.dirname(HERE), "assets", "watermark.png")
    
    if os.path.exists(img_path):
        # Use image watermark
        wm = ImageMobject(img_path)
        wm.scale_to_fit_width(1.2)  # Adjust size for portrait video
        wm.set_opacity(T["watermark"]["opacity"])
    else:
        # Fallback to text watermark
        wm = Text(T["brand"], font=FONT, font_size=22, color=TXT)
        wm.set_opacity(T["watermark"]["opacity"])
    
    corner = {"DR": DR, "DL": DL, "UR": UR, "UL": UL}[T["watermark"]["corner"]]
    wm.to_corner(corner, buff=0.4)
    return wm


class IntroCard(Scene):
    """Branded opener: kicker + big title + underline.
    Kept SHORT on purpose — a long brand card before the hook tanks retention. Default ~2s so
    Scene1's hook lands fast (see SKILL.md "The hook is the whole ballgame")."""
    def construct(self, title_text=None, duration=2.0):
        self.camera.background_color = BG
        title_text = title_text or T.get("_title", "Explainer")
        kicker = Text(T["intro"]["kicker"], font=FONT, font_size=FS["caption"],
                      color=ACCENT, weight=BOLD).shift(UP*1.2)
        title = Text(title_text, font=FONT, font_size=FS["title"], color=PRIMARY, weight=BOLD)
        # PITFALL: only shrink if it overflows; never up-scale short titles.
        if title.width > 7.0:
            title.scale_to_fit_width(7.0)
        line = Line(LEFT*2.5, RIGHT*2.5, color=SECONDARY, stroke_width=6).next_to(title, DOWN, buff=0.5)
        self.play(FadeIn(kicker, shift=DOWN*0.3), run_time=0.5)
        self.play(Write(title), run_time=0.9)
        if T["intro"]["show_underline"]:
            self.play(Create(line), run_time=0.4)
        self.add(watermark())
        self.wait(max(0.1, duration - 1.8))
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)


class OutroCard(Scene):
    """Branded closer: tagline + CTA + handle."""
    def construct(self, duration=3.0):
        self.camera.background_color = BG
        tagline = Text(T["outro"]["tagline"], font=FONT, font_size=FS["heading"],
                       color=TXT, weight=BOLD).shift(UP*1.0)
        cta = Text(T["outro"]["cta"], font=FONT, font_size=FS["body"],
                   color=ACCENT, weight=BOLD).next_to(tagline, DOWN, buff=1.0)
        handle = Text(T["brand"], font=FONT, font_size=FS["label"],
                      color=PRIMARY).next_to(cta, DOWN, buff=0.5)
        box = SurroundingRectangle(cta, color=ACCENT, buff=0.35, corner_radius=0.15)
        self.play(Write(tagline), run_time=1.2)
        self.play(FadeIn(cta), Create(box), run_time=1.0)
        self.play(FadeIn(handle, shift=UP*0.2), run_time=0.6)
        self.wait(max(0.1, duration - 3.3))
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
