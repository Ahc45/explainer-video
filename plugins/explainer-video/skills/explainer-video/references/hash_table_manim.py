from manim import *

class HashTableExplainer(Scene):
    def construct(self):
        # Scene 1: The Problem
        books = VGroup(*[Square(side_length=0.5, fill_opacity=1).set_color(BLUE) for _ in range(20)])
        books.arrange_in_grid(rows=5, cols=4, buff=0.1)
        books.to_edge(DOWN)
        
        confused_icon = Text("?", font_size=72).set_color(YELLOW)
        confused_icon.move_to(UP * 2)

        self.play(FadeIn(books), FadeIn(confused_icon))
        self.wait(1)
        self.play(FadeOut(books), FadeOut(confused_icon))

        # Scene 2: The Solution - Hashing
        machine = Rectangle(width=3, height=2).set_fill(GRAY, opacity=0.5)
        machine_label = Text("Hash Function", font_size=24).move_to(machine.get_center())
        self.play(Create(machine), Write(machine_label))

        key = Text("Book Title", font_size=36).shift(UP * 2)
        self.play(Write(key))

        shelf_num = Text("Shelf #42", font_size=36).shift(DOWN * 2)
        self.play(key.animate.next_to(machine, DOWN), run_time=1)
        self.play(ReplacementTransform(key.copy(), shelf_num))
        self.wait(1)

        # Scene 3: The Mechanism (O(1))
        complexity = Text("O(1)", font_size=72, color=GREEN).move_to(ORIGIN)
        self.play(FadeOut(machine), FadeOut(machine_label), FadeOut(shelf_num), FadeOut(key))
        self.play(Write(complexity))
        self.wait(1)
        self.play(FadeOut(complexity))

        # Scene 4: Collisions
        shelf = Rectangle(width=2, height=1).set_fill(GRAY, opacity=0.5)
        shelf_label = Text("Shelf 42", font_size=24).next_to(shelf, DOWN)
        self.play(Create(shelf), Write(shelf_label))

        book1 = Square(side_length=0.5, fill_opacity=1).set_color(BLUE)
        book2 = Square(side_length=0.5, fill_opacity=1).set_color(RED)
        book1.move_to(shelf.get_center())
        book2.next_to(book1, DOWN, buff=0)

        self.play(Create(book1))
        self.wait(0.5)
        self.play(Create(book2)) # Collision!
        collision_text = Text("Collision!", color=RED).to_edge(UP)
        self.play(Write(collision_text))
        self.wait(1)

        # Scene 5: Conclusion
        self.play(FadeOut(shelf), FadeOut(book1), FadeOut(book2), FadeOut(shelf_label), FadeOut(collision_text))
        final_text = Text("Hash Tables: Fast & Efficient", font_size=40)
        self.play(Write(final_text))
        self.wait(2)
