import tkinter as tk
from tkinter import messagebox
import numpy as np

ZONES = ["Library", "Hostels", "Cafeteria", "Labs", "Admin Block"]
DEFAULT_CURRENT = [54, 68, 72, 61, 47]
DEFAULT_PREVIOUS = [48, 59, 64, 56, 41]


def predict_loads(current_loads, previous_loads):
    current = np.asarray(current_loads, dtype=float)
    previous = np.asarray(previous_loads, dtype=float)
    trend = current - previous
    predicted = current + 0.75 * trend
    return np.clip(predicted, 0, 100)


def detect_congestion(predicted_loads, threshold=75):
    predicted = np.asarray(predicted_loads, dtype=float)
    return predicted >= threshold


def allocate_resources(predicted_loads):
    predicted = np.asarray(predicted_loads, dtype=float)
    total = predicted.sum()
    if total <= 0:
        return np.full_like(predicted, 100 / len(predicted), dtype=float)
    allocation = predicted / total * 100
    return np.round(allocation, 1)


def build_summary(current_loads, previous_loads, predicted_loads):
    current = np.asarray(current_loads, dtype=float)
    previous = np.asarray(previous_loads, dtype=float)
    predicted = np.asarray(predicted_loads, dtype=float)
    congestion = detect_congestion(predicted)
    allocation = allocate_resources(predicted)

    lines = []
    for index, zone in enumerate(ZONES):
        if congestion[index]:
            risk = "High"
        elif predicted[index] >= 60:
            risk = "Medium"
        else:
            risk = "Low"

        lines.append(
            f"{zone}: current {current[index]:.1f}%, previous {previous[index]:.1f}%, predicted {predicted[index]:.1f}%, risk {risk}, allocation {allocation[index]:.1f}%"
        )

    peak_zone = ZONES[int(np.argmax(predicted))]
    lines.append(f"\nPeak congestion risk: {peak_zone}")
    return "\n".join(lines)


class CampusWifiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campus Wi-Fi Load Balance")
        self.root.geometry("980x720")
        self.root.configure(bg="#f4f7fb")

        self.current_vars = []
        self.previous_vars = []

        tk.Label(
            root,
            text="Campus Wi-Fi Load Balance",
            font=("Segoe UI", 20, "bold"),
            bg="#f4f7fb",
            fg="#103a6b",
        ).pack(pady=(20, 5))

        tk.Label(
            root,
            text="Visualize load, predict congestion spots, and allocate network resources intelligently",
            font=("Segoe UI", 11),
            bg="#f4f7fb",
            fg="#495057",
        ).pack(pady=(0, 15))

        form_frame = tk.Frame(root, bg="#ffffff", bd=1, relief="solid")
        form_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(
            form_frame,
            text="Enter the latest load values for each zone",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#103a6b",
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        tk.Label(form_frame, text="Zone", font=("Segoe UI", 10, "bold"), bg="#ffffff").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Label(form_frame, text="Current Load (%)", font=("Segoe UI", 10, "bold"), bg="#ffffff").grid(row=1, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Previous Load (%)", font=("Segoe UI", 10, "bold"), bg="#ffffff").grid(row=1, column=2, padx=10, pady=5)

        for row_index, zone in enumerate(ZONES, start=2):
            tk.Label(form_frame, text=zone, bg="#ffffff", anchor="w").grid(row=row_index, column=0, padx=10, pady=6, sticky="w")

            current_var = tk.StringVar(value=str(DEFAULT_CURRENT[row_index - 2]))
            previous_var = tk.StringVar(value=str(DEFAULT_PREVIOUS[row_index - 2]))
            self.current_vars.append(current_var)
            self.previous_vars.append(previous_var)

            tk.Entry(form_frame, textvariable=current_var, width=10).grid(row=row_index, column=1, padx=10, pady=6)
            tk.Entry(form_frame, textvariable=previous_var, width=10).grid(row=row_index, column=2, padx=10, pady=6)

        button_frame = tk.Frame(root, bg="#f4f7fb")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Analyze Network",
            command=self.run_analysis,
            bg="#103a6b",
            fg="white",
            padx=10,
            pady=6,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=8)

        tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_form,
            bg="#6c757d",
            fg="white",
            padx=10,
            pady=6,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=8)

        result_frame = tk.Frame(root, bg="#ffffff", bd=1, relief="solid")
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(
            result_frame,
            text="Prediction Results",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#103a6b",
        ).pack(anchor="w", padx=12, pady=(10, 5))

        self.summary_text = tk.Text(result_frame, height=10, width=90, font=("Consolas", 10), wrap="word")
        self.summary_text.pack(padx=12, pady=(0, 10), fill="x")

        self.canvas = tk.Canvas(result_frame, height=260, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", padx=12, pady=(0, 12))

        self.run_analysis()

    def _read_inputs(self):
        current = []
        previous = []
        for current_var, previous_var in zip(self.current_vars, self.previous_vars):
            try:
                current_value = float(current_var.get())
                previous_value = float(previous_var.get())
            except ValueError:
                raise ValueError("Entries must contain numeric values")
            current.append(current_value)
            previous.append(previous_value)
        return current, previous

    def run_analysis(self):
        try:
            current, previous = self._read_inputs()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        predicted = predict_loads(current, previous)
        summary = build_summary(current, previous, predicted)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, summary)

        self.draw_chart(current, predicted)

    def draw_chart(self, current, predicted):
        self.canvas.delete("all")
        self.canvas.create_text(300, 18, text="Current Load vs Predicted Load", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(150, 40, text="Current", fill="#103a6b")
        self.canvas.create_text(300, 40, text="Predicted", fill="#e67e22")

        bar_width = 70
        gap = 20
        start_x = 40
        chart_height = 180
        for index, zone in enumerate(ZONES):
            x_pos = start_x + index * (bar_width + gap)
            current_height = int((current[index] / 100) * chart_height)
            predicted_height = int((predicted[index] / 100) * chart_height)

            self.canvas.create_rectangle(x_pos, 210 - current_height, x_pos + bar_width, 210, fill="#103a6b", outline="")
            self.canvas.create_rectangle(x_pos + 15, 210 - predicted_height, x_pos + 15 + bar_width - 30, 210, fill="#e67e22", outline="")
            self.canvas.create_text(x_pos + bar_width // 2, 225, text=zone, font=("Segoe UI", 8))

    def reset_form(self):
        for current_var, previous_var, default_current, default_previous in zip(self.current_vars, self.previous_vars, DEFAULT_CURRENT, DEFAULT_PREVIOUS):
            current_var.set(str(default_current))
            previous_var.set(str(default_previous))
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, "Click Analyze Network to view the latest prediction results.")
        self.canvas.delete("all")


def main():
    root = tk.Tk()
    CampusWifiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
