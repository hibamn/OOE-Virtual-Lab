import tkinter as tk
from tkinter import messagebox, ttk
import math

COLORS = {
    "bg_dark": "#0a0a0c",
    "bg_sidebar": "#121216",
    "bg_panel": "#1b1b22",
    "accent": "#00f0ff",
    "accent_glow": "#0099ff",
    "success": "#00ff9d",
    "warning": "#ffbd2e",
    "danger": "#ff4d4d",
    "text_main": "#e1e1e6",
    "text_dim": "#a1a1aa",
    "ray_p": "#fff200",
    "ray_c": "#ff1ff0",
    "ray_f": "#00ff9d",
}

class LensPhysics:
    def __init__(self, target_di=1.50, tolerance=0.02):
        self.target_di = target_di
        self.tolerance = tolerance

    def calculate(self, f, do, ho):
        if f <= 0:
            return {"error": "Invalid focal length (f ≤ 0)"}
        if do <= f:
            return {"error": "Virtual Image (d₀ ≤ f)"}
        try:
            di = 1.0 / (1.0 / f - 1.0 / do)
            mag = -di / do
            hi = mag * ho
            error = abs(di - self.target_di)
            is_focused = error < self.tolerance
            return {"f": f, "do": do, "ho": ho, "di": di, "mag": mag, "hi": hi, "error_m": error, "is_focused": is_focused, "success": True}
        except ZeroDivisionError:
            return {"error": "Calculation Error"}

class CustomSlider(tk.Frame):
    def __init__(self, parent, label, min_val, max_val, start_val, callback):
        super().__init__(parent, bg=COLORS["bg_sidebar"], pady=12)
        self.callback = callback
        top_frame = tk.Frame(self, bg=COLORS["bg_sidebar"])
        top_frame.pack(fill=tk.X)
        tk.Label(top_frame, text=label, font=("Inter", 10, "bold"), fg=COLORS["text_dim"], bg=COLORS["bg_sidebar"]).pack(side=tk.LEFT)
        self.val_label = tk.Label(top_frame, text=f"{start_val:.2f} m", font=("JetBrains Mono", 10, "bold"), fg=COLORS["accent"], bg=COLORS["bg_sidebar"])
        self.val_label.pack(side=tk.RIGHT)
        self.var = tk.DoubleVar(value=start_val)
        self.scale = tk.Scale(self, from_=min_val, to=max_val, orient=tk.HORIZONTAL, resolution=0.01, variable=self.var, command=self._on_change, bg=COLORS["bg_sidebar"], fg=COLORS["accent"], troughcolor=COLORS["bg_panel"], activebackground=COLORS["accent"], highlightthickness=0, bd=0, showvalue=False, cursor="hand2")
        self.scale.pack(fill=tk.X, pady=(5, 0))

    def _on_change(self, val):
        self.val_label.config(text=f"{float(val):.2f} m")
        self.callback()

    def get(self):
        return self.var.get()

    def set(self, val):
        self.var.set(val)
        self.val_label.config(text=f"{val:.2f} m")

