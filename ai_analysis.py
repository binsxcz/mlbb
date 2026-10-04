# ai_analysis.py
import cv2
import json
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input
from tensorflow.keras.models import load_model, Model
from tensorflow.keras import layers
from pydantic import BaseModel, Field

MODEL_PATH = "mlbb_model.h5"
INPUT_SHAPE = (224, 224)

_loaded_keras_model = None


class Keypoint(BaseModel):
    timestamp: str = Field(description="MM:SS timestamp")
    observed_action: str = Field(description="Action observed")
    how_to_improve: str = Field(description="Coaching advice")


class CoachingReport(BaseModel):
    summary: str = Field(description="Game summary")
    keypoints: list[Keypoint] = Field(description="List of tips")


def get_or_build_model():
    global _loaded_keras_model
    if _loaded_keras_model is not None:
        return _loaded_keras_model

    if os.path.exists(MODEL_PATH):
        print(f"[INFO] Loading saved Keras model from {MODEL_PATH}...")
        _loaded_keras_model = load_model(MODEL_PATH)
    else:
        print("[INFO] No custom mlbb_model.h5 found. Initializing MobileNetV2 backbone...")
        base_model = MobileNetV2(
            input_shape=(INPUT_SHAPE[0], INPUT_SHAPE[1], 3),
            include_top=False,
            weights="imagenet"
        )
        base_model.trainable = False

        inputs = tf.keras.Input(shape=(INPUT_SHAPE[0], INPUT_SHAPE[1], 3))
        x = base_model(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.2)(x)
        outputs = layers.Dense(4, activation="softmax")(x)

        _loaded_keras_model = Model(inputs, outputs)

    return _loaded_keras_model


def verify_is_mlbb_gameplay(video_path):
    if not video_path or not os.path.exists(video_path):
        return False, "No input video file path provided or file does not exist."

    if os.path.getsize(video_path) == 0:
        return False, "The selected video file is empty (0 bytes). No input recorded."

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        cap.release()
        return False, "Could not open video file. The format may be corrupted or unsupported."

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = frame_count / fps

    if duration_sec < 3.0:
        cap.release()
        return False, f"Recording too short ({duration_sec:.1f}s). You must record at least 3 seconds of gameplay."

    ret, first_frame = cap.read()
    if not ret or first_frame is None:
        cap.release()
        return False, "Failed to decode frames from the video file."

    height, width, _ = first_frame.shape
    aspect_ratio = width / float(height)

    if aspect_ratio < 1.2:
        cap.release()
        return False, "Invalid orientation. Uploaded video is not in landscape mode (Mobile Legends requires horizontal gameplay)."

    gray_first = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    variances = []

    sample_steps = max(1, frame_count // 5)
    for i in range(1, 5):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * sample_steps)
        ret, frame = cap.read()
        if ret and frame is not None:
            gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray_first, gray_curr)
            variances.append(np.mean(diff))

    cap.release()

    if len(variances) > 0 and np.mean(variances) < 1.0:
        return False, "Static or blank screen detected. Please record or upload active gameplay footage."

    return True, None


def extract_and_preprocess_frames(video_path, interval_sec=5.0, max_frames=15):
    """
    Extracts frames at a 5-second interval for model evaluation.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_jump = int(fps * interval_sec)

    preprocessed_frames = []
    timestamps = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_jump == 0:
            time_sec = frame_count / fps
            mins, secs = int(time_sec // 60), int(time_sec % 60)
            time_str = f"{mins:02d}:{secs:02d}"

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized_frame = cv2.resize(rgb_frame, INPUT_SHAPE)
            processed_tensor = preprocess_input(resized_frame.astype("float32"))

            preprocessed_frames.append(processed_tensor)
            timestamps.append(time_str)

        frame_count += 1
        if len(preprocessed_frames) >= max_frames:
            break

    cap.release()
    return timestamps, np.array(preprocessed_frames)


def analyze_gameplay(video_path):
    is_valid, error_msg = verify_is_mlbb_gameplay(video_path)
    if not is_valid:
        raise ValueError(f"Analysis Aborted: {error_msg}")

    model = get_or_build_model()
    timestamps, frame_batch = extract_and_preprocess_frames(video_path)

    if len(frame_batch) == 0:
        raise ValueError("Analysis Aborted: No valid frames could be extracted from the video stream.")

    predictions = model.predict(frame_batch)

    LABEL_MAP = {
        0: ("Positioning Error / High Overextension Risk",
            "Maintain safer distance behind frontline and keep vision on side bushes during teamfights."),
        1: ("Isolated Objective Contest Opportunity",
            "Check mini-map before committing to solo pushes. Coordinate with Jungler for Turtle/Lord."),
        2: ("Suboptimal Skill Sequence / Cooldown Usage",
            "Hold core crowd control abilities for high-threat target entry instead of minion waves."),
        3: ("Solid Teamfight Execution & Rotational Positioning",
            "Good map awareness and timely rotation. Continue mirroring enemy roamer movements.")
    }

    keypoints = []

    # Ensure predictions handle both single or multiple output dimensions safely
    if len(predictions.shape) == 1:
        predictions = np.expand_dims(predictions, axis=0)

    for i, pred in enumerate(predictions):
        time_str = timestamps[i] if i < len(timestamps) else "00:00"
        predicted_class_idx = int(np.argmax(pred))
        confidence = float(np.max(pred))

        # Fallback if prediction class index exceeds map length
        if predicted_class_idx not in LABEL_MAP:
            predicted_class_idx = 0

        action, advice = LABEL_MAP[predicted_class_idx]
        keypoints.append({
            "timestamp": time_str,
            "observed_action": f"{action} (Confidence: {confidence:.1%})",
            "how_to_improve": advice
        })

    summary = (
        f"MobileNetV2 Keras Model processed {len(frame_batch)} validated MLBB frames (5s interval). "
        f"Generated {len(keypoints)} tactical evaluation points."
    )

    return {
        "summary": summary,
        "keypoints": keypoints
    }
