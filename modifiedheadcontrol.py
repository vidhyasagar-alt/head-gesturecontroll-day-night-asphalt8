import cv2
import mediapipe as mp
import pyautogui
import time
import keyboard
import numpy as np

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

HAND_MODEL_PATH = r"D:\PY project\hand_landmarker.task"
FACE_MODEL_PATH = r"D:\PY project\face_landmarker.task"

# ─── MediaPipe Tasks API setup ───────────────────────────────────────────────
BaseOptions       = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# ─── Hand Landmarker ─────────────────────────────────────────────────────────
HandLandmarker        = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions

hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=HAND_MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.4,
    min_hand_presence_confidence=0.4,
    min_tracking_confidence=0.4,
)

try:
    landmarker = HandLandmarker.create_from_options(hand_options)
except Exception as e:
    print(f"❌ Error loading hand landmarker: {e}")
    exit()

# ─── Face Landmarker ──────────────────────────────────────────────────────────
FaceLandmarker        = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

face_options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=FACE_MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

try:
    face_landmarker = FaceLandmarker.create_from_options(face_options)
except Exception as e:
    print(f"❌ Error loading face landmarker: {e}")
    exit()

# ─── Camera ──────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# ─── Key state ───────────────────────────────────────────────────────────────
keys = {"up": False, "down": False, "left": False, "right": False}

def control(key):
    if key and not keys[key]:
        pyautogui.keyDown(key)
        keys[key] = True

def release(key):
    if keys[key]:
        pyautogui.keyUp(key)
        keys[key] = False

def release_all():
    for k in keys:
        if keys[k]:
            pyautogui.keyUp(k)
            keys[k] = False

# ─── Image enhancement ───────────────────────────────────────────────────────
def enhance_night(frame):
    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    yuv[:, :, 0] = clahe.apply(yuv[:, :, 0])
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

# ─── Pause / Resume ──────────────────────────────────────────────────────────
game_paused = False

def pause_game():
    global game_paused
    if not game_paused:
        release_all()
        pyautogui.press("escape")
        game_paused = True
        print("⏸  Game PAUSED (hand lost)")

def resume_game():
    global game_paused
    if game_paused:
        pyautogui.press("escape")
        game_paused = False
        print("▶  Game RESUMED (hand detected)")

# ─── Head calibration (ONE-TIME fixed neutral) ───────────────────────────────
# The neutral baseline is captured ONCE during a short startup countdown.
# It NEVER drifts afterwards, so moving right always means "steer right".

HEAD_DEAD_ZONE      = 0.06   # ±6% of frame width = straight zone
CALIBRATION_FRAMES  = 45     # collect ~1.5 s of frames at 30 fps
calibration_samples = []     # temporary buffer during calibration
head_neutral_x      = None   # locked after calibration; None = not yet set
calibration_done    = False

def try_calibrate(nose_x):
    """
    Collect nose X samples until we have enough, then lock the neutral.
    Returns True once calibration is complete.
    """
    global head_neutral_x, calibration_done
    if calibration_done:
        return True
    calibration_samples.append(nose_x)
    if len(calibration_samples) >= CALIBRATION_FRAMES:
        head_neutral_x   = float(np.mean(calibration_samples))
        calibration_done = True
        print(f"✅ Neutral locked at x = {head_neutral_x:.3f}  (press R to recalibrate)")
    return calibration_done

def recalibrate():
    """Reset calibration so the next N frames set a new neutral."""
    global calibration_done, head_neutral_x
    calibration_samples.clear()
    calibration_done = False
    head_neutral_x   = None
    print("🔄 Recalibrating — hold head straight…")

# ─── Mode state ──────────────────────────────────────────────────────────────
night_mode          = False
MODE_SWITCH_HOLD_MS = 1500
mode_gesture_start  = None
last_mode_fingers   = 0

# ─── Finger counting helpers ─────────────────────────────────────────────────
FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]

def count_fingers(lm):
    count = 0
    for tip, pip in zip(FINGER_TIPS, FINGER_PIPS):
        if lm[tip].y < lm[pip].y:
            count += 1
    return count

def is_fist(lm):
    return count_fingers(lm) == 0

