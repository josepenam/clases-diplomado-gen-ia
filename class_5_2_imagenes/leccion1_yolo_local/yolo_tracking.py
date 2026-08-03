#!/usr/bin/env python3
"""
Run YOLO tracking on a webcam stream with persistent track IDs.

Example:
  python yolo_tracking.py --model yolov8n.pt --source 0
"""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLO webcam tracking demo.")
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="YOLO model path or name (e.g. yolov8n.pt).",
    )
    parser.add_argument(
        "--source",
        default="0",
        help="Inference source (default: 0 for webcam).",
    )
    parser.add_argument(
        "--tracker",
        default="bytetrack.yaml",
        help="Tracker config (default: bytetrack.yaml).",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold.",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.45,
        help="IoU threshold.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Inference image size.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Device for inference (e.g. 'cpu', '0', '0,1').",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: ultralytics. Install with `pip install ultralytics`."
        ) from exc
    source = int(args.source) if args.source.isdigit() else args.source

    model = YOLO(args.model)

    track_kwargs = {
        "source": source,
        "show": True,
        "persist": True,
        "tracker": args.tracker,
        "conf": args.conf,
        "iou": args.iou,
        "imgsz": args.imgsz,
        "stream": True,
    }
    if args.device is not None:
        track_kwargs["device"] = args.device

    # Stream results to keep the window open and the tracker state persistent.
    for _ in model.track(**track_kwargs):
        pass


if __name__ == "__main__":
    main()
