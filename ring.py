import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import csv
import os
import datetime
import math

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 设置支持日文字体（请根据实际情况更换）
matplotlib.rcParams['font.family'] = ['Meiryo']

class ArousalValenceRecorder:
    def __init__(self, master):
        self.master = master
        self.master.title("Arousal-Valence Annotation Tool")

        # 数据列表: 存储(time, A, V)
        self.data = []
        self.text_labels = []

        # 拖动相关变量
        self.dragging_label = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # 用于存储已在图上绘制的点和线的艺术家对象，以便清空
        self.points_artists = []
        self.lines_artists = []

        # 存储标签参考线对象的字典：{label_text: line_artist}
        self.label_lines = {}

        # 上方绘图区域
        self.frame = tk.Frame(self.master)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 底部按钮区域
        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 保存记录按钮
        self.save_record_button = tk.Button(self.bottom_frame, text="記録保存", command=self.save_and_clear)
        self.save_record_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 新增保存layout布局按钮
        self.save_layout_button = tk.Button(self.bottom_frame, text="layout保存", command=self.save_layout)
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
        self.add_label(0, 1.15, "覚醒(arousing)", fontsize=12, ha='center', va='bottom')
        self.add_label(0, -1.15, "沈静(sleepy)", fontsize=12, ha='center', va='top')
        self.add_label(1.15, 0, "快(pleasure)", fontsize=12, ha='left', va='center', rotation=90)
        self.add_label(-1.15, 0, "不快(unpleasure)", fontsize=12, ha='right', va='center', rotation=90)

        self.add_label(-0.05, 1.05, "覚醒した ●", fontsize=10, ha='right', va='bottom')
        self.add_label(0.1, 1.00, "● 驚愕した", fontsize=10, ha='left', va='bottom')
        self.add_label(0.25, 0.95, "● 興奮した", fontsize=10, ha='left', va='bottom')

        self.add_label(-0.8, 1.0, "警戒 ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.8, 1.0, "怒り ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.9, 0.9, "恐れ ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.9, 0.8, "緊張 ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.9, 0.7, "悩み ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.8, 0.6, "不愉快 ●", fontsize=10, ha='right', va='bottom')
        self.add_label(-0.7, 0.5, "フラストレーション ●", fontsize=10, ha='right', va='bottom')

        self.add_label(0.9, 0.5, "● 幸福感", fontsize=10, ha='left', va='bottom')
        self.add_label(0.8, 0.4, "● 喜び", fontsize=10, ha='left', va='bottom')
        self.add_label(0.7, 0.3, "● 嬉しい", fontsize=10, ha='left', va='bottom')
        self.add_label(0.7, 0.2, "● 愉快", fontsize=10, ha='left', va='bottom')

        self.add_label(-0.9, -0.1, "惨めな ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.8, -0.2, "落ち込む ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.9, -0.3, "哀しみ ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.9, -0.4, "憂うつ ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.8, -0.5, "退屈 ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.8, -0.6, "けだるい ●", fontsize=10, ha='right', va='top')
        self.add_label(-0.7, -0.7, "疲れ ●", fontsize=10, ha='right', va='top')

        self.add_label(0.8, -0.1, "● 満足", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.2, "● 充足", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.3, "● 穏やか", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.4, "● 落ち着き", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.5, "● くつろぎ", fontsize=10, ha='left', va='top')
        self.add_label(0.7, -0.6, "● 安心", fontsize=10, ha='left', va='top')

        self.add_label(0, -0.9, "● 眠気", fontsize=10, ha='left', va='top')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.right_button = 3

        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        # 初始化时为各标签绘制参考线
        self.draw_label_lines()

        # 自动加载布局（如果有layout.csv则加载并更新参考线）
        self.load_layout()

    def add_label(self, x, y, text, **kwargs):
        t = self.ax.text(x, y, text, **kwargs)
        self.text_labels.append({"artist": t, "text": text, "x": x, "y": y})

    def draw_label_lines(self):
        # 首先删除已有的参考线
        for line in self.label_lines.values():
            line.remove()
        self.label_lines.clear()

        # 为每个标签绘制从(0,0)到标签位置的淡色虚线
        for lbl in self.text_labels:
            x, y = lbl["artist"].get_position()
            line = self.ax.plot([0, x], [0, y], color='gray', linestyle='--', linewidth=0.5)[0]
            self.label_lines[lbl["text"]] = line

        self.canvas.draw()

    def on_click(self, event):
        # 左键点击: 标记点，并弹出时间输入框
        if event.button == 1:
            if event.inaxes != self.ax:
                return
            V = event.xdata
            A = event.ydata

            # 弹出对话框让用户输入时间
            current_time = simpledialog.askfloat("時点を入力してください", "時点（ｓ）を入力してください:", parent=self.master)
            if current_time is None:
                # 用户取消输入，不添加点
                return

            # 将数据添加到列表中
            self.data.append((current_time, A, V))

            # 根据点在序列中的位置决定颜色
            if len(self.data) == 1:
                color = 'red'    # 第一个点为红色
            else:
                # 上一个最新点如果是绿色，可考虑不变。简单实现：最新点为绿色，前面点为蓝色
                # 其实前面点颜色会因为是已绘制点，不再改变。这里仅对新点使用绿色。
                color = 'green'

            pt = self.ax.plot(V, A, 'o', color=color, markersize=5)[0]
            self.points_artists.append(pt)

            # 连接上一个点和当前点
            if len(self.data) > 1:
                prev_time, prev_A, prev_V = self.data[-2]
                line = self.ax.plot([prev_V, V], [prev_A, A], color='black', linestyle='-', linewidth=1)[0]
                self.lines_artists.append(line)

            self.canvas.draw()

        # 右键点击: 拖动标签
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

            # 更新对应参考线位置
            text = self.dragging_label["text"]
            if text in self.label_lines:
                line = self.label_lines[text]
                line.set_xdata([0, self.dragging_label["x"]])
                line.set_ydata([0, self.dragging_label["y"]])

            self.dragging_label = None
            self.canvas.draw()

    def on_motion(self, event):
        if self.dragging_label is not None and event.inaxes == self.ax:
            new_x = event.xdata + self.drag_offset_x
            new_y = event.ydata + self.drag_offset_y
            self.dragging_label["artist"].set_position((new_x, new_y))
            # 不在motion更新线，以提高性能，释放鼠标后再更新线
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

    def save_and_clear(self):
        # 保存当前数据到CSV
        if not self.data:
            print("現在、保存するレコードはありません。")
            return

        # 文件名: emotion_YYYYMMDD_HHMMSS.csv
        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emotion_{now_str}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["time(s)", "arousal", "valence"])
            for row in self.data:
                writer.writerow(row)
        print(f"記録は次のように保存されました {filename}")

        # 清空数据与图上的点和线
        self.data.clear()

        # 移除点和线艺术家
        for pt in self.points_artists:
            pt.remove()
        self.points_artists.clear()

        for ln in self.lines_artists:
            ln.remove()
        self.lines_artists.clear()

        self.canvas.draw()

    def save_layout(self):
        layout_file = "layout.csv"
        with open(layout_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["text", "x", "y"])
            for lbl in self.text_labels:
                t = lbl["text"]
                x, y = lbl["artist"].get_position()
                writer.writerow([t, x, y])
        print("レイアウトの保存先 layout.csv")

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

        # 重新绘制参考线
        self.draw_label_lines()
        print("layout.csv レイアウトが読み込まれました")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArousalValenceRecorder(root)
    root.mainloop()
