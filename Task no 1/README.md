# Campus Wi-Fi Load Balance

This project is a Tkinter-based desktop application that helps campus network managers visualize Wi-Fi load, predict congestion spots, and decide how to allocate network resources.

## Features
- Enter current and previous load values for major campus zones.
- Predict future load using a simple NumPy-based trend model.
- Highlight high-risk congestion zones.
- Show a visual bar chart for current vs. predicted load.

## Run
```bash
python main.py
```

## Test
```bash
python -m pytest -q
```
