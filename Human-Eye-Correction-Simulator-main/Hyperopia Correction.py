import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
import os
import math
import random
from collections import deque

# =========================
# CONFIGURATION
# =========================
IMAGE_PATH = "snellen_chart.png"
WINDOW_W = 1920
WINDOW_H = 1080
DISPLAY_W = 650
DISPLAY_H = 750

# Modern color palette
COLORS = {
    'primary': '#2563eb',      # Modern blue
    'primary_dark': '#1e40af',
    'success': '#10b981',      # Modern green
    'success_light': '#34d399',
    'danger': '#ef4444',       # Modern red
    'danger_light': '#f87171',
    'warning': '#f59e0b',      # Modern orange
    'dark': '#1f2937',
    'dark_blue': '#0f172a',
    'light_gray': '#f3f4f6',
    'medium_gray': '#6b7280',
    'white': '#ffffff',
    'glow_blue': '#60a5fa',
    'glow_green': '#6ee7b7',
    'glow_red': '#fca5a5'
}

# =========================
# FONT HELPER
# =========================
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "arial.ttf",
    "Arial.ttf",
]

def get_pil_font(size):
    """Load a PIL font at the given size, falling back to default."""
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

# =========================
# PARTICLE SYSTEM
# =========================
class LightParticle:
    """Represents a photon traveling through the optical system"""
    def __init__(self, x, y, target_y, hyperopia, lens_power):
        self.x = x
        self.y = y
        self.start_y = y
        self.target_y = target_y
        self.hyperopia = hyperopia
        self.lens_power = lens_power
        self.vx = 5
        self.vy = 0
        self.color = COLORS['warning'] if lens_power == 0 else COLORS['glow_blue']
        self.life = 100
        self.max_life = 100
        self.trail = deque(maxlen=10)

        # Calculate convergence point
        base_focus_offset = hyperopia * 12
        correction_offset = lens_power * base_focus_offset
        self.focus_offset = base_focus_offset - correction_offset

    def update(self, retina_x, center_y, lens_x):
        """Update particle position with realistic convergence"""
        self.trail.append((self.x, self.y))

        focus_x = retina_x + self.focus_offset

        if self.x < focus_x:
            dx = focus_x - self.x
            dy = center_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                speed = 5
                self.vx = (dx / distance) * speed
                self.vy = (dy / distance) * speed

        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def is_alive(self):
        return self.life > 0

