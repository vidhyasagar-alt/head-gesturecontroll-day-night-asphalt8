# 🎮 PRO Head + Hand Game Controller with Day / Night Mode

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> Control **Asphalt 8 Airborne** using your **head to steer** and **hand gestures for gas, nitro and brake** — with a built-in **Day / Night vision mode** you can switch without touching your keyboard!

---

## 🎬 Demo

📹 **Watch it in action:** *([watch demo video here](https://youtu.be/DEotcgTxWRM?si=ptNGMsBYmCRCgpFf))*

---

## ✨ What Makes This Project Unique

Most gesture controllers use only hands for everything. This project splits the controls smartly:

- 🧠 **Head** handles steering — left, right, straight
- ✋ **Hand** handles throttle — gas, nitro, brake
- 🌙 **Night vision pipeline** activates when night mode is ON — brightness boost, gamma correction and CLAHE so detection still works in dark rooms
- 🔄 **Mode switching** happens through held gestures — no keyboard needed at all

---

## 🕹️ Controls

### 🧠 HEAD — Steering

| Head Movement | Action | Key |
|---|---|---|
| Turn head LEFT past dead zone | Steer Left | ← Left Arrow |
| Turn head RIGHT past dead zone | Steer Right | → Right Arrow |
| Head within dead zone | Go Straight | — |

> 📌 On startup, hold your head straight for ~1.5 seconds. The green calibration bar fills up and locks your neutral position. Steering is always relative to YOUR locked neutral — never drifts. Press **R** anytime to recalibrate.

---

### ✋ HAND — Gas / Nitro / Brake

| Gesture | Action | Key |
|---|---|---|
| 🤚 Open hand (all fingers down) | Gas — accelerate | ↑ Up Arrow |
| ☝️ 1 finger up (index only) | Nitro boost | Space + ↑ |
| ✊ Fist (all fingers closed) | Brake | ↓ Down Arrow |
| 🚫 No hand visible | Auto pause game | Escape |
| 🤚 Hand reappears | Auto resume game | Escape |

---

### 🌗 HAND — Day / Night Mode Switch

| Gesture | Hold Duration | Result |
|---|---|---|
| ☝️ Hold **1 finger** (index only) | 1.5 seconds | ☀️ Switches to **DAY mode** |
| ✌️ Hold **2 fingers** (index + middle) | 1.5 seconds | 🌙 Switches to **NIGHT mode** |

> 💡 A yellow progress bar fills at the bottom of the screen while you hold the gesture. When it reaches full, the mode switches automatically. The current mode is always shown on the top left of the camera window.

---

## ☀️🌙 Day Mode vs Night Mode

| Feature | ☀️ Day Mode | 🌙 Night Mode |
|---|---|---|
| Camera feed | Normal | Enhanced |
| Brightness boost | Off | On |
| Gamma correction | Off | On (lifts dark shadows) |
| CLAHE contrast | Off | On (smart local contrast) |
| Noise reduction | Off | On (Gaussian blur) |
| Best for | Normal lighting | Dark rooms / low light |

---

## 🧠 How It Works

```
Webcam captures frame (320x240 for low latency)
        |
        v
Frame is flipped horizontally
        |
        v
If NIGHT MODE is ON:
  -> Brightness + contrast boost (alpha=1.8, beta=50)
  -> Gamma correction (lifts dark shadows)
  -> CLAHE on YUV Y-channel (smart local contrast)
  -> Gaussian blur (noise reduction)
        |
        v
Same enhanced frame sent to BOTH:
  -> MediaPipe Face Landmarker  ->  nose position  ->  HEAD STEERING
  -> MediaPipe Hand Landmarker  ->  finger gestures ->  GAS / NITRO / BRAKE
        |
        v
PyAutoGUI simulates keyboard inputs
        |
        v
🚗 Asphalt 8 responds in real time!
```

---

## 📐 Head Calibration System

The neutral head position is captured ONCE at startup over ~1.5 seconds (45 frames). The average nose X position is locked as the neutral point. After that:

- Nose moves **left of neutral by more than 6%** → steer left
- Nose moves **right of neutral by more than 6%** → steer right
- Within the **6% dead zone** → go straight

The neutral **NEVER drifts** after calibration. Press **R** to recalibrate anytime.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.8+ | Core language |
| OpenCV | Camera capture, night vision processing, HUD display |
| MediaPipe Face Landmarker | 478-point face mesh, nose tracking for steering |
| MediaPipe Hand Landmarker | 21-point hand landmarks for gesture detection |
| PyAutoGUI | Simulates keyboard inputs for game control |
| NumPy | Gamma correction lookup table, calibration averaging |
| keyboard | Quit and recalibrate key detection |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or above
- Webcam
- Asphalt 8 Airborne installed on PC (Windows)
- Download model files from MediaPipe:
  - [hand_landmarker.task](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)
  - [face_landmarker.task](https://developers.google.com/mediapipe/solutions/vision/face_landmarker)

### Step 1 — Clone the repository
```bash
git clone https://github.com/vidhyasagar-alt/night-vision-gesture-controller.git
cd night-vision-gesture-controller
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Set your model paths
Open `pronightvisioncontrol.py` and update these two lines:
```python
HAND_MODEL_PATH = r"D:\YOUR_PATH\hand_landmarker.task"
FACE_MODEL_PATH = r"D:\YOUR_PATH\face_landmarker.task"
```

### Step 4 — Run the controller
```bash
python pronightvisioncontrol.py
```

### Step 5 — Play! 🏁
1. Open **Asphalt 8 Airborne** on your PC
2. Run the script — the webcam window opens
3. Hold your head **straight** — wait for the green calibration bar to fill (~1.5 sec)
4. Once calibrated, **steer with your head** and **control throttle with your hand**
5. Hold 2 fingers for 1.5 sec to switch to **Night mode** if playing in a dark room
6. Start racing! 🚗💨

---

## 📦 Requirements

```
opencv-python
mediapipe
pyautogui
keyboard
numpy
```

---

## 📁 Project Structure

```
night-vision-gesture-controller/
|
|-- pronightvisioncontrol.py   # Main script - run this
|-- requirements.txt           # All required libraries
|-- README.md                  # Project documentation
```

> ⚠️ Download `hand_landmarker.task` and `face_landmarker.task` separately from MediaPipe and update their paths in the script.

---

## 🎯 Key Features

- ✅ Head-based steering with one-time calibration and fixed neutral (no drift)
- ✅ Hand-based gas, nitro and brake control
- ✅ Day / Night mode switch using held finger gestures — no keyboard needed
- ✅ Night vision pipeline: brightness boost, gamma correction, CLAHE, noise reduction
- ✅ Auto pause when hand leaves frame, auto resume when hand returns
- ✅ Real-time HUD showing current mode, steering direction and action
- ✅ Yellow progress bar shows mode switch progress
- ✅ Press R to recalibrate head neutral anytime
- ✅ Works with any PC game that uses arrow key controls

---

## 🔮 Future Improvements

- [ ] Add voice command support
- [ ] GUI to adjust dead zone and sensitivity
- [ ] Support for more games
- [ ] Two-hand gesture support for extra controls
- [ ] Mobile phone camera support via IP Webcam

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| Camera too dark | Switch to Night mode (hold 2 fingers for 1.5 sec) |
| Head steering not working | Press R to recalibrate, hold head straight |
| Hand not detected | Make sure hand is clearly visible in the frame |
| Game not responding | Click on Asphalt 8 window to bring it into focus |
| Model not found error | Check that model paths in the script are correct |
| False pause / resume | Keep hand visible — controller waits 15 frames before pausing |

---

## 👨‍💻 About the Developer

**Vidhya Sagar**
🎓 Final Year ECE Student — Podhigai College of Engineering and Technology
💡 Passionate about AI, Computer Vision and Embedded Systems
🔗 GitHub: [@vidhyasagar-alt](https://github.com/vidhyasagar-alt)

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify and share!

---

⭐ If this project impressed you, please give it a star!

*Made with ❤️ and a lot of late nights by Vidhya Sagar — ECE Department, Podhigai College of Engineering and Technology*
