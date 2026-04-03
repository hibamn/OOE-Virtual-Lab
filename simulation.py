import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

class AcousticTriangulationSim:
    """
    Simulation environment for NANO-PHONONICS Acoustic Triangulation (Track 3).
    Demonstrates TDOA (Time Difference of Arrival) methodology for tracking
    keystrokes on a solid plate based on mechanical wave propagation.
    """
    
    def __init__(self):
        self._init_physics_parameters()
        self._init_geometry()
        self._init_state()
        self._init_ui()
        self._bind_events()
        
        # Start initial simulation
        self.simulate_press(self.pressed_key)

   
    
    def _init_physics_parameters(self):
        """Initialize physical and mathematical constants."""
        self.vg = 600.0       # Wave group velocity in plate (m/s)
        self.noise_std = 4e-6 # Sensor measurement noise standard deviation (s)
        self.grid_res = 220   # Resolution for the vectorized TDOA search grid
        np.random.seed(42)

    def _init_geometry(self):
        """Define keyboard layout, sensor coordinates, and simulation boundaries."""
        self.pitch = 0.01905
        self.key_w = 0.017
        self.key_h = 0.017

        rows = [
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM")
        ]
        row_offsets = [0.0, 0.5 * self.pitch, 1.0 * self.pitch]

        self.key_positions = {}
        self.all_keys = []
        
        for r, row in enumerate(rows):
            y = (len(rows) - 1 - r) * self.pitch
            for i, ch in enumerate(row):
                x = row_offsets[r] + i * self.pitch
                p = np.array([x, y])
                self.key_positions[ch] = p
                self.all_keys.append((ch, x, y))

        # Calculate plate boundaries based on key extent
        xs = [p[0] for p in self.key_positions.values()]
        ys = [p[1] for p in self.key_positions.values()]
        self.xmin, self.xmax = min(xs) - 0.03, max(xs) + 0.03
        self.ymin, self.ymax = min(ys) - 0.03, max(ys) + 0.035

        # Place 4 sensors near the corners of the plate
        self.sensors = np.array([
            [self.xmin + 0.008, self.ymin + 0.008],
            [self.xmax - 0.008, self.ymin + 0.008],
            [self.xmin + 0.008, self.ymax - 0.008],
            [self.xmax - 0.008, self.ymax - 0.008]
        ])

    def _init_state(self):
        """Initialize variables used during active simulation."""
        self.pressed_key = "G"
        self.true_source = self.key_positions[self.pressed_key].copy()
        
        self.estimated_source = self.true_source.copy()
        self.estimated_key = self.pressed_key
        
        self.arrival_times = np.zeros(4)
        self.tdoa = np.zeros(4)
        
        self.heatmap = None
        self.sensor_texts = []
        self.circles = []
        self.anim_frame = 0

    

    def _init_ui(self):
        """Construct the 'Command Center' UI layout."""
        # Color Palette
        self.colors = {
            'bg': '#0b0f19',
            'panel': '#151b2b',
            'text': '#a5b4fc',
            'highlight': '#38bdf8',
            'error': '#fb7185',
            'success': '#4ade80',
            'grid': '#334155'
        }

        self.fig = plt.figure(figsize=(15, 8.5))
        self.fig.patch.set_facecolor(self.colors['bg'])
        
        gs = self.fig.add_gridspec(1, 2, width_ratios=[2.4, 1.0], wspace=0.1)
        
        self._setup_main_plot(gs[0])
        self._setup_sidebar_panels(gs[1])
        
        plt.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=0.07)
        self.ani = FuncAnimation(self.fig, self._update_anim, interval=60, blit=False)

    def _setup_main_plot(self, gs_area):
        """Setup the primary interactive plate map."""
        self.ax = self.fig.add_subplot(gs_area)
        self.ax.set_facecolor('#000000') 
        self.ax.set_xlim(self.xmin, self.xmax)
        self.ax.set_ylim(self.ymin, self.ymax)
        self.ax.set_aspect("equal")
        self.ax.set_title("NANO-PHONONICS ACOUSTIC TRACKING (TDOA)", 
                          color=self.colors['highlight'], fontweight='bold', fontsize=14, pad=15)
        self.ax.set_xlabel("Plate X Coordinates (m)", color=self.colors['text'])
        self.ax.set_ylabel("Plate Y Coordinates (m)", color=self.colors['text'])
        self.ax.tick_params(colors=self.colors['text'])
        
        self.ax.grid(True, alpha=0.15, color=self.colors['highlight'])
        for spine in self.ax.spines.values():
            spine.set_color(self.colors['grid'])

        self._draw_keyboard()
        self._draw_sensors()

        # Target marker
        self.true_marker, = self.ax.plot(
            [], [], "+", color=self.colors['success'], 
            markersize=20, mew=3, label="Triangulated Origin", zorder=6
        )
        
        # Propagation animation rings
        for i in range(5):
            c = Circle((0, 0), 0.01, fill=False, lw=2.5, 
                       edgecolor=self.colors['highlight'], alpha=0.0, zorder=4)
            self.ax.add_patch(c)
            self.circles.append(c)

        self.ax.legend(loc="upper left", facecolor=f"{self.colors['bg']}aa", 
                       edgecolor=self.colors['grid'], labelcolor='white')

    def _draw_keyboard(self):
        """Draw the keyboard layout onto the main plot."""
        self.key_patches = {}
        for ch, x, y in self.all_keys:
            rect = Rectangle(
                (x - self.key_w / 2, y - self.key_h / 2),
                self.key_w, self.key_h,
                facecolor=f"{self.colors['highlight']}11", 
                edgecolor=f"{self.colors['highlight']}44",
                linewidth=1.2,
                zorder=3
            )
            self.ax.add_patch(rect)
            self.ax.text(x, y, ch, ha="center", va="center", 
                         color='#94a3b8', fontweight="bold", fontsize=10, zorder=4)
            self.key_patches[ch] = rect

    def _draw_sensors(self):
        """Draw the acoustic sensors onto the main plot."""
        for i, s in enumerate(self.sensors):
            # Outer ring
            self.ax.plot(s[0], s[1], "o", color='#fff', markersize=9, 
                         markeredgecolor=self.colors['highlight'], markeredgewidth=2, zorder=5)
            # Center glow
            self.ax.plot(s[0], s[1], "o", color=self.colors['highlight'], 
                         markersize=14, alpha=0.3, zorder=5) 
            txt = self.ax.text(s[0], s[1] - 0.008, f"S{i+1}", 
                               color="white", fontsize=10, ha='center', fontweight='bold', zorder=5)
            self.sensor_texts.append(txt)

    def _setup_sidebar_panels(self, gs_area):
        """Setup the text panels for metrics and results."""
        self.ax_info = self.fig.add_subplot(gs_area)
        self.ax_info.axis('off')

        self.text_telemetry = self.ax_info.text(
            0.0, 0.98, "", fontsize=10.5, family='monospace', color=self.colors['text'], va='top',
            bbox=dict(boxstyle="square,pad=1.0", facecolor=self.colors['panel'], 
                      edgecolor=self.colors['grid'], linewidth=1.5)
        )
        
        self.text_decoder = self.ax_info.text(
            0.0, 0.58, "", fontsize=12, family='monospace', color=self.colors['success'], va='top',
            bbox=dict(boxstyle="square,pad=1.2", facecolor=f"{self.colors['success']}11", 
                      edgecolor=self.colors['success'], linewidth=2.0)
        )

       
        
        theory_text = (
            "MATHEMATICAL THEORY:\n"
            r"$\Delta d_{i} = v_g \cdot \Delta t_{i}$" + "\n"
            r"$E(x,y) = \sum_{i} \left( \frac{|| \vec{S}_i - \vec{p} ||}{v_g} - \Delta t_{meas, i} \right)^2$"
        )
        self.ax_info.text(
            0.0, 0.05, theory_text, fontsize=11.5, color='#94a3b8', va='top'
        )

    
    def _bind_events(self):
        """Map user interaction keys and mouse clicks to simulation events."""
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.fig.canvas.mpl_connect("button_press_event", self._on_click)

    def _on_key(self, event):
        if event.key is None: return
        k = event.key.upper()
        if len(k) == 1 and k in self.key_positions:
            self.simulate_press(k)

    def _on_click(self, event):
        if event.inaxes != self.ax: return
        for ch, patch in self.key_patches.items():
            if patch.contains(event)[0]:
                self.simulate_press(ch)
                break

    
    def _dists(self, origin, targets):
        """Calculate euclidean distances from origin point to multiple target points."""
        return np.sqrt(((targets - origin) ** 2).sum(axis=1))

    def _get_nearest_key(self, p):
        """Find the closest keyboard key location to a given physical coordinate."""
        best_k = None
        best_d = 1e9
        for k, pos in self.key_positions.items():
            d = np.linalg.norm(p - pos)
            if d < best_d:
                best_d = d
                best_k = k
        return best_k, best_d

    def _compute_tdoa_field(self, tdoa_measured):
        """
        Calculates the error surface for all points in the space simultaneously using grid broadcasting.
        """
        xs = np.linspace(self.xmin, self.xmax, self.grid_res)
        ys = np.linspace(self.ymin, self.ymax, self.grid_res)
        X, Y = np.meshgrid(xs, ys)
        
        # Grid shape: (res, res, 2)
        grid = np.stack((X, Y), axis=-1)
        
        # Distances to each sensor from each grid point: shape (res, res, 4)
        dists = np.linalg.norm(grid[:, :, None, :] - self.sensors[None, None, :, :], axis=-1)
        times = dists / self.vg
        
        # Model Time Difference of Arrival
        model_tdoa = times - times[:, :, 0:1]
        
        # Least squares error against measured TDOA
        errors = np.sum((model_tdoa - tdoa_measured[None, None, :])**2, axis=-1)
        errors += 1e-15 # numerical stability to prevent division by zero in log scales
        
        # Locate global minimum
        min_idx = np.unravel_index(np.argmin(errors), errors.shape)
        best_p = np.array([xs[min_idx[1]], ys[min_idx[0]]])
        best_err = errors[min_idx]
        
        return best_p, best_err, errors


    def simulate_press(self, key):
        """Execute a full simulation cycle: physical impact -> signal capture -> triangulation -> render."""
        if key not in self.key_positions:
            return

        self.pressed_key = key
        self.true_source = self.key_positions[key].copy()

        # 1. Physical Wave Propagation
        d = self._dists(self.true_source, self.sensors)
        t_true = d / self.vg
        
        # 2. Add atmospheric / hardware noise
        noise = np.random.normal(0, self.noise_std, size=t_true.shape)
        self.arrival_times = t_true + noise
        self.tdoa = self.arrival_times - self.arrival_times[0]

        # 3. Sensor Acquisition & TDOA Estimation (Vectorized for Heatmap generation)
        self.estimated_source, best_err, errors_grid = self._compute_tdoa_field(self.tdoa)
        self.estimated_key, key_dist = self._get_nearest_key(self.estimated_source)

        # 4. Visual Rendering
        self._highlight_active_keys(self.estimated_key)
        self.true_marker.set_data([self.estimated_source[0]], [self.estimated_source[1]])
        self._render_heatmap(errors_grid)
        self._update_telemetry_texts(best_err, key_dist)

        # Restart wave animation
        self.anim_frame = 0
        self.fig.canvas.draw_idle()

    
    def _highlight_active_keys(self, target_key):
        """Visual effect to reset all keys and pulse the detected key."""
        for ch, patch in self.key_patches.items():
            patch.set_facecolor(f"{self.colors['highlight']}11")
            patch.set_edgecolor(f"{self.colors['highlight']}44")
            patch.set_linewidth(1.2)
            
        if target_key in self.key_patches:
            self.key_patches[target_key].set_facecolor(f"{self.colors['success']}55")
            self.key_patches[target_key].set_edgecolor(self.colors['success'])
            self.key_patches[target_key].set_linewidth(3.0)

    def _render_heatmap(self, errors_grid):
        """Draw or update the background TDOA error field visualization."""
        if self.heatmap is None:
            self.heatmap = self.ax.imshow(
                errors_grid, 
                extent=[self.xmin, self.xmax, self.ymin, self.ymax], 
                origin='lower', 
                cmap='inferno_r', # Bright spot points to origin
                alpha=0.6, 
                zorder=2,
                norm=mcolors.LogNorm(vmin=errors_grid.min(), vmax=errors_grid.max())
            )
        else:
            self.heatmap.set_data(errors_grid)
            self.heatmap.set_norm(mcolors.LogNorm(vmin=errors_grid.min(), vmax=errors_grid.max()))

    def _update_telemetry_texts(self, best_err, key_dist):
        """Update side-panels with specific metric readings."""
        telemetry = (
            "--- TRACKING TELEMETRY (TDOA) ---\n\n"
            f"V-Prop Constant  : {self.vg} m/s\n"
            f"Sensor Noise Std : {self.noise_std*1e6:.1f} µs\n\n"
            f"Intercepted TDOA wrt Sensor 1:\n"
            f"  S1: 0.0 µs\n"
            f"  S2: {self.tdoa[1]*1e6:+.2f} µs\n"
            f"  S3: {self.tdoa[2]*1e6:+.2f} µs\n"
            f"  S4: {self.tdoa[3]*1e6:+.2f} µs\n\n"
            "--- CALCULATION RESULTS ---\n\n"
            f"Grid Error Min   : {best_err:.2e}\n"
            f"Est. Coordinates : x={self.estimated_source[0]:.4f}\n"
            f"                   y={self.estimated_source[1]:.4f}\n"
            f"Nearest Key Node : {self.estimated_key} (Dist: {key_dist*1000:.1f}mm)"
        )
        self.text_telemetry.set_text(telemetry)

        decoder = (
            "--- DECODED OUTPUT ---\n\n"
            f"KEY NODE    :  '{self.estimated_key}'\n\n"
            f"RECON HEX   :   0x{ord(self.estimated_key):02X}\n\n"
            f"RECON BINARY:   0b{ord(self.estimated_key):08b}"
        )
        self.text_decoder.set_text(decoder)

    def _update_anim(self, frame):
        """Frame-by-frame mechanical wave propagation visual logic."""
        self.anim_frame += 1
        base = 0.000
        step = 0.002
        for i, c in enumerate(self.circles):
            c.center = (self.estimated_source[0], self.estimated_source[1])
            radius = base + (self.anim_frame % 28) * step + i * 0.008
            c.radius = radius
            alpha_val = max(0.0, 0.7 - (radius * 12))
            c.set_alpha(alpha_val)
            c.set_edgecolor(self.colors['highlight'])
        return self.circles

def main():
    AcousticTriangulationSim()
    plt.show()

if __name__ == '__main__':
    main()