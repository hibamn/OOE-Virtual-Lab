# 🔬 OOE VIRTUAL LABORATORY: OPTICAL & EM SYSTEMS
**Institution:** National Higher School of Advanced Technologies (ENSTA)  
**Module:** Physics / Computer Vision  
**Academic Year:** 2025–2026  
**Supervisor:** Dr. CHEGGOU Rabéa  

---

## 👥 TEAM IDENTIFICATION
- **Project Leader:** MESSAHLI Hiba Manel
- **Group Number:** G4
- **Team Members:**
  1. HAMMADI Nibel
  2. RAKI Meriem
  3. BENDAHMANE Reham
  4. TAKELAIT Amani
  5. BOUHEROUA Imane

---
## 📌 Project Overview

This project contains two physics simulations:

1. **The Microfilm Projector**: A converging lens system that projects a microfilm onto a wall using the thin-lens equation and transverse magnification.
2. **Atmospheric Mirages**: A numerical ray-tracing simulation of inferior (desert) and superior (Fata Morgana) mirages using RK4 integration.

---

## 📐 Physics Formulas Used

### 🔷 The Microfilm Projector

**Optical Power and Focal Length:**
$$P = \frac{1}{f} \quad \Rightarrow \quad f = \frac{1}{P} = \frac{1}{10} = 0.10 \text{ m} = 10 \text{ cm}$$

**Thin-Lens Equation (Gaussian form):**
$$\frac{1}{OA'} - \frac{1}{OA} = \frac{1}{f}$$

**Transverse Magnification:**
$$M = \frac{A'B'}{AB} = \frac{OA'}{OA} \approx -14$$

**Results:**
- Object distance: $OA = -10.71 \text{ cm}$
- Magnification: $M \approx -14$ (inverted, enlarged)
- Image height: $|A'B'| \approx 28 \text{ cm}$

---

### 🔷 Atmospheric Mirages – Ray Tracing

**Snell's Law (at each atmospheric layer):**
$$n_1 \sin\theta_1 = n_2 \sin\theta_2$$

**Layered Medium Invariant:**
$$n(y)\sin\psi = \text{constant}$$

**Ray Propagation Equations (from Fermat's Principle):**
$$\frac{dx}{ds} = v_x, \quad \frac{dy}{ds} = v_y$$

$$\frac{dv_x}{ds} = -\frac{v_y v_x}{n}\frac{dn}{dy}, \quad \frac{dv_y}{ds} = \frac{v_x^2}{n}\frac{dn}{dy}$$

**Desert Atmosphere Model (Inferior Mirage):**
$$n(y) = n_{\text{base}} - \Delta n \cdot e^{-y/H}$$

**Ocean Atmosphere Model (Superior Mirage / Fata Morgana):**
$$n(y) = n_{\text{base}} + A \cdot e^{-y/h_1} - B \cdot e^{-y/h_2}$$

**Phase Velocity:**
$$v = \frac{c}{n}$$

---

### 🔬 Simulation 1 — The Microfilm Projector (`lens_sim.py`)

![Microfilm Projector Screenshot](microfilm_projector.png)

This simulation models a converging lens system that projects a microfilm onto a wall placed **1.50 m** from the lens — exactly the setup described in Track 3.

**What it shows:**
- A real-time ray diagram with the object (microfilm), the converging lens, focal points F and 2F, and the projected image
- Whether the image is **in focus** (green) or **blurry** (red) relative to the target wall
- The image orientation: **upright or inverted**

**Controls:**
| Slider | What it does |
|---|---|
| Focal Length (f) | Changes the lens power |
| Object Distance (d₀) | Moves the microfilm closer or farther from the lens |
| Object Height (h₀) | Changes the size of the microfilm |

**Buttons:**
- **AUTO-FOCUS** → Automatically calculates and sets the exact object distance needed to project a sharp image on the wall
- **INVERT MICROFILM** → Flips the microfilm upside down (required in practice since M < 0)
- **SOLVE EXERCISE (Q1–Q4)** → Displays the full step-by-step solution to the Track 3 mission (focal length, object distance, magnification, image height)
- **RESET SYSTEM** → Returns all sliders to default values

**Key physics demonstrated:**
$$f = \frac{1}{P} = \frac{1}{10} = 0.10 \text{ m}, \quad OA = -10.71 \text{ cm}, \quad M \approx -14, \quad |A'B'| \approx 28 \text{ cm}$$

---

### 👁️ Simulation 2 — Hyperopia Correction Simulator (`Hyperopia_Correction.py`)

![Hyperopia Correction Screenshot](hyperopia_correction.png)

This simulation applies the **same thin-lens physics** to a real-world medical problem: correcting farsightedness (hyperopia) using a converging lens (glasses).

**What it shows:**
- **Left panel (red):** Uncorrected vision — the image forms *behind* the retina, causing blur. The blur intensity increases with hyperopia severity.
- **Right panel (green):** Corrected vision — a converging lens shifts the focus forward onto the retina, restoring a sharp image.
- **Bottom-left:** Optical path diagram showing how rays converge with and without the corrective lens.
- **Bottom-right:** A vision test chart (Snellen, Reading, Contrast, Astigmatism) that reacts in real time to the correction level.

**Controls:**
| Slider | What it does |
|---|---|
| Hyperopia Severity | Simulates how far behind the retina the focus falls (in diopters) |
| Corrective Lens Power | Adds optical power to shift the image forward onto the retina |

**Connection to Track 3 physics:**

Both simulations use the same fundamental equations:

$$\frac{1}{d_o} + \frac{1}{d_i} = \frac{1}{f}, \qquad m = -\frac{d_i}{d_o}, \qquad P = \frac{1}{f}$$

In the projector, we move the image **far away** onto a wall. In hyperopia correction, we move the image **forward** onto the retina. Same lens equation, two different real-world applications.

---

## ▶️ How to Run the Simulations

**Requirements:** Python 3.x with `tkinter` (included by default in most Python installations)
```bash
# Microfilm Projector
python lens_sim.py

# Hyperopia Correction
python Hyperopia_Correction.py
```

---
