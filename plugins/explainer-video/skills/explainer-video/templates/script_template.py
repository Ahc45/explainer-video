#!/usr/bin/env python3
"""Manim script SCAFFOLD for the explainer pipeline. Copy to `script.py` in a project,
then replace the content scenes. Portrait 9:16, synced to timing_contract.json durations.

Rules that keep sync intact (see SKILL.md):
  - One Scene subclass per scene `id` in timing_contract.json.
  - Track `used` = sum of every run_time + wait. End with a 0.5s FadeOut (counted).
  - Call fill(self, D["<id>"], used) right before the FadeOut so the video length
    matches the measured audio duration.
  - Add self.add(watermark()) at the top of every CONTENT scene (not the bookends).
  - Render order: SceneIntro <content ids...> SceneOutro (bookends are SILENT).

Scene-vocabulary recipes (proven, copy-paste-friendly) are at the bottom of this file.
"""
from manim import *
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "templates"))
from theme import (BG, PRIMARY, SECONDARY, ACCENT, DIM, TXT, FONT,
                   watermark, IntroCard, OutroCard, icon, icon_node)

with open("timing_contract.json") as f:
    C = json.load(f)
D = {s["id"]: s["duration"] for s in C["scenes"]}

config.frame_width = 9
config.frame_height = 16
config.pixel_width = 1080
config.pixel_height = 1920


# ---- helpers -------------------------------------------------------------
def fill(scene, target, used):
    """Wait so total scene length == audio duration (0.5s reserved for the fade-out)."""
    scene.wait(max(0.05, target - used - 0.5))


def box(label, w, h, color, fs=34):
    """A rounded, outlined label box on the dark background — the workhorse mobject."""
    r = RoundedRectangle(width=w, height=h, corner_radius=0.15,
                         stroke_color=color, stroke_width=4, fill_color=BG, fill_opacity=1)
    t = Text(label, font=FONT, font_size=fs, color=color).move_to(r)
    return VGroup(r, t)


# ---- bookends (silent; styling comes from templates/theme.json) ----------
class SceneIntro(IntroCard):
    def construct(self):
        super().construct(title_text=C["title"], duration=2.0)


class SceneOutro(OutroCard):
    def construct(self):
        super().construct(duration=3.0)


# ---- content scenes: rename to your timing_contract ids, swap the visuals -
class Scene1_Hook(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(watermark())
        used = 0
        title = Text("your hook here", font=FONT, font_size=56, color=TXT, weight=BOLD).shift(UP * 3.5)
        self.play(Write(title), run_time=1.2); used += 1.2
        # ... build + animate, incrementing `used` by each run_time ...
        fill(self, D["Scene1_Hook"], used)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


class Scene2_Body(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.add(watermark())
        used = 0
        # Example: key -> transform -> output flow (see FLOW recipe below)
        a = box("input", 3.2, 1.1, PRIMARY).shift(UP * 3)
        f = box("process()", 3.0, 1.3, ACCENT, 40).shift(UP * 0.3)
        out = box("output", 3.2, 1.1, SECONDARY).shift(DOWN * 2.6)
        ar1 = Arrow(a.get_bottom(), f.get_top(), color=TXT, buff=0.2, stroke_width=5)
        ar2 = Arrow(f.get_bottom(), out.get_top(), color=TXT, buff=0.2, stroke_width=5)
        self.play(FadeIn(a, shift=DOWN * 0.2), run_time=0.8); used += 0.8
        self.play(GrowArrow(ar1), Create(f), run_time=0.9); used += 0.9
        self.play(GrowArrow(ar2), FadeIn(out, shift=DOWN * 0.2), run_time=0.9); used += 0.9
        self.play(Indicate(out, color=SECONDARY, scale_factor=1.15), run_time=0.8); used += 0.8
        fill(self, D["Scene2_Body"], used)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


# ==========================================================================
# SCENE-VOCABULARY RECIPES  (lift these into content scenes)
# --------------------------------------------------------------------------
# HOOK / TENSION:
#   pile = VGroup(*[Square(0.7, stroke_color=DIM, fill_color=PRIMARY, fill_opacity=0.25)
#                   for _ in range(24)]).arrange_in_grid(rows=4, cols=6, buff=0.12).shift(DOWN*4)
#   q = Text("?", font=FONT, font_size=170, color=SECONDARY, weight=BOLD).shift(UP*2.5)
#   self.play(LaggedStartMap(FadeIn, pile, shift=UP*0.2, lag_ratio=0.04), run_time=1.4)
#
# VERTICAL FLOW (key -> fn -> result): use box() + Arrow(..., buff=0.2) + GrowArrow.
#   Stack boxes on the Y axis (portrait!), never spread on X.
#
# INDEXED LIST / O(1) LOOKUP:
#   slots = VGroup(*[box(f"slot {i}", 5.0, 1.2, DIM, 34) for i in range(6)]).arrange(DOWN, buff=0.3)
#   ptr = Triangle(color=ACCENT, fill_opacity=1).scale(0.28).rotate(-PI/2).next_to(slots[2], LEFT)
#   self.play(slots[2][0].animate.set_stroke(ACCENT, 6), slots[2][1].animate.set_color(ACCENT))
#
# CLUSTERING (unsupervised): scatter Dots, then .animate.move_to(target).set_color(...)
#   into two grids; draw Circle(radius=1.15, color=...) around each cluster.
#
# TWO-COLUMN COMPARE: a DIM Line(UP*5, DOWN*5) divider; headers + VGroup of short
#   Text lines arranged DOWN with aligned_edge=LEFT at LEFT*2.2 / RIGHT*2.2.
#
# PAYOFF: 2 short colored lines (primary/secondary) + one ACCENT takeaway,
#   finish with Indicate(takeaway).
#
# ICON NODES / ARCHITECTURE DIAGRAM (system-design, tech-stack):
#   Fetch icons first: `node scripts/icon_fetch.mjs` (needs "icons" in the contract).
#   Icons are ImageMobjects -> put nodes in a Group, animate with FadeIn/.animate, and
#   "highlight" with a SurroundingRectangle (never set_color on the image).
#     client = icon_node("react", "client").move_to(UP*5)
#     lb     = icon_node("nginx", "load balancer").move_to(UP*1.8)
#     db     = icon_node("postgresql", "database").move_to(DOWN*2)
#     a1 = Arrow(client.get_bottom(), lb.get_top(), color=TXT, buff=0.2, stroke_width=5)
#     self.play(FadeIn(client, shift=DOWN*0.2), run_time=0.7); used += 0.7
#     self.play(GrowArrow(a1), FadeIn(lb, shift=DOWN*0.2), run_time=0.9); used += 0.9
#     ring = SurroundingRectangle(db, color=ACCENT, buff=0.15, corner_radius=0.1)
#     self.play(Create(ring), run_time=0.6); used += 0.6   # highlight the DB
#   Stack nodes on Y (portrait!); a request "packet" = Dot(color=ACCENT) you move
#   along the arrows with .animate.move_to to show data flowing through the system.
#
# Keep it monospace (FONT=Menlo), keep text short (portrait is narrow — long lines
# overflow), and grab QA frames AFTER a scene's animations settle, not mid-Write().
# ==========================================================================