# =========================
# TEST PATTERN GENERATOR
# =========================
class TestPatternGenerator:
    """Generate various vision test patterns"""

    @staticmethod
    def create_snellen_chart(width, height):
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        lines = [
            ("E", 140),
            ("F P", 110),
            ("T O Z", 90),
            ("L P E D", 70),
            ("P E C F D", 58),
            ("E D F C Z P", 48),
            ("F E L O P Z D", 40),
            ("D E F P O T E C", 32),
        ]

        y = 40
        for text, size in lines:
            font = get_pil_font(size)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            x = (width - text_w) // 2
            draw.text((x, y), text, fill="black", font=font)
            y += size + 15

        return img

    @staticmethod
    def create_reading_text(width, height):
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        title_font = get_pil_font(22)
        body_font = get_pil_font(16)
        small_font = get_pil_font(13)

        title = "Reading Vision Test"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = title_bbox[2] - title_bbox[0]
        draw.text((width // 2 - title_w // 2, 40), title, fill=COLORS['primary'], font=title_font)

        paragraphs = [
            "The human eye is a remarkable",
            "organ capable of detecting light",
            "and converting it into electrical",
            "signals. The cornea and lens work",
            "together to focus light precisely",
            "onto the retina at the back of",
            "the eye. When this focusing system",
            "is disrupted, vision becomes blurred.",
            "",
            "Convex lenses help hyperopic eyes",
            "by converging light rays before",
            "they enter the eye, compensating",
            "for the eye's insufficient optical",
            "power and restoring clear vision."
        ]

        y = 110
        for line in paragraphs:
            draw.text((60, y), line, fill="black", font=body_font)
            y += 32

        y += 40
        small_text = [
            "Small print test: The quick brown fox jumps",
            "over the lazy dog. Can you read this clearly?",
            "Vision quality depends on proper focus."
        ]
        for line in small_text:
            draw.text((60, y), line, fill="#333333", font=small_font)
            y += 24

        return img

    @staticmethod
    def create_contrast_test(width, height):
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        title_font = get_pil_font(22)
        draw.text((width // 2 - 110, 30), "Contrast Sensitivity", fill=COLORS['primary'], font=title_font)

        y = 90
        contrasts = [255, 200, 150, 100, 70, 50, 30]

        for contrast in contrasts:
            for x in range(0, width, 30):
                color = (contrast, contrast, contrast) if (x // 30) % 2 == 0 else (255, 255, 255)
                draw.rectangle([x, y, x + 30, y + 80], fill=color)
            y += 95

        return img

    @staticmethod
    def create_astigmatism_test(width, height):
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        title_font = get_pil_font(22)
        draw.text((width // 2 - 100, 30), "Astigmatism Test", fill=COLORS['primary'], font=title_font)

        center_x = width // 2
        center_y = height // 2 + 30
        radius = 240

        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = center_x + int(radius * 0.3 * math.cos(rad))
            y1 = center_y + int(radius * 0.3 * math.sin(rad))
            x2 = center_x + int(radius * math.cos(rad))
            y2 = center_y + int(radius * math.sin(rad))
            draw.line([x1, y1, x2, y2], fill="black", width=4)

        draw.ellipse([center_x - 15, center_y - 15, center_x + 15, center_y + 15],
                     fill="black")

        return img

# =========================
# IMAGE PROCESSING
# =========================
def apply_hyperopia_blur(img, severity):
    if severity == 0:
        return img.copy()

    radius = severity * 1.2
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))

    contrast_factor = 1.0 - (severity * 0.02)
    blurred = ImageEnhance.Contrast(blurred).enhance(contrast_factor)

    if severity > 5:
        return add_chromatic_aberration(blurred, severity - 5)

    return blurred

def add_chromatic_aberration(img, amount):
    r, g, b = img.split()

    offset = int(amount * 0.5)
    if offset > 0:
        r = ImageOps.expand(r, border=offset, fill=0)
        r = r.crop((offset*2, offset, r.width, r.height-offset))

        b = ImageOps.expand(b, border=offset, fill=0)
        b = b.crop((0, offset, b.width-offset*2, b.height-offset))

    return Image.merge("RGB", (r, g, b))

def apply_lens_correction(blurred_img, original_img, correction_strength):
    if correction_strength == 0:
        return blurred_img

    sharpness = 2.5 * correction_strength
    corrected = ImageEnhance.Sharpness(blurred_img).enhance(1.0 + sharpness)

    if correction_strength > 0.3:
        corrected = corrected.filter(
            ImageFilter.UnsharpMask(
                radius=3,
                percent=int(200 * correction_strength),
                threshold=1
            )
        )

    corrected = Image.blend(blurred_img, original_img, correction_strength * 0.95)
    corrected = ImageEnhance.Contrast(corrected).enhance(1.0 + 0.1 * correction_strength)

    return corrected

# =========================
# MODERN GRADIENT FRAME
# =========================
class GradientFrame(tk.Canvas):
    """Frame with gradient background"""
    def __init__(self, parent, color1, color2, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind('<Configure>', self._draw_gradient)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 1 or height < 1:
            return

        # Create gradient
        r1, g1, b1 = self.winfo_rgb(self.color1)
        r2, g2, b2 = self.winfo_rgb(self.color2)
        r1, g1, b1 = r1/256, g1/256, b1/256
        r2, g2, b2 = r2/256, g2/256, b2/256

        for i in range(height):
            ratio = i / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_line(0, i, width, i, fill=color, tags="gradient")

# =========================
# ADVANCED EYE ANATOMY
# =========================
class AdvancedEyeAnatomy:
    """Detailed interactive eye anatomy with particle system"""

    def __init__(self, canvas, x, y, width, height):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        self.particles = []
        self.animating = False
        self.lens_power = 0
        self.hyperopia_severity = 0

        self.cornea_x = self.center_x - 120
        self.lens_x = self.center_x - 60
        self.retina_x = self.center_x + 100

    def draw_anatomy(self, hyperopia_severity, lens_power):
        """Draw detailed eye anatomy"""
        self.canvas.delete("anatomy")
        self.lens_power = lens_power
        self.hyperopia_severity = hyperopia_severity

        eye_width = 240
        eye_height = 180

        # Sclera with subtle gradient effect
        self.canvas.create_oval(
            self.center_x - eye_width//2, self.center_y - eye_height//2,
            self.center_x + eye_width//2, self.center_y + eye_height//2,
            fill="#f8f8f8", outline="#888", width=3, tags="anatomy"
        )

        # Retina
        retina_points = []
        for i in range(-60, 61, 10):
            x = self.retina_x
            y = self.center_y + i
            retina_points.extend([x, y])
        self.canvas.create_line(retina_points, fill=COLORS['danger'], width=5, tags="anatomy", smooth=True)

        # Fovea with glow
        self.canvas.create_oval(
            self.retina_x - 12, self.center_y - 12,
            self.retina_x + 12, self.center_y + 12,
            fill=COLORS['danger_light'], outline=COLORS['danger'], width=2, tags="anatomy"
        )
        self.canvas.create_oval(
            self.retina_x - 6, self.center_y - 6,
            self.retina_x + 6, self.center_y + 6,
            fill=COLORS['danger'], outline="", tags="anatomy"
        )

        # Vitreous
        self.canvas.create_text(
            self.center_x + 20, self.center_y,
            text="Vitreous", font=("Arial", 11, "italic"),
            fill="#bbb", tags="anatomy"
        )

        # Cornea
        cornea_points = []
        for i in range(-70, 71, 10):
            angle = i / 70 * 0.8
            x = self.cornea_x - 20 * math.cos(angle)
            y = self.center_y + i
            cornea_points.extend([x, y])
        self.canvas.create_line(cornea_points, fill=COLORS['primary'], width=5, tags="anatomy", smooth=True)

        # Cornea highlights
        self.canvas.create_arc(
            self.cornea_x - 35, self.center_y - 80,
            self.cornea_x + 5, self.center_y - 20,
            start=60, extent=60, outline="white", width=3, style=tk.ARC, tags="anatomy"
        )

        # Lens
        lens_top = self.center_y - 50
        lens_bottom = self.center_y + 50

        self.canvas.create_arc(
            self.lens_x - 25, lens_top,
            self.lens_x + 5, lens_bottom,
            start=90, extent=180, outline=COLORS['glow_blue'], width=4,
            style=tk.ARC, tags="anatomy"
        )
        self.canvas.create_arc(
            self.lens_x - 5, lens_top,
            self.lens_x + 25, lens_bottom,
            start=270, extent=180, outline=COLORS['glow_blue'], width=4,
            style=tk.ARC, tags="anatomy"
        )
        self.canvas.create_oval(
            self.lens_x - 15, lens_top + 10,
            self.lens_x + 15, lens_bottom - 10,
            fill="#e3f2fd", outline="", tags="anatomy"
        )

        # Iris and Pupil with gradient effect
        iris_radius = 35
        # Outer iris
        self.canvas.create_oval(
            self.cornea_x - iris_radius, self.center_y - iris_radius,
            self.cornea_x + iris_radius, self.center_y + iris_radius,
            fill=COLORS['primary'], outline=COLORS['primary_dark'], width=3, tags="anatomy"
        )
        # Inner iris detail
        self.canvas.create_oval(
            self.cornea_x - iris_radius + 5, self.center_y - iris_radius + 5,
            self.cornea_x + iris_radius - 5, self.center_y + iris_radius - 5,
            fill="", outline=COLORS['glow_blue'], width=1, tags="anatomy"
        )

        pupil_radius = 18
        self.canvas.create_oval(
            self.cornea_x - pupil_radius, self.center_y - pupil_radius,
            self.cornea_x + pupil_radius, self.center_y + pupil_radius,
            fill="#000", outline="", tags="anatomy"
        )

        # External corrective lens with glass effect
        if lens_power > 0:
            ext_lens_x = self.cornea_x - 80
            ext_lens_height = 120

            # Convex lens with gradient
            self.canvas.create_arc(
                ext_lens_x - 30, self.center_y - ext_lens_height//2,
                ext_lens_x, self.center_y + ext_lens_height//2,
                start=90, extent=180, outline=COLORS['primary'], width=6,
                style=tk.ARC, tags="anatomy"
            )
            self.canvas.create_arc(
                ext_lens_x, self.center_y - ext_lens_height//2,
                ext_lens_x + 30, self.center_y + ext_lens_height//2,
                start=270, extent=180, outline=COLORS['primary'], width=6,
                style=tk.ARC, tags="anatomy"
            )

            # Multiple glass highlights for depth
            self.canvas.create_arc(
                ext_lens_x - 25, self.center_y - ext_lens_height//2 + 20,
                ext_lens_x + 10, self.center_y - ext_lens_height//2 + 60,
                start=45, extent=90, outline="white", width=4,
                style=tk.ARC, tags="anatomy"
            )
            self.canvas.create_arc(
                ext_lens_x - 20, self.center_y - ext_lens_height//2 + 25,
                ext_lens_x + 5, self.center_y - ext_lens_height//2 + 55,
                start=50, extent=80, outline=COLORS['glow_blue'], width=2,
                style=tk.ARC, tags="anatomy"
            )
            self.canvas.create_arc(
                ext_lens_x - 10, self.center_y + ext_lens_height//2 - 60,
                ext_lens_x + 25, self.center_y + ext_lens_height//2 - 20,
                start=225, extent=90, outline="white", width=3,
                style=tk.ARC, tags="anatomy"
            )

            # Convex Lens label — plain text above the lens, no rectangle
            self.canvas.create_text(
                ext_lens_x, self.center_y - ext_lens_height//2 - 12,
                text="Convex Lens", font=("Arial", 11, "bold"),
                fill=COLORS['primary'], tags="anatomy"
            )

            # Power badge — plain text below the lens, no rectangle
            power_text = f"+{lens_power * hyperopia_severity:.1f}D"
            self.canvas.create_text(
                ext_lens_x, self.center_y + ext_lens_height//2 + 14,
                text=power_text,
                font=("Arial", 11, "bold"),
                fill=COLORS['success'], tags="anatomy"
            )

        # Calculate focus point
        base_focus_offset = hyperopia_severity * 12
        correction_offset = lens_power * base_focus_offset
        focus_x = self.retina_x + base_focus_offset - correction_offset

        is_focused = abs(focus_x - self.retina_x) < 15
        focus_color = COLORS['success'] if is_focused else COLORS['danger']

        # Draw light rays with glow
        ray_offsets = [-50, -25, 0, 25, 50]

        for offset in ray_offsets:
            start_x = self.lens_x + 20
            start_y = self.center_y + offset

            if is_focused:
                # Glow effect for successful focus
                self.canvas.create_line(
                    start_x, start_y,
                    self.retina_x, self.center_y,
                    fill=COLORS['glow_green'], width=4,
                    tags="anatomy"
                )
                self.canvas.create_line(
                    start_x, start_y,
                    self.retina_x, self.center_y,
                    fill=COLORS['success'], width=2, arrow=tk.LAST,
                    tags="anatomy"
                )
            else:
                progress = (self.retina_x - start_x) / (focus_x - start_x) if focus_x != start_x else 1
                ray_y_at_retina = start_y + (self.center_y - start_y) * progress

                # Glow for unfocused
                self.canvas.create_line(
                    start_x, start_y,
                    self.retina_x, ray_y_at_retina,
                    fill=COLORS['glow_red'], width=4,
                    tags="anatomy"
                )
                self.canvas.create_line(
                    start_x, start_y,
                    self.retina_x, ray_y_at_retina,
                    fill=COLORS['danger'], width=2,
                    tags="anatomy"
                )

                if focus_x < self.retina_x + 150:
                    self.canvas.create_line(
                        self.retina_x, ray_y_at_retina,
                        focus_x, self.center_y,
                        fill=COLORS['danger_light'], width=1, dash=(4, 4),
                        tags="anatomy", arrow=tk.LAST
                    )

        # Focus point with pulsing glow
        glow_radius = 18
        self.canvas.create_oval(
            focus_x - glow_radius, self.center_y - glow_radius,
            focus_x + glow_radius, self.center_y + glow_radius,
            fill="", outline=focus_color, width=1, tags="anatomy"
        )
        self.canvas.create_oval(
            focus_x - 10, self.center_y - 10,
            focus_x + 10, self.center_y + 10,
            fill=focus_color, outline="white", width=3, tags="anatomy"
        )

        # Blur circle on retina
        if not is_focused:
            blur_radius = min(abs(focus_x - self.retina_x) * 0.3, 40)
            self.canvas.create_oval(
                self.retina_x - 5, self.center_y - blur_radius,
                self.retina_x + 15, self.center_y + blur_radius,
                outline=COLORS['danger'], width=3, dash=(3, 3),
                tags="anatomy"
            )

        # ── Anatomy labels — tick + plain text, no filled rectangles ──
        # Tick starts just below the sclera oval (center_y + eye_height/2)
        tick_top = self.center_y + 90
        tick_bot = tick_top + 10
        label_y  = tick_bot + 11   # text centre

        for lx, text, color in [
            (self.cornea_x, "Cornea", COLORS['primary']),
            (self.lens_x,   "Lens",   COLORS['glow_blue']),
            (self.retina_x, "Retina", COLORS['danger']),
        ]:
            self.canvas.create_line(
                lx, tick_top, lx, tick_bot,
                fill=color, width=2, tags="anatomy"
            )
            self.canvas.create_text(
                lx, label_y,
                text=text,
                font=("Arial", 11, "bold"),
                fill=color,
                tags="anatomy"
            )

        # Status with modern styling
        status_y = self.y + self.height - 15
        if lens_power == 0:
            status = "Light converges BEHIND retina -> Rays spread -> BLURRED"
            color = COLORS['danger']
        elif is_focused:
            status = "Light converges ON retina -> Single point -> CRYSTAL CLEAR!"
            color = COLORS['success']
        else:
            status = f"Partial correction -> Moving focus point ({lens_power * 100:.0f}%)"
            color = COLORS['warning']

        self.canvas.create_text(
            self.center_x, status_y,
            text=status, font=("Arial", 12, "bold"),
            fill=color, tags="anatomy"
        )

    def start_particle_animation(self):
        if not self.animating:
            self.animating = True
            self.animate_particles()

    def stop_particle_animation(self):
        self.animating = False

    def animate_particles(self):
        if not self.animating:
            return

        if random.random() < 0.4:
            y_offset = random.randint(-50, 50)
            particle = LightParticle(
                self.x + 20,
                self.center_y + y_offset,
                self.center_y,
                self.hyperopia_severity,
                self.lens_power
            )
            self.particles.append(particle)

        for particle in self.particles[:]:
            particle.update(self.retina_x, self.center_y, self.lens_x)

            if not particle.is_alive() or particle.x > self.x + self.width + 50:
                self.particles.remove(particle)

        self.canvas.delete("particles")
        for particle in self.particles:
            if len(particle.trail) > 1:
                trail_points = []
                for px, py in particle.trail:
                    trail_points.extend([px, py])
                # Glow trail
                self.canvas.create_line(
                    trail_points, fill=particle.color, width=4,
                    tags="particles", smooth=True
                )
                self.canvas.create_line(
                    trail_points, fill="white", width=2,
                    tags="particles", smooth=True
                )

            size = 6
            # Glow particle
            self.canvas.create_oval(
                particle.x - size - 2, particle.y - size - 2,
                particle.x + size + 2, particle.y + size + 2,
                fill=particle.color, outline="", tags="particles"
            )
            self.canvas.create_oval(
                particle.x - size, particle.y - size,
                particle.x + size, particle.y + size,
                fill="white", outline="", tags="particles"
            )

        if self.animating:
            self.canvas.after(30, self.animate_particles)

# =========================
# MODERN METRICS DASHBOARD
# =========================
class ModernMetricsDashboard:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=COLORS['light_gray'])
        self.metrics = {}

        # Header with gradient
        header = tk.Frame(self.frame, bg=COLORS['dark'], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="PERFORMANCE METRICS",
            font=("Arial", 15, "bold"),
            bg=COLORS['dark'],
            fg="white"
        ).pack(expand=True)

        # Metric cards
        self.metric_labels = {}
        metric_names = [
            ("acuity", "Visual Acuity", "20/20", "👁"),
            ("clarity", "Image Clarity", "100%", "*"),
            ("focus", "Focus Quality", "Perfect", "O"),
            ("prescription", "RX Needed", "+0.0D", "+")
        ]

        metrics_container = tk.Frame(self.frame, bg=COLORS['light_gray'])
        metrics_container.pack(fill="x", pady=15)

        for key, name, default, icon in metric_names:
            # Card with shadow effect
            card = tk.Frame(metrics_container, bg="white", relief="raised", bd=2)
            card.pack(fill="x", padx=20, pady=6)

            # Inner card frame
            card_inner = tk.Frame(card, bg="white")
            card_inner.pack(fill="x", padx=15, pady=12)

            # Icon and label
            left_frame = tk.Frame(card_inner, bg="white")
            left_frame.pack(side="left")

            tk.Label(
                left_frame,
                text=icon,
                font=("Arial", 18),
                bg="white"
            ).pack(side="left", padx=(0, 10))

            tk.Label(
                left_frame,
                text=name,
                font=("Arial", 12, "bold"),
                bg="white",
                fg=COLORS['dark']
            ).pack(side="left")

            # Value
            value_label = tk.Label(
                card_inner,
                text=default,
                font=("Arial", 14, "bold"),
                bg="white",
                fg=COLORS['success']
            )
            value_label.pack(side="right")
            self.metric_labels[key] = value_label

        # Separator
        tk.Frame(self.frame, bg=COLORS['medium_gray'], height=2).pack(fill="x", padx=20, pady=15)

        # Progress bars
        self.create_modern_progress_bar("Optical Power", "optical", COLORS['danger'])
        self.create_modern_progress_bar("Correction Level", "correction", COLORS['success'])

    def create_modern_progress_bar(self, label, key, color):
        container = tk.Frame(self.frame, bg=COLORS['light_gray'])
        container.pack(fill="x", padx=25, pady=10)

        # Label row
        label_row = tk.Frame(container, bg=COLORS['light_gray'])
        label_row.pack(fill="x")

        tk.Label(
            label_row,
            text=label,
            font=("Arial", 11, "bold"),
            bg=COLORS['light_gray'],
            fg=COLORS['dark']
        ).pack(side="left")

        percent_label = tk.Label(
            label_row,
            text="0%",
            font=("Arial", 10, "bold"),
            bg=COLORS['light_gray'],
            fg=COLORS['medium_gray']
        )
        percent_label.pack(side="right")
        self.metric_labels[key + "_percent"] = percent_label

        # Progress bar with modern styling
        bar_bg = tk.Frame(container, bg="#e5e7eb", height=28, relief="flat")
        bar_bg.pack(fill="x", pady=(8, 0))

        # Inner glow bar
        bar_fill = tk.Frame(bar_bg, bg=color, height=28)
        bar_fill.place(x=0, y=0, relheight=1, relwidth=0)

        self.metric_labels[key + "_bar"] = bar_fill
        self.metric_labels[key + "_color"] = color

    def update(self, hyperopia_severity, lens_correction):
        effective_blur = hyperopia_severity * (1 - lens_correction)

        # Visual acuity
        if effective_blur < 0.5:
            acuity = "20/20"
            acuity_color = COLORS['success']
        elif effective_blur < 2:
            acuity = "20/30"
            acuity_color = COLORS['warning']
        elif effective_blur < 4:
            acuity = "20/50"
            acuity_color = COLORS['warning']
        elif effective_blur < 6:
            acuity = "20/100"
            acuity_color = COLORS['danger']
        else:
            acuity = "20/200"
            acuity_color = COLORS['danger']

        self.metric_labels["acuity"].config(text=acuity, fg=acuity_color)

        # Clarity
        clarity = max(0, 100 - effective_blur * 15)
        clarity_color = COLORS['success'] if clarity > 80 else COLORS['warning'] if clarity > 50 else COLORS['danger']
        self.metric_labels["clarity"].config(text=f"{clarity:.0f}%", fg=clarity_color)

        # Focus
        if effective_blur < 0.5:
            focus = "Perfect"
            focus_color = COLORS['success']
        elif effective_blur < 2:
            focus = "Good"
            focus_color = COLORS['primary']
        elif effective_blur < 4:
            focus = "Fair"
            focus_color = COLORS['warning']
        else:
            focus = "Poor"
            focus_color = COLORS['danger']
        self.metric_labels["focus"].config(text=focus, fg=focus_color)

        # Prescription
        needed_rx = hyperopia_severity * (1 - lens_correction)
        self.metric_labels["prescription"].config(
            text=f"+{needed_rx:.1f}D",
            fg=COLORS['danger'] if needed_rx > 1 else COLORS['success']
        )

        # Progress bars
        optical_power = hyperopia_severity / 10
        self.metric_labels["optical_bar"].place(relwidth=optical_power)
        self.metric_labels["optical_percent"].config(text=f"{optical_power*100:.0f}%")

        correction_level = lens_correction
        self.metric_labels["correction_bar"].place(relwidth=correction_level)
        self.metric_labels["correction_percent"].config(text=f"{correction_level*100:.0f}%")

        bar_color = COLORS['success'] if correction_level > 0.8 else COLORS['primary']
        self.metric_labels["correction_bar"].config(bg=bar_color)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

# =========================
# MAIN APPLICATION
# =========================
class UltimateHyperopiaSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Hyperopia Correction Simulator")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.configure(bg=COLORS['light_gray'])

        # State
        self.hyperopia_severity = 6.0
        self.lens_correction = 0.0
        self.auto_correcting = False
        self.current_pattern = "snellen"
        self.show_particles = True

        # Load patterns
        self.patterns = {
            "snellen": TestPatternGenerator.create_snellen_chart(DISPLAY_W, DISPLAY_H),
            "reading": TestPatternGenerator.create_reading_text(DISPLAY_W, DISPLAY_H),
            "contrast": TestPatternGenerator.create_contrast_test(DISPLAY_W, DISPLAY_H),
            "astigmatism": TestPatternGenerator.create_astigmatism_test(DISPLAY_W, DISPLAY_H)
        }

        if os.path.exists(IMAGE_PATH):
            custom = Image.open(IMAGE_PATH).convert("RGB")
            custom = ImageOps.exif_transpose(custom)
            custom.thumbnail((DISPLAY_W, DISPLAY_H))
            canvas = Image.new("RGB", (DISPLAY_W, DISPLAY_H), "white")
            x = (DISPLAY_W - custom.width) // 2
            y = (DISPLAY_H - custom.height) // 2
            canvas.paste(custom, (x, y))
            self.patterns["custom"] = custom

        self.current_display_left = None
        self.current_display_right = None

        self._setup_ui()
        self.update_visualization()

    def _setup_ui(self):
        # Modern gradient header
        header = GradientFrame(
            self.root,
            COLORS['primary_dark'],
            COLORS['primary'],
            height=140,
            highlightthickness=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        # FIX: use a valid bg color instead of "" for frames/labels inside Canvas
        title_container = tk.Frame(header, bg=COLORS['primary'])
        title_container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            title_container,
            text="HYPEROPIA CORRECTION SIMULATOR",
            font=("Arial", 32, "bold"),
            fg="white",
            bg=COLORS['primary']
        ).pack()

        tk.Label(
            title_container,
            text="Advanced Real-Time Optical Analysis & Vision Correction System",
            font=("Arial", 14),
            fg="#bfdbfe",
            bg=COLORS['primary']
        ).pack(pady=(8, 0))

        # Main content
        content = tk.Frame(self.root, bg=COLORS['light_gray'])
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Vision panels
        vision_container = tk.Frame(content, bg=COLORS['light_gray'])
        vision_container.pack(fill="both", expand=True)

        # LEFT PANEL
        left_panel = tk.Frame(vision_container, bg="white", relief="raised", bd=3)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        left_header = GradientFrame(
            left_panel,
            COLORS['danger'],
            COLORS['danger_light'],
            height=90,
            highlightthickness=0
        )
        left_header.pack(fill="x")
        left_header.pack_propagate(False)

        # FIX: valid bg color
        header_content = tk.Frame(left_header, bg=COLORS['danger'])
        header_content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            header_content,
            text="UNCORRECTED VISION",
            font=("Arial", 20, "bold"),
            fg="white",
            bg=COLORS['danger']
        ).pack()

        tk.Label(
            header_content,
            text="Light Converges Behind Retina -> Blurred Image",
            font=("Arial", 12),
            fg="#fee2e2",
            bg=COLORS['danger']
        ).pack(pady=(5, 0))

        self.left_canvas = tk.Canvas(
            left_panel,
            width=DISPLAY_W,
            height=DISPLAY_H,
            bg="white",
            highlightthickness=0
        )
        self.left_canvas.pack(pady=20, padx=20)

        self.left_status = tk.Label(
            left_panel,
            text="",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        self.left_status.pack(pady=15)

        # RIGHT PANEL
        right_panel = tk.Frame(vision_container, bg="white", relief="raised", bd=3)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        right_header = GradientFrame(
            right_panel,
            COLORS['success'],
            COLORS['success_light'],
            height=90,
            highlightthickness=0
        )
        right_header.pack(fill="x")
        right_header.pack_propagate(False)

        # FIX: valid bg color
        header_content = tk.Frame(right_header, bg=COLORS['success'])
        header_content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            header_content,
            text="CORRECTED VISION",
            font=("Arial", 20, "bold"),
            fg="white",
            bg=COLORS['success']
        ).pack()

        tk.Label(
            header_content,
            text="Light Converges On Retina -> Sharp Image",
            font=("Arial", 12),
            fg="#d1fae5",
            bg=COLORS['success']
        ).pack(pady=(5, 0))

        self.right_canvas = tk.Canvas(
            right_panel,
            width=DISPLAY_W,
            height=DISPLAY_H,
            bg="white",
            highlightthickness=0
        )
        self.right_canvas.pack(pady=20, padx=20)

        self.right_status = tk.Label(
            right_panel,
            text="",
            font=("Arial", 16, "bold"),
            bg="white"
        )
        self.right_status.pack(pady=15)

        # Bottom section
        bottom_container = tk.Frame(content, bg=COLORS['light_gray'])
        bottom_container.pack(fill="both", pady=(15, 0))

        # Anatomy panel
        anatomy_panel = tk.Frame(bottom_container, bg="white", relief="raised", bd=3, width=900)
        anatomy_panel.pack(side="left", fill="both", padx=(0, 10))
        anatomy_panel.pack_propagate(False)

        anatomy_header = GradientFrame(
            anatomy_panel,
            COLORS['primary_dark'],
            COLORS['primary'],
            height=75,
            highlightthickness=0
        )
        anatomy_header.pack(fill="x")
        anatomy_header.pack_propagate(False)

        # FIX: valid bg color
        header_content = tk.Frame(anatomy_header, bg=COLORS['primary'])
        header_content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            header_content,
            text="OPTICAL PATH ANALYSIS",
            font=("Arial", 18, "bold"),
            fg="white",
            bg=COLORS['primary']
        ).pack()

        tk.Label(
            header_content,
            text="Real-Time Light Ray Physics  |  Green = Focused  |  Red = Defocused",
            font=("Arial", 11),
            fg="#bfdbfe",
            bg=COLORS['primary']
        ).pack(pady=(3, 0))

        self.anatomy_canvas = tk.Canvas(
            anatomy_panel,
            width=880,
            height=280,
            bg="#fafafa",
            highlightthickness=0
        )
        self.anatomy_canvas.pack(pady=15, padx=10)

        self.eye_anatomy = AdvancedEyeAnatomy(self.anatomy_canvas, 10, 10, 860, 260)

        # Particle toggle with modern styling
        particle_frame = tk.Frame(anatomy_panel, bg="white")
        particle_frame.pack(pady=10)

        self.particle_var = tk.IntVar(value=1)
        particle_check = tk.Checkbutton(
            particle_frame,
            text="Animate Light Photons",
            font=("Arial", 13, "bold"),
            bg="white",
            fg=COLORS['primary'],
            selectcolor="white",
            variable=self.particle_var,
            command=self.toggle_particles,
            activebackground="white"
        )
        particle_check.pack()

        # Control panel
        control_panel = tk.Frame(bottom_container, bg="white", relief="raised", bd=3)
        control_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Test pattern selector with modern cards
        pattern_header = tk.Frame(control_panel, bg=COLORS['dark_blue'], height=50)
        pattern_header.pack(fill="x")
        pattern_header.pack_propagate(False)

        tk.Label(
            pattern_header,
            text="VISION TEST PATTERN",
            font=("Arial", 14, "bold"),
            bg=COLORS['dark_blue'],
            fg="white"
        ).pack(expand=True)

        pattern_container = tk.Frame(control_panel, bg=COLORS['light_gray'])
        pattern_container.pack(fill="x", padx=15, pady=15)

        patterns = [
            ("Snellen", "snellen"),
            ("Reading", "reading"),
            ("Contrast", "contrast"),
            ("Astigmatism", "astigmatism")
        ]

        if "custom" in self.patterns:
            patterns.append(("Custom", "custom"))

        self.pattern_var = tk.StringVar(value="snellen")

        btn_row = tk.Frame(pattern_container, bg=COLORS['light_gray'])
        btn_row.pack()

        for text, value in patterns:
            btn = tk.Radiobutton(
                btn_row,
                text=text,
                font=("Arial", 11, "bold"),
                variable=self.pattern_var,
                value=value,
                command=lambda v=value: self.change_pattern(v),
                bg="white",
                fg=COLORS['dark'],
                selectcolor=COLORS['primary'],
                activebackground="white",
                activeforeground=COLORS['primary'],
                indicatoron=0,
                width=10,
                height=2,
                relief="raised",
                bd=2
            )
            btn.pack(side="left", padx=5)

        # Sliders with modern styling
        # Severity
        sev_container = tk.Frame(control_panel, bg="white")
        sev_container.pack(fill="x", padx=20, pady=(20, 10))

        sev_header = tk.Frame(sev_container, bg="white")
        sev_header.pack(fill="x")

        tk.Label(
            sev_header,
            text="HYPEROPIA SEVERITY",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=COLORS['danger']
        ).pack(side="left")

        self.severity_label = tk.Label(
            sev_header,
            text=f"+{self.hyperopia_severity:.1f}D",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=COLORS['danger']
        )
        self.severity_label.pack(side="right")

        style = ttk.Style()
        style.configure("Custom.Horizontal.TScale", sliderlength=40)

        self.severity_scale = ttk.Scale(
            sev_container,
            from_=0,
            to=10,
            orient="horizontal",
            command=self.on_severity_change,
            style="Custom.Horizontal.TScale"
        )
        self.severity_scale.set(self.hyperopia_severity)
        self.severity_scale.pack(fill="x", pady=(10, 0))

        # Correction
        corr_container = tk.Frame(control_panel, bg="white")
        corr_container.pack(fill="x", padx=20, pady=(20, 10))

        corr_header = tk.Frame(corr_container, bg="white")
        corr_header.pack(fill="x")

        tk.Label(
            corr_header,
            text="CORRECTIVE LENS POWER",
            font=("Arial", 14, "bold"),
            bg="white",
            fg=COLORS['success']
        ).pack(side="left")

        self.correction_label = tk.Label(
            corr_header,
            text=f"{self.lens_correction*100:.0f}%",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=COLORS['success']
        )
        self.correction_label.pack(side="right")

        self.correction_scale = ttk.Scale(
            corr_container,
            from_=0,
            to=1,
            orient="horizontal",
            command=self.on_correction_change,
            style="Custom.Horizontal.TScale"
        )
        self.correction_scale.set(self.lens_correction)
        self.correction_scale.pack(fill="x", pady=(10, 0))

        # Modern action buttons
        btn_container = tk.Frame(control_panel, bg="white")
        btn_container.pack(pady=20)

        self.auto_btn = tk.Button(
            btn_container,
            text="AUTO CORRECT VISION",
            font=("Arial", 13, "bold"),
            bg=COLORS['success'],
            fg="white",
            bd=0,
            padx=30,
            pady=15,
            cursor="hand2",
            command=self.toggle_auto_correction,
            relief="raised",
            activebackground=COLORS['success_light']
        )
        self.auto_btn.pack(side="left", padx=8)

        tk.Button(
            btn_container,
            text="RESET ALL",
            font=("Arial", 13, "bold"),
            bg=COLORS['medium_gray'],
            fg="white",
            bd=0,
            padx=30,
            pady=15,
            cursor="hand2",
            command=self.reset_simulation,
            relief="raised",
            activebackground="#9ca3af"
        ).pack(side="left", padx=8)

        # Metrics
        self.metrics = ModernMetricsDashboard(control_panel)
        self.metrics.pack(fill="x", padx=15, pady=(10, 20))

    def change_pattern(self, pattern):
        self.current_pattern = pattern
        self.update_visualization()

    def on_severity_change(self, value):
        self.hyperopia_severity = float(value)
        self.severity_label.config(text=f"+{self.hyperopia_severity:.1f}D")
        self.update_visualization()

    def on_correction_change(self, value):
        self.lens_correction = float(value)
        self.correction_label.config(text=f"{self.lens_correction*100:.0f}%")
        self.update_visualization()

    def update_visualization(self):
        base_img = self.patterns[self.current_pattern]

        # Left: Uncorrected
        blurred = apply_hyperopia_blur(base_img, self.hyperopia_severity)
        self.current_display_left = ImageTk.PhotoImage(blurred)
        self.left_canvas.delete("all")
        self.left_canvas.create_image(
            DISPLAY_W // 2,
            DISPLAY_H // 2,
            image=self.current_display_left
        )

        blur_level = self.hyperopia_severity
        if blur_level < 1:
            left_text = "Mild Blur"
            left_color = COLORS['warning']
        elif blur_level < 4:
            left_text = "Moderate Blur"
            left_color = COLORS['warning']
        else:
            left_text = "Severe Blur"
            left_color = COLORS['danger']
        self.left_status.config(text=left_text, fg=left_color)

        # Right: Corrected
        corrected = apply_lens_correction(blurred, base_img, self.lens_correction)
        self.current_display_right = ImageTk.PhotoImage(corrected)
        self.right_canvas.delete("all")
        self.right_canvas.create_image(
            DISPLAY_W // 2,
            DISPLAY_H // 2,
            image=self.current_display_right
        )

        if self.lens_correction < 0.2:
            right_text = "No Correction"
            right_color = COLORS['danger']
        elif self.lens_correction < 0.7:
            right_text = "Partial Correction"
            right_color = COLORS['warning']
        else:
            right_text = "Crystal Clear"
            right_color = COLORS['success']
        self.right_status.config(text=right_text, fg=right_color)

        # Update anatomy
        self.eye_anatomy.draw_anatomy(self.hyperopia_severity, self.lens_correction)

        # Update metrics
        self.metrics.update(self.hyperopia_severity, self.lens_correction)

    def toggle_particles(self):
        if self.particle_var.get():
            self.eye_anatomy.start_particle_animation()
        else:
            self.eye_anatomy.stop_particle_animation()

    def toggle_auto_correction(self):
        if self.auto_correcting:
            self.auto_correcting = False
            self.auto_btn.config(text="AUTO CORRECT VISION", bg=COLORS['success'])
        else:
            self.auto_correcting = True
            self.auto_btn.config(text="PAUSE CORRECTION", bg=COLORS['warning'])
            self.animate_correction()

    def animate_correction(self):
        if not self.auto_correcting:
            return

        if self.lens_correction < 1.0:
            self.lens_correction = min(1.0, self.lens_correction + 0.015)
            self.correction_scale.set(self.lens_correction)
            self.correction_label.config(text=f"{self.lens_correction*100:.0f}%")
            self.update_visualization()
            self.root.after(25, self.animate_correction)
        else:
            self.auto_correcting = False
            self.auto_btn.config(text="AUTO CORRECT VISION", bg=COLORS['success'])

    def reset_simulation(self):
        self.auto_correcting = False
        self.lens_correction = 0.0
        self.hyperopia_severity = 6.0

        self.correction_scale.set(0)
        self.severity_scale.set(6)
        self.auto_btn.config(text="AUTO CORRECT VISION", bg=COLORS['success'])

        self.update_visualization()

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    root = tk.Tk()

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = UltimateHyperopiaSimulator(root)
    app.eye_anatomy.start_particle_animation()

    root.mainloop()

