import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
from datetime import datetime, timedelta
import sys
import os

if len(sys.argv) > 1:
    user_id = int(sys.argv[1])
else:
    user_id = None
    
# Tạo dữ liệu giả
def generate_mock_data():
    today = datetime(2025, 4, 14)
    dates = [(today - timedelta(days=x)).strftime("%d/%m") for x in range(13, -1, -1)]
    scan_volumes = [random.randint(50, 150) for _ in range(14)]

    sources = ["Việt", "Anh", "Pháp", "Đức", "Tây Ban Nha", "Khác"]
    ocr_accuracy = [random.uniform(80, 100) for _ in range(len(sources))]

    users = ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Admin"]
    actions = ["Quét OCR", "Chỉnh sửa", "Báo cáo lỗi OCR", "Cập nhật hệ thống OCR"]
    files = ["Báo cáo tài chính Q1.pdf", "Hợp đồng dịch vụ.docx", "Biên bản cuộc họp.pdf", "Hệ thống"]
    statuses = ["Hoàn thành", "Hoàn thành", "Đang xử lý", "Hoàn thành"]

    activities = []
    for i in range(4):
        time = (today - timedelta(hours=random.randint(1, 24))).strftime("%d/%m/%Y, %H:%M")
        activities.append({
            "user": users[i],
            "action": actions[i],
            "file": files[i],
            "time": time,
            "status": statuses[i]
        })

    return {
        "total_accounts": random.randint(1000, 2000),
        "total_scans": random.randint(5000, 10000),
        "ocr_accuracy": random.uniform(90, 99),
        "errors_reported": random.randint(100, 150),
        "dates": dates,
        "scan_volumes": scan_volumes,
        "sources": sources,
        "ocr_accuracy_data": ocr_accuracy,
        "activities": activities
    }



def load_statistic(root, top_frame):
    for widget in root.winfo_children():
        if widget not in [top_frame]:  # Giữ lại top_frame
            widget.pack_forget()  # Ẩn thay vì xóa
        
    data = generate_mock_data()

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    tab_summary = tk.Frame(notebook, bg="#f0f0f0")
    tab_charts = tk.Frame(notebook, bg="#f0f0f0")
    tab_activities = tk.Frame(notebook, bg="#f0f0f0")

    notebook.add(tab_summary, text="Tổng quan")
    notebook.add(tab_charts, text="Biểu đồ")
    notebook.add(tab_activities, text="Hoạt động gần đây")

    # Summary stats
    summary_frame = tk.Frame(tab_summary, bg="#f0f0f0")
    summary_frame.pack(fill=tk.X, pady=10)

    stats = [
        ("Tổng tài liệu", data["total_accounts"], "#4a90e2"),
        ("Trang đã quét OCR", data["total_scans"], "#2ecc71"),
        ("Độ chính xác OCR", f"{data['ocr_accuracy']:.1f}%", "#f39c12"),
        ("Lỗi được báo cáo", data["errors_reported"], "#9b59b6")
    ]

    for label, value, color in stats:
        frame = tk.Frame(summary_frame, bg=color, width=200, height=80)
        frame.pack_propagate(False)
        frame.pack(side=tk.LEFT, padx=10)
        tk.Label(frame, text=label, bg=color, fg="white", font=("Arial", 10)).pack(pady=5)
        tk.Label(frame, text=value, bg=color, fg="white", font=("Arial", 14, "bold")).pack()

    # Charts
    chart_left = tk.Frame(tab_charts, bg="#f0f0f0")
    chart_right = tk.Frame(tab_charts, bg="#f0f0f0")
    chart_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    chart_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    fig1 = Figure(figsize=(6, 3), dpi=100)
    ax1 = fig1.add_subplot(111)
    ax1.plot(data["dates"], data["scan_volumes"], color='skyblue', linewidth=2)
    ax1.set_title("Lượng tài liệu quét theo ngày")
    ax1.set_ylabel("Số lượng")
    ax1.tick_params(axis='x', rotation=45)
    fig1.tight_layout()

    canvas1 = FigureCanvasTkAgg(fig1, master=chart_left)
    canvas1.draw()
    canvas1.get_tk_widget().pack()

    fig2 = Figure(figsize=(4, 3), dpi=100)
    ax2 = fig2.add_subplot(111)
    ax2.bar(data["sources"], data["ocr_accuracy_data"], color='orange')
    ax2.set_title("Độ chính xác OCR theo nguồn")
    ax2.set_ylim(0, 100)
    ax2.tick_params(axis='x', rotation=45)
    fig2.tight_layout()

    canvas2 = FigureCanvasTkAgg(fig2, master=chart_right)
    canvas2.draw()
    canvas2.get_tk_widget().pack()

    # Activities
    activities_frame = tk.Frame(tab_activities, bg="#f0f0f0")
    activities_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ("User", "Action", "File", "Time", "Status")
    tree = ttk.Treeview(activities_frame, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120 if col != "File" else 180)

    for activity in data["activities"]:
        tag = "done" if activity["status"] == "Hoàn thành" else "processing"
        tree.insert("", tk.END, values=(
            activity["user"],
            activity["action"],
            activity["file"],
            activity["time"],
            activity["status"]
        ), tags=(tag,))

    tree.tag_configure("done", background="#d4edda")
    tree.tag_configure("processing", background="#fff3cd")

    tree.pack(fill=tk.BOTH, expand=True)

    admin_button = tk.Button(tab_activities, text="Công cụ quản trị viên", bg="red", fg="white", font=("Arial", 10))
    admin_button.pack(pady=5)
