import tkinter as tk
from tkinter import filedialog
import time
import csv
import os
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# 设置支持日文字体（请根据实际情况更换）
matplotlib.rcParams['font.family'] = ['Meiryo']

class ArousalValenceRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Arousal-Valence Annotation Tool")

        self.data = []
        self.current_click_coordinates = None
        self.text_labels = []

        # 拖动相关变量
        self.dragging_label = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # 上方绘图区域
        self.frame = tk.Frame(self.master)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 底部输入与控制区域
        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 时间输入框与记录按钮
        tk.Label(self.bottom_frame, text="Enter time point(s):").pack(side=tk.LEFT, padx=5)
        self.time_entry = tk.Entry(self.bottom_frame, width=10)
        self.time_entry.pack(side=tk.LEFT, padx=5)
        self.record_button = tk.Button(self.bottom_frame, text="Record", command=self.record_data)
        self.record_button.pack(side=tk.LEFT, padx=5)

        # 保存布局按钮
        self.save_layout_button = tk.Button(self.bottom_frame, text="Save layout", command=self.save_layout)
        self.save_layout_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 初始化绘图
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel("")
        self.ax.set_ylabel("")
        self.ax.set_title("")

        # 绘制参考圆环
        circle = patches.Circle((0,0), radius=1.0, fill=False, linestyle='-', color='black')
        self.ax.add_patch(circle)

        # 绘制坐标轴
        self.ax.axhline(y=0, color='black', linewidth=1)
        self.ax.axvline(x=0, color='black', linewidth=1)

        # 添加标签
        self.add_label(0, 1.15, "覚醒(arousing)", fontsize=10, ha='center', va='bottom')
        self.add_label(0, -1.15, "沈静(sleepy)", fontsize=10, ha='center', va='top')
        self.add_label(1.15, 0, "快(pleasure)", fontsize=10, ha='left', va='center', rotation=0)
        self.add_label(-1.15, 0, "不快(unpleasure)", fontsize=10, ha='right', va='center', rotation=0)

        self.add_label(-0.05, 1.05, "(woke up)覚醒した ●", fontsize=10, ha='left', va='bottom')
        self.add_label(0.1, 1.00, "(surprised)驚愕した ●", fontsize=10, ha='left', va='bottom')
        self.add_label(0.25, 0.95, "● 興奮した(excited)", fontsize=10, ha='right', va='bottom')

        self.add_label(-0.8, 1.0, "(vigilance)警戒 ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.8, 1.0, "(anger)怒り ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.9, 0.9, "(fear)恐れ ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.9, 0.8, "(tension)緊張 ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.9, 0.7, "(worries)悩み ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.8, 0.6, "(unpleasant)不愉快 ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.7, 0.5, "(frustration)フラストレーション ●", fontsize=10, ha='right', va='bottom')

        self.add_label(0.9, 0.5, "● (happiness)幸福感", fontsize=10, ha='left', va='bottom')
        self.add_label(0.8, 0.4, "● (joy)喜び", fontsize=10, ha='left', va='bottom')
        self.add_label(0.7, 0.3, "● (happy)嬉しい", fontsize=10, ha='left', va='bottom')
        self.add_label(0.7, 0.2, "● (pleasant)愉快", fontsize=10, ha='left', va='bottom')

        self.add_label(-0.9, -0.1, "(miserable)惨めな ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.8, -0.2, "(get depressed)落ち込む ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.9, -0.3, "(sorrow)哀しみ ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.9, -0.4, "(depression)憂うつ ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.8, -0.5, "(boredom)退屈 ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.8, -0.6, "(Feeling listless)けだるい ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.7, -0.7, "(tired)疲れ ●", fontsize=10, ha='right', va='top')

        self.add_label(0.8, -0.1, "● 満足(satisfaction)", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.2, "● 充足(sufficiency)", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.3, "● 穏やか(gentle)", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.4, "● 落ち着き(calmness)", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.5, "● くつろぎ(Relaxation)", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.6, "● 安心(peace of mind)", fontsize=10, ha='left', va='top')

        self.add_label(0, -0.9, "眠気 ●(sleepiness)", fontsize=10, ha='center', va='top')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.right_button = 3

        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.output_file = "emotion_data.csv"
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["time(s)", "arousal", "valence"])

        # 启动时自动加载布局（如果存在）
        self.load_layout()

    def add_label(self, x, y, text, **kwargs):
        t = self.ax.text(x, y, text, **kwargs)
        self.text_labels.append({"artist": t, "text": text, "x": x, "y": y})

    def on_click(self, event):
        if event.button == 1: 
            if event.inaxes != self.ax:
                return
            V = event.xdata
            A = event.ydata
            self.current_click_coordinates = (A, V)
            self.ax.plot(V, A, 'ro', markersize=5)
            self.canvas.draw()

        if event.button == self.right_button:
            label = self.find_label_near(event.xdata, event.ydata, threshold=0.1)
            if label is not None:
                self.dragging_label = label
                self.drag_offset_x = label["x"] - event.xdata
                self.drag_offset_y = label["y"] - event.ydata
                # 改变标签颜色以示选中
                label["artist"].set_color('red')
                self.canvas.draw()

    def on_release(self, event):
        if event.button == self.right_button and self.dragging_label is not None:
            self.dragging_label["x"] = self.dragging_label["artist"].get_position()[0]
            self.dragging_label["y"] = self.dragging_label["artist"].get_position()[1]
            # 恢复标签颜色
            self.dragging_label["artist"].set_color('black')
            self.dragging_label = None
            self.canvas.draw()

    def on_motion(self, event):
        if self.dragging_label is not None and event.inaxes == self.ax:
            new_x = event.xdata + self.drag_offset_x
            new_y = event.ydata + self.drag_offset_y
            self.dragging_label["artist"].set_position((new_x, new_y))
            self.canvas.draw()

    def find_label_near(self, x, y, threshold=0.05):
        candidate = None
        for lbl in self.text_labels:
            lx, ly = lbl["artist"].get_position()
            dist = math.sqrt((lx - x)**2 + (ly - y)**2)
            if dist < threshold:
                candidate = lbl
                threshold = dist
        return candidate

    def record_data(self):
        time_str = self.time_entry.get().strip()
        if not time_str or self.current_click_coordinates is None:
            return
        try:
            current_time = float(time_str)
        except ValueError:
            return
        A, V = self.current_click_coordinates
        self.data.append((current_time, A, V))
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([current_time, A, V])
        self.time_entry.delete(0, tk.END)
        self.current_click_coordinates = None

    def save_layout(self):
        layout_file = "layout.csv"
        with open(layout_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["text", "x", "y"])
            for lbl in self.text_labels:
                t = lbl["text"]
                x, y = lbl["artist"].get_position()
                writer.writerow([t, x, y])
        print("Layout saved to layout.csv")

    def load_layout(self):
        layout_file = "layout.csv"
        if not os.path.exists(layout_file):
            return
        layout_map = {}
        with open(layout_file, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header != ["text", "x", "y"]:
                return
            for row in reader:
                if len(row) == 3:
                    text, x_str, y_str = row
                    try:
                        x_pos = float(x_str)
                        y_pos = float(y_str)
                        layout_map[text] = (x_pos, y_pos)
                    except ValueError:
                        pass

        # 根据layout_map更新标签位置
        for lbl in self.text_labels:
            t = lbl["text"]
            if t in layout_map:
                x_pos, y_pos = layout_map[t]
                lbl["artist"].set_position((x_pos, y_pos))
                lbl["x"] = x_pos
                lbl["y"] = y_pos

        self.canvas.draw()
        print("layout.csv layout loaded")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArousalValenceRecorder(root)
    root.mainloop()