# ─── Main loop ───────────────────────────────────────────────────────────────
print("🎮 Head-Steer Controller (FIXED SCALE) Active.")
print("   Hold your head STRAIGHT — calibrating neutral for ~1.5 s…")
print("   Move head LEFT/RIGHT to steer  |  1 finger = Nitro  |  Fist = Brake")
print("   Press R to recalibrate  |  Press Q to quit.\n")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # ── Keyboard shortcuts ────────────────────────────────────────────────────
    key_pressed = cv2.waitKey(1) & 0xFF
    if key_pressed == ord('q') or keyboard.is_pressed('q'):
        break
    if key_pressed == ord('r') or keyboard.is_pressed('r'):
        recalibrate()

    # ── Apply enhancement if night mode ──────────────────────────────────────
    display_frame = enhance_night(frame.copy()) if night_mode else frame.copy()
    rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

    ts = int(time.time() * 1000)

    # ── Detections ───────────────────────────────────────────────────────────
    mp_image     = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    hand_result  = landmarker.detect_for_video(mp_image, ts)
    face_result  = face_landmarker.detect_for_video(mp_image, ts)
    hand_present = hand_result and bool(hand_result.hand_landmarks)
    head_present = bool(face_result.face_landmarks)

    status_steer  = "STRAIGHT"
    status_action = "GAS"
    now = time.time()

    # ════════════════════════════════════════════════════════════════════════
    #  HEAD STEERING  (fixed neutral — no drift)
    # ════════════════════════════════════════════════════════════════════════
    if head_present:
        nose   = face_result.face_landmarks[0][1]
        nose_x = nose.x

        # --- Calibration phase ---
        if not calibration_done:
            try_calibrate(nose_x)
            # Show calibration progress bar and instructions
            progress = int((len(calibration_samples) / CALIBRATION_FRAMES) * (w - 20))
            cv2.rectangle(display_frame, (10, h // 2 - 20), (w - 10, h // 2 + 20),
                          (60, 60, 60), -1)
            cv2.rectangle(display_frame, (10, h // 2 - 20), (10 + progress, h // 2 + 20),
                          (0, 220, 100), -1)
            cv2.putText(display_frame, "CALIBRATING — LOOK STRAIGHT",
                        (12, h // 2 + 7), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            release("left"); release("right")
            status_steer = "CALIBRATING"

        # --- Normal steering phase (neutral is LOCKED) ---
        else:
            if head_neutral_x is not None:
                delta = nose_x - head_neutral_x   # <0 = turned left, >0 = turned right

                # Draw nose dot
                nx_px = int(nose_x * w)
                ny_px = int(nose.y * h)
                cv2.circle(display_frame, (nx_px, ny_px), 5, (255, 100, 0), -1)

                if delta < -HEAD_DEAD_ZONE:
                    control("left"); release("right")
                    status_steer = "STEER LEFT"
                elif delta > HEAD_DEAD_ZONE:
                    control("right"); release("left")
                    status_steer = "STEER RIGHT"
                else:
                    release("left"); release("right")
                    status_steer = "STRAIGHT"

                # ── Fixed dead-zone guide lines (never move) ──────────────────
                neutral_px = int(head_neutral_x * w)
                left_px    = int((head_neutral_x - HEAD_DEAD_ZONE) * w)
                right_px   = int((head_neutral_x + HEAD_DEAD_ZONE) * w)
                cv2.line(display_frame, (left_px,  0), (left_px,  h), (0, 255, 255), 1)
                cv2.line(display_frame, (right_px, 0), (right_px, h), (0, 255, 255), 1)
                cv2.line(display_frame, (neutral_px, 0), (neutral_px, h), (100, 100, 255), 1)
            else:
                release("left"); release("right")
    else:
        release("left"); release("right")
        status_steer = "NO HEAD"

    # ════════════════════════════════════════════════════════════════════════
    #  HAND → GAS / BRAKE / NITRO  +  PAUSE  +  MODE SWITCH
    # ════════════════════════════════════════════════════════════════════════
    if hand_present:
        resume_game()
        lm      = hand_result.hand_landmarks[0]
        fingers = count_fingers(lm)
        fist    = is_fist(lm)

        # ── Mode-switch detection ─────────────────────────────────────────
        mode_target = None
        if fingers == 1:
            mode_target = False   # Day
        elif fingers == 2:
            mode_target = True    # Night

        if mode_target is not None:
            if last_mode_fingers != fingers:
                mode_gesture_start = now
                last_mode_fingers  = fingers
            elif mode_gesture_start is not None and now - mode_gesture_start >= MODE_SWITCH_HOLD_MS / 1000:
                if night_mode != mode_target:
                    night_mode = mode_target
                    mode_label = "🌙 NIGHT" if night_mode else "☀️  DAY"
                    print(f"   Mode switched → {mode_label}")
                mode_gesture_start = now
        else:
            last_mode_fingers  = 0
            mode_gesture_start = None

        # ── Gas / Brake / Nitro ──────────────────────────────────────────
        if fist:
            control("down"); release("up")
            status_action = "BRAKE"
        elif fingers == 1:
            pyautogui.press("space")
            control("up"); release("down")
            status_action = "NITRO"
        else:
            control("up"); release("down")
            status_action = "GAS"

    else:
        pause_game()
        release_all()
        status_action = "HAND LOST"
        last_mode_fingers  = 0
        mode_gesture_start = None

    # ════════════════════════════════════════════════════════════════════════
    #  HUD overlay
    # ════════════════════════════════════════════════════════════════════════
    mode_tag = "NIGHT" if night_mode else "DAY"
    mode_col = (0, 180, 255) if night_mode else (0, 255, 180)

    cv2.putText(display_frame, f"{status_steer} | {status_action}",
                (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(display_frame, f"MODE: {mode_tag}",
                (8, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, mode_col, 2)
    if calibration_done:
        cv2.putText(display_frame, "R=recal",
                    (w - 70, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

    # Mode-switch progress bar
    if mode_gesture_start and last_mode_fingers in (1, 2):
        elapsed  = min(now - mode_gesture_start, MODE_SWITCH_HOLD_MS / 1000)
        progress = int((elapsed / (MODE_SWITCH_HOLD_MS / 1000)) * (w - 20))
        cv2.rectangle(display_frame, (10, h - 15), (10 + progress, h - 5),
                      (255, 200, 0), -1)
        cv2.putText(display_frame, "HOLD TO SWITCH MODE",
                    (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 200, 0), 1)

    cv2.imshow ("Head+Hand Controller", display_frame)

 # ─── Cleanup ─────────────────────────────────────────────────────────────────
release_all()
cap.release()
face_landmarker.close()
cv2.destroyAllWindows()
print("👋 Exited cleanly.")