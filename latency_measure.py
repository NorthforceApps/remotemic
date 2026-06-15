#!/usr/bin/env python3
import argparse
import math
import subprocess
import wave
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks


def record_wav(path: Path, seconds: float, device: str, rate: int, channels: int) -> None:
    duration = max(1, math.ceil(seconds))
    cmd = [
        "arecord",
        "-D",
        device,
        "-f",
        "S16_LE",
        "-c",
        str(channels),
        "-r",
        str(rate),
        "-d",
        str(duration),
        str(path),
    ]
    subprocess.run(cmd, check=True)


def read_wav(path: Path) -> tuple[int, np.ndarray]:
    with wave.open(str(path), "rb") as wav:
        rate = wav.getframerate()
        channels = wav.getnchannels()
        frames = wav.readframes(wav.getnframes())
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    audio /= max(np.max(np.abs(audio)), 1.0)
    return rate, audio


def smooth_energy(audio: np.ndarray, rate: int) -> np.ndarray:
    win = max(1, int(rate * 0.003))
    energy = np.abs(audio)
    return np.convolve(energy, np.ones(win) / win, mode="same")


def detect_click_pairs(audio: np.ndarray, rate: int) -> list[tuple[float, float, float]]:
    env = smooth_energy(audio, rate)
    threshold = max(0.08, float(np.percentile(env, 99.5)) * 0.45)
    distance = int(rate * 0.035)
    peaks, props = find_peaks(env, height=threshold, distance=distance)
    times = peaks / rate
    heights = props["peak_heights"]

    pairs = []
    used = set()
    for i, t0 in enumerate(times):
        if i in used:
            continue
        candidates = np.where((times > t0 + 0.03) & (times < t0 + 0.6))[0]
        if len(candidates) == 0:
            continue
        # Choose nearest plausible echo/playback peak.
        j = int(candidates[0])
        if heights[j] < heights[i] * 0.15:
            continue
        used.add(i)
        used.add(j)
        pairs.append((float(t0), float(times[j]), float(times[j] - t0)))
    return pairs


def plot(path: Path, out: Path) -> None:
    rate, audio = read_wav(path)
    seconds = np.arange(len(audio)) / rate
    env = smooth_energy(audio, rate)
    pairs = detect_click_pairs(audio, rate)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
    ax1.plot(seconds, audio, linewidth=0.6)
    ax1.set_ylabel("wave")
    ax1.set_title(str(path))
    ax2.plot(seconds, env, linewidth=0.9)
    ax2.set_ylabel("energy")
    ax2.set_xlabel("seconds")

    for src, out_t, delay in pairs:
        for ax in (ax1, ax2):
            ax.axvline(src, color="tab:green", alpha=0.7)
            ax.axvline(out_t, color="tab:red", alpha=0.7)
        ax2.annotate(
            f"{delay * 1000:.0f} ms",
            xy=(out_t, env[min(int(out_t * rate), len(env) - 1)]),
            xytext=(out_t, max(env) * 0.8),
            arrowprops={"arrowstyle": "->", "color": "tab:red"},
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(out, dpi=160)

    if pairs:
        delays_ms = np.array([p[2] for p in pairs]) * 1000
        print(f"pairs: {len(pairs)}")
        print(f"median: {np.median(delays_ms):.1f} ms")
        print(f"min/max: {np.min(delays_ms):.1f}/{np.max(delays_ms):.1f} ms")
        print("delays:", " ".join(f"{x:.0f}" for x in delays_ms), "ms")
    else:
        print("No click pairs auto-detected. Open PNG and measure spikes manually.")
    print(f"wrote: {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true", help="record before plotting")
    parser.add_argument("--seconds", type=float, default=12)
    parser.add_argument("--device", default="hw:0,4")
    parser.add_argument("--rate", type=int, default=48000)
    parser.add_argument("--channels", type=int, default=2)
    parser.add_argument("--wav", type=Path, default=Path("latency-test.wav"))
    parser.add_argument("--png", type=Path, default=Path("latency-test.png"))
    args = parser.parse_args()

    if args.record:
        record_wav(args.wav, args.seconds, args.device, args.rate, args.channels)
    plot(args.wav, args.png)


if __name__ == "__main__":
    main()