class LensCanvas(tk.Canvas):
    def __init__(self, parent, owner):
        super().__init__(parent, bg=COLORS["bg_dark"], highlightthickness=0)
        self.owner = owner
        self.scale_factor = 250
        self.bind("<Configure>", lambda e: self.owner.refresh())

    def draw_system(self, data, target_dist):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 100 or h < 100:
            return
        cx, cy = w / 2, h / 2
        for i in range(0, w, 50):
            self.create_line(i, 0, i, h, fill="#1a1a22", width=1)
        for i in range(0, h, 50):
            self.create_line(0, i, w, i, fill="#1a1a22", width=1)
        self.create_line(0, cy, w, cy, fill="#ffffff", width=2, dash=(10, 10))
        tx = cx + target_dist * self.scale_factor
        self.create_line(tx, cy - 150, tx, cy + 150, fill=COLORS["danger"], width=2)
        self.create_text(tx, cy - 170, text=f"TARGET: {target_dist:.2f}m", fill=COLORS["danger"], font=("Inter", 9, "bold"))
        self._draw_lens(cx, cy)
        if "error" in data:
            do = self.owner.do_slider.get()
            ho = self.owner.ho_slider.get()
            ox, oy = cx - do * self.scale_factor, cy
            oh = ho * self.scale_factor
            self._draw_object(ox, oy, oh)
            self._draw_error_msg(w, h, data["error"])
            return
        f, do, ho = data["f"], data["do"], data["ho"]
        di, hi = data["di"], data["hi"]
        ox, oy = cx - do * self.scale_factor, cy
        ix, iy = cx + di * self.scale_factor, cy
        oh = ho * self.scale_factor
        ih = hi * self.scale_factor
        self._draw_points(cx, cy, f)
        self._draw_object(ox, oy, oh)
        self._draw_image(ix, iy, ih, data["is_focused"])
        self._draw_rays(ox, oy, oh, cx, ix, iy, ih, f)

    def _draw_lens(self, x, y):
        lh = 220
        self.create_oval(x - 20, y - lh, x + 20, y + lh, fill="#1a3a4a", outline=COLORS["accent"], width=2)
        self.create_line(x, y - lh - 20, x, y + lh + 20, fill=COLORS["accent"], width=1, dash=(5, 5))
        self.create_text(x, y - lh - 40, text="CONVERGING LENS", fill=COLORS["accent"], font=("Inter", 10, "bold"))

    def _draw_points(self, cx, cy, f):
        for s in [-1, 1]:
            fx = cx + s * f * self.scale_factor
            self.create_oval(fx - 6, cy - 6, fx + 6, cy + 6, fill=COLORS["accent"], outline="white")
            self.create_text(fx, cy + 25, text="F", fill=COLORS["accent"], font=("JetBrains Mono", 10, "bold"))
            f2x = cx + s * 2 * f * self.scale_factor
            self.create_oval(f2x - 4, cy - 4, f2x + 4, cy + 4, fill=COLORS["accent_glow"], outline="white")
            self.create_text(f2x, cy + 25, text="2F", fill=COLORS["accent_glow"], font=("JetBrains Mono", 9))

    def _draw_object(self, x, y, h):
        self.create_line(x, y, x, y - h, fill=COLORS["success"], width=6, arrow=tk.LAST, arrowshape=(10, 12, 5))
        status = "OBJECT (AB)" if h >= 0 else "OBJECT (AB) [INVERTED]"
        self.create_text(x, y + 40, text=status, fill=COLORS["success"], font=("Inter", 9, "bold"))

    def _draw_image(self, x, y, h, focused):
        color = COLORS["success"] if focused else COLORS["danger"]
        dash_p = (5, 2) if not focused else None
        self.create_line(x, y, x, y - h, fill=color, width=6, arrow=tk.LAST, arrowshape=(10, 12, 5), dash=dash_p)
        orient = "UPRIGHT" if h >= 0 else "INVERTED"
        status = "IN FOCUS" if focused else "BLURRY"
        self.create_text(x, y + 40, text=f"IMAGE\n({status})\n{orient}", fill=color, font=("Inter", 9, "bold"), justify=tk.CENTER)

    def _draw_rays(self, ox, oy, oh, cx, ix, iy, ih, f):
        self.create_line(ox, oy - oh, cx, oy - oh, fill=COLORS["ray_p"], width=2)
        self.create_line(cx, oy - oh, ix, iy - ih, fill=COLORS["ray_p"], width=2, arrow=tk.LAST)
        self.create_line(ox, oy - oh, ix, iy - ih, fill=COLORS["ray_c"], width=2, dash=(10, 5))

    def _draw_error_msg(self, w, h, msg):
        self.create_text(w / 2, h - 100, text=msg, fill=COLORS["danger"], font=("Inter", 14, "bold"))

class LensApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The Microfilm Projector")
        self.root.geometry("1400x850")
        self.root.configure(bg=COLORS["bg_dark"])
        self.physics = LensPhysics()
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        self.sidebar = tk.Frame(self.root, bg=COLORS["bg_sidebar"], width=350)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        header = tk.Frame(self.sidebar, bg=COLORS["bg_panel"], height=80)
        header.pack(fill=tk.X)
        tk.Label(header, text="OPTIC LAB", font=("Inter", 18, "bold"), fg=COLORS["accent"], bg=COLORS["bg_panel"]).place(relx=0.5, rely=0.5, anchor="center")
        controls = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], padx=25, pady=25)
        controls.pack(fill=tk.BOTH, expand=True)
        self.f_slider = CustomSlider(controls, "Focal Length (f)", 0.1, 1.2, 0.45, self.refresh)
        self.f_slider.pack(fill=tk.X)
        self.do_slider = CustomSlider(controls, "Obj. Distance (d₀)", 0.1, 2.0, 0.85, self.refresh)
        self.do_slider.pack(fill=tk.X)
        self.ho_slider = CustomSlider(controls, "Obj. Height (h₀)", -0.25, 0.25, 0.12, self.refresh)
        self.ho_slider.pack(fill=tk.X)
        btn_frame = tk.Frame(controls, bg=COLORS["bg_sidebar"], pady=20)
        btn_frame.pack(fill=tk.X)
        ttk.Style().configure("TButton", font=("Inter", 10, "bold"))
        self.focus_btn = tk.Button(btn_frame, text="AUTO-FOCUS", command=self.auto_focus, bg=COLORS["accent"], fg="black", font=("Inter", 11, "bold"), bd=0, height=2, cursor="hand2")
        self.focus_btn.pack(fill=tk.X, pady=5)
        self.invert_btn = tk.Button(btn_frame, text="INVERT MICROFILM", command=self.invert_microfilm, bg=COLORS["bg_panel"], fg=COLORS["text_main"], font=("Inter", 10, "bold"), bd=0, height=2, cursor="hand2", activebackground=COLORS["accent_glow"])
        self.invert_btn.pack(fill=tk.X, pady=5)
        self.solve_btn = tk.Button(btn_frame, text="SOLVE EXERCISE (Q1–Q4)", command=self.solve_exercise, bg=COLORS["warning"], fg="black", font=("Inter", 10, "bold"), bd=0, height=2, cursor="hand2", activebackground=COLORS["accent_glow"])
        self.solve_btn.pack(fill=tk.X, pady=5)
        self.reset_btn = tk.Button(btn_frame, text="RESET SYSTEM", command=self.reset, bg=COLORS["bg_panel"], fg=COLORS["text_dim"], font=("Inter", 10), bd=0, height=1, cursor="hand2")
        self.reset_btn.pack(fill=tk.X, pady=5)
        self.status_panel = tk.Frame(controls, bg=COLORS["bg_panel"], padx=15, pady=15, bd=1, relief="solid")
        self.status_panel.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_title = tk.Label(self.status_panel, text="SYSTEM STATUS", font=("Inter", 8, "bold"), fg=COLORS["text_dim"], bg=COLORS["bg_panel"])
        self.status_title.pack(anchor="w")
        self.status_msg = tk.Label(self.status_panel, text="READY", font=("JetBrains Mono", 11, "bold"), fg=COLORS["accent"], bg=COLORS["bg_panel"], pady=5, justify="left")
        self.status_msg.pack(anchor="w")
        self.canvas = LensCanvas(self.root, self)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def refresh(self, *args):
        f = self.f_slider.get()
        do = self.do_slider.get()
        ho = self.ho_slider.get()
        data = self.physics.calculate(f, do, ho)
        self.canvas.draw_system(data, self.physics.target_di)
        self._update_status(data)

    def _update_status(self, data):
        if "error" in data:
            self.status_msg.config(text=data["error"], fg=COLORS["danger"])
        else:
            orient = "UPRIGHT" if data["mag"] > 0 else "INVERTED"
            txt = f"dᵢ: {data['di']:.3f}m\nMag: {data['mag']:.2f}x ({orient})"
            color = COLORS["success"] if data["is_focused"] else COLORS["warning"]
            self.status_msg.config(text=txt, fg=color)

    def invert_microfilm(self):
        self.ho_slider.set(-self.ho_slider.get())
        self.refresh()

    def auto_focus(self):
        f = self.f_slider.get()
        target = self.physics.target_di
        try:
            do_req = 1.0 / (1.0 / f - 1.0 / target)
            if 0.1 <= do_req <= 2.0:
                self.do_slider.set(do_req)
                self.refresh()
            else:
                messagebox.showwarning("Range Error", "Required distance out of slider bounds.")
        except Exception:
            messagebox.showerror("Math Error", "Cannot focus with current focal length.")

    def solve_exercise(self):
        P = 10.0
        f = 1.0 / P
        di = 1.50
        h0 = 0.020
        try:
            do = 1.0 / (1.0 / f - 1.0 / di)
        except ZeroDivisionError:
            messagebox.showerror("Math Error", "Impossible configuration (division by zero).")
            return
        m = -di / do
        hi = m * h0
        advice = "Insert the microfilm UPSIDE DOWN" if hi < 0 else "Insert the microfilm RIGHT-SIDE UP"
        in_bounds = (self.f_slider.scale.cget("from") <= f <= self.f_slider.scale.cget("to") and self.do_slider.scale.cget("from") <= do <= self.do_slider.scale.cget("to") and self.ho_slider.scale.cget("from") <= h0 <= self.ho_slider.scale.cget("to"))
        if in_bounds:
            self.f_slider.set(f)
            self.do_slider.set(do)
            self.ho_slider.set(h0)
            self.refresh()
        msg = (
            "Track 3 — Mission 3: Project the Blueprint\n\n"
            f"[Q1] P = +{P:.0f} D  →  f′ = {f:.3f} m = {f*100:.1f} cm\n\n"
            f"[Q2] With OA′ = +{di:.2f} m, the required OA (object distance) is:\n"
            f"     OA = {do:.4f} m\n\n"
            f"[Q3] Magnification γ = {m:.3f}\n\n"
            f"[Q4] A′B′ = γ·AB = {hi*100:.2f} cm  ({'inverted' if hi < 0 else 'upright'})\n"
            f"     {advice}\n"
        )
        messagebox.showinfo("Solved (Q1–Q4)", msg)

    def reset(self):
        self.f_slider.set(0.45)
        self.do_slider.set(0.85)
        self.ho_slider.set(0.12)
        self.refresh()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = LensApp(root)
    root.mainloop()
