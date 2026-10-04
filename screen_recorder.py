import os
import time
import threading
import cv2
import numpy as np
import mss
import pygetwindow as gw


class ScreenRecorder:
    def __init__(self):
        self.is_recording = False
        self.output_filename = "recorded_gameplay.mp4"
        self._thread = None

    def get_game_window_bounds(self, target_titles=("scrcpy", "bluestacks", "ldplayer", "nox")):
        """Finds the mobile emulator window region on screen."""
        windows = gw.getAllWindows()
        for win in windows:
            title_lower = win.title.lower()
            if any(target in title_lower for target in target_titles):
                if win.width > 0 and win.height > 0:
                    return {
                        "top": win.top,
                        "left": win.left,
                        "width": win.width,
                        "height": win.height,
                    }

        # Default to full monitor 1 if emulator window isn't explicitly found
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            return {
                "top": monitor["top"],
                "left": monitor["left"],
                "width": monitor["width"],
                "height": monitor["height"],
            }

    def start_recording(self, fps=30.0):
        """Starts background recording."""
        if self.is_recording:
            return

        self.is_recording = True
        bounds = self.get_game_window_bounds()

        # Ensure width and height are even numbers for VideoWriter
        width = bounds["width"] - (bounds["width"] % 2)
        height = bounds["height"] - (bounds["height"] % 2)
        bounds["width"], bounds["height"] = width, height

        self._thread = threading.Thread(
            target=self._record_loop,
            args=(bounds, fps),
            daemon=True
        )
        self._thread.start()

    def _record_loop(self, bounds, fps):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(self.output_filename, fourcc, fps, (bounds["width"], bounds["height"]))

        with mss.mss() as sct:
            frame_duration = 1.0 / fps
            while self.is_recording:
                start_time = time.time()

                sct_img = sct.grab(bounds)
                frame = np.array(sct_img)
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                out.write(frame_bgr)

                elapsed = time.time() - start_time
                sleep_time = frame_duration - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

        out.release()

    def stop_recording(self):
        """Stops recording and returns saved video filepath."""
        self.is_recording = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)

        return os.path.abspath(self.output_filename)
