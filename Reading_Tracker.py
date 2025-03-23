import ttkbootstrap as tb  # 替换 tkinter 和 ttk
from ttkbootstrap.constants import *  # 直接使用 `PRIMARY`、`SUCCESS` 等常量
from tkinter import messagebox
import json
import os
import datetime

DATA_FILE = "progress.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
else:
    data = {}

def change_theme(event):
    """切换 ttkbootstrap 主题"""
    selected_theme = theme_var.get()
    style.theme_use(selected_theme)
    update_user_style()

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def update_option_menu():
    book_options = list(data.keys())
    default_value = "请选择书籍" if book_options else "暂无书籍"

    book_menu['menu'].delete(0, 'end')
    for book in book_options:
        book_menu["menu"].add_command(label=book, command=lambda v=book: book_var.set(v))  # ✅ 修复错误
    
    book_var.set(default_value)

def add_book():
    title = book_entry.get().strip().strip("《").strip("》").strip()
    total_pages = total_pages_entry.get().strip()
    init_read_pages = init_read_pages_entry.get().strip()
    goal_date = goal_date_entry.get().strip()
    
    if not title:
        messagebox.showerror("错误", "书名不能为空！")
        return
    
    if not total_pages.isdigit() or not init_read_pages.isdigit():
        messagebox.showerror("错误", "总页数和已读页数必须是正整数！")
        return
    
    total_pages = int(total_pages)
    init_read_pages = int(init_read_pages)
    
    if total_pages <= 0 or init_read_pages < 0:
        messagebox.showerror("错误", "总页数必须大于0，已读页数不能为负！")
        return
    
    if init_read_pages > total_pages:
        messagebox.showerror("错误", "已读页数不能大于总页数！")
        return
    
    try:
        goal_date_obj = datetime.datetime.strptime(goal_date, "%Y-%m-%d")
        if goal_date_obj < datetime.datetime.today():
            messagebox.showerror("错误", "目标完成日期不能早于当前日期！")
            return
    except ValueError:
        messagebox.showerror("错误", "目标完成日期格式不正确！应为 YYYY-MM-DD")
        return
    
    start_date = str(datetime.date.today())
    start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    remaining_days = max((goal_date_obj - start_date_obj).days, 1)
    target_daily = (total_pages - init_read_pages) / remaining_days 
    
    data[title] = {
        "total_pages": total_pages,
        "init_read_pages": init_read_pages,
        "start_date": start_date,
        "goal_date": goal_date,
        "target_daily": round(target_daily, 2),
        "records": []
    }

    save_data()
    update_display()
    update_option_menu()
    messagebox.showinfo("成功", f"书籍《{title}》添加成功！")

def delete_book():
    title = book_var.get()
    if not title or title == "请选择书籍":
        messagebox.showerror("错误", "请选择要删除的书籍！")
        return
    
    if not title or title == "暂无书籍":
        messagebox.showerror("错误", "请至少添加一本书籍！")
        return
    
    confirm = messagebox.askyesno("确认", f"确定要删除书籍《{title}》吗？")
    if confirm:
        del data[title]
        save_data()
        update_display()
        update_option_menu()
        messagebox.showinfo("成功", f"书籍《{title}》已删除！")


def log_progress():
    title = book_var.get()
    pages = current_page_entry.get()
    
    if not title or title == "请选择书籍":
        messagebox.showerror("错误", "请选择一本书籍！")
        return
    if not pages.isdigit():
        messagebox.showerror("错误", "请输入有效的页数！")
        return

    pages = int(pages)
    today = str(datetime.date.today())
    book_info = data[title]
    records = book_info["records"]

    last_read = records[-1]["page"] if records else book_info["init_read_pages"]
    if pages < last_read:
        messagebox.showerror("错误", "当前页数不能小于已读页数！")
        return
    if pages > book_info["total_pages"]:
        messagebox.showerror("错误", "当前页数不能超过总页数！")
        return

    # 判断是否已经有今天的记录
    if records and records[-1]["date"] == today:
        records[-1]["page"] = pages  # 更新今天的记录
    else:
        records.append({"date": today, "page": pages})  # 添加新记录

    save_data()
    update_display()


def update_user_style():
    # 重新应用自定义样式
    """重新应用自定义样式"""
    style.configure(
        "Red.TButton",
        font=("微软雅黑", 9),  
        foreground="red",
        bootstyle="danger",  # 确保按钮样式与 ttkbootstrap 一致
        padding=(10, 5)  # 统一按钮的 padding
    )
    style.configure(
        "Green.TLabel",
        font=("微软雅黑", 10),  
        foreground="green",
        bootstyle="danger",  # 确保按钮样式与 ttkbootstrap 一致
        padding=(10, 5)  # 统一按钮的 padding
    )
    style.configure(
        "Red.TLabel",
        font=("微软雅黑", 10),  
        foreground="red",
        bootstyle="danger",  # 确保按钮样式与 ttkbootstrap 一致
        padding=(10, 5)  # 统一按钮的 padding
    )

def schedule_auto_refresh():
    update_display()
    root.after(60000, schedule_auto_refresh)  # 每隔60秒刷新一次
    
def update_display():
    for widget in progress_frame.winfo_children():
        widget.destroy()
    
    row = 0
    for title, info in data.items():
        total_pages = info.get("total_pages", 0)
        init_read_pages = info.get("init_read_pages", 0)
        start_date = info.get("start_date", str(datetime.date.today()))
        goal_date = info.get("goal_date", "未知")
        target_daily = info.get("target_daily", 1)
        records = info.get("records", [])
        
        last_read = max(records[-1]["page"], init_read_pages) if records else init_read_pages
        elapsed_days = max((datetime.datetime.today() - datetime.datetime.strptime(start_date, "%Y-%m-%d")).days, 1) + 1
        print(last_read)
        print(init_read_pages)
        print(elapsed_days)
        avg_speed = (last_read - init_read_pages) / elapsed_days if elapsed_days > 0 else 0
        expected_finish = datetime.datetime.today() + datetime.timedelta(days=(total_pages - last_read) / avg_speed) if avg_speed > 0 else "未开始"
        progress = (last_read / total_pages) * 100 if total_pages > 0 else 0
        prev_read = records[-2]["page"] if len(records) > 1 else init_read_pages
        today = str(datetime.date.today())
        today_record = next((r for r in records[::-1] if r["date"] == today), None)
        last_record_before_today = next((r for r in records[::-1] if r["date"] != today), None)
        
        # 如果今天有记录，提取今天读到的页数
        if today_record:
            today_read = today_record["page"]
            last_read_before_today = last_record_before_today["page"] if last_record_before_today else info["init_read_pages"]
            daily_progress = today_read - last_read_before_today
        else:
            daily_progress = 0
        
        is_on_track = "✅ 达标" if daily_progress >= target_daily else "❌ 未达标"

        
        tb.Label(progress_frame, text=f"{title}", font=("微软雅黑", 12, "bold"), bootstyle="primary").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        tb.Label(progress_frame, text=f"总页数: {total_pages}", font=("微软雅黑", 10), bootstyle="primary").grid(row=row, column=1, padx=5, pady=5, sticky="w")
        tb.Label(progress_frame, text=f"已读页数: {last_read}", font=("微软雅黑", 10), bootstyle="primary").grid(row=row, column=2, padx=5, pady=5, sticky="w")
        tb.Label(progress_frame, text=f"进度: {progress:.1f}%", font=("微软雅黑", 10), bootstyle="primary").grid(row=row, column=3, padx=5, pady=5, sticky="w")

        # 创建进度条的外框
        progress_bar_frame = tb.LabelFrame(progress_frame, text="进度条", bootstyle="primary")
        progress_bar_frame.grid(row=row, column=4, columnspan=3, padx=5, pady=5, sticky="we")

        # 在外框内放置进度条
        progress_bar = tb.Progressbar(progress_bar_frame, length=200, mode='determinate', bootstyle="primary")
        progress_bar.pack(fill="x", padx=5, pady=5)  # 让进度条自适应 LabelFrame
        progress_bar['value'] = progress  # 设置进度
        tb.Label(progress_frame, text=f"目标每日: {target_daily:.1f}", font=("微软雅黑", 10), bootstyle="primary").grid(row=row+1, column=0, padx=5, pady=5, sticky="w")
        tb.Label(progress_frame, text=f"实际每日: {avg_speed:.1f}", font=("微软雅黑", 10), bootstyle="primary").grid(row=row+1, column=1, padx=5, pady=5, sticky="w")
        tb.Label(progress_frame, text=f"开始日期: {start_date}", font=("微软雅黑", 10), bootstyle="primary").grid(row=row+1, column=2, padx=5, pady=5, sticky="w")
        tb.Label(progress_frame, text=f"目标完成: {goal_date}", font=("微软雅黑", 10), bootstyle="primary").grid(row=row+1, column=3, padx=5, pady=5, sticky="w")
        tb.Label(progress_frame, text=f"预计完成: {expected_finish if isinstance(expected_finish, str) else expected_finish.date()}", font=("微软雅黑", 10), bootstyle="primary").grid(row=row+1, column=4, padx=5, pady=5, sticky="w")
        color_style = "Green.TLabel" if "✅" in is_on_track else "Red.TLabel"
        tb.Label(progress_frame, text=is_on_track, style=color_style).grid(row=row+1, column=5, padx=5, pady=5, sticky="w")
        row += 2

root = tb.Window(themename="cerculean")
root.title("Reading Tracker")

# 置顶
root.attributes("-topmost", True)

# 创建 ttk 样式
style = tb.Style()
style.configure("Red.TButton")
style.map("Red.TButton", foreground=[("!disabled", "red")])  # 让按钮文本变红
style.configure("Red.TLabel")
style.map("Red.TLabel", foreground=[("!disabled", "red")])  # 让标签文本变绿
style.configure("Green.TLabel")
style.map("Green.TLabel", foreground=[("!disabled", "green")])  # 让标签文本变绿

# 主题选择下拉菜单
theme_var = tb.StringVar(value="cosmo")  # 默认主题
theme_menu_frame = tb.Frame(root)
theme_menu_frame.pack(fill="x", padx=10, pady=5)
tb.Label(theme_menu_frame, text="选择主题:", bootstyle="primary").pack(side="left", padx=5)
theme_combobox = tb.Combobox(
    theme_menu_frame, textvariable=theme_var, values=style.theme_names(), state="readonly", bootstyle="primary"
)
theme_combobox.pack(side="left", padx=5)
theme_combobox.bind("<<ComboboxSelected>>", change_theme)  # 绑定事件
style.theme_use("cosmo")  
update_user_style()

# 添加书籍部分
add_frame = tb.LabelFrame(root, text="添加书籍", bootstyle="primary")
add_frame.pack(fill="x", padx=10, pady=5)

tb.Label(add_frame, text="书名:", bootstyle="primary").grid(row=0, column=0, padx=10, pady=5)
book_entry = tb.Entry(add_frame, bootstyle="primary")
book_entry.grid(row=0, column=1)

tb.Label(add_frame, text="总页数:", bootstyle="primary").grid(row=0, column=2, padx=10, pady=5)
total_pages_entry = tb.Entry(add_frame, width=8, bootstyle="primary")
total_pages_entry.grid(row=0, column=3)

tb.Label(add_frame, text="已读页数:", bootstyle="primary").grid(row=0, column=4, padx=10, pady=5)
init_read_pages_entry = tb.Entry(add_frame, width=8, bootstyle="primary")
init_read_pages_entry.grid(row=0, column=5)

tb.Label(add_frame, text="目标完成日期:", bootstyle="primary").grid(row=0, column=6, padx=10, pady=5)
goal_date_entry = tb.Entry(add_frame, bootstyle="primary")
goal_date_entry.grid(row=0, column=7)
goal_date_entry.insert(0, "YYYY-MM-DD")

tb.Button(add_frame, text="添加书籍", command=add_book, bootstyle="primary").grid(row=0, column=8, padx=10, pady=5)

# 记录进度部分
log_frame = tb.LabelFrame(root, text="记录进度", bootstyle="primary")
log_frame.pack(fill="x", padx=10, pady=5)

book_var = tb.StringVar(root, value="暂无书籍")
book_menu = tb.OptionMenu(log_frame, book_var, *list(data.keys()) if data else ["暂无书籍"])
book_menu.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

update_option_menu()

tb.Label(log_frame, text="当前页数:", bootstyle="primary").grid(row=0, column=2)
current_page_entry = tb.Entry(log_frame, width=8, bootstyle="primary")
current_page_entry.grid(row=0, column=3)

tb.Button(log_frame, text="记录进度", command=log_progress, bootstyle="primary").grid(row=0, column=4, padx=10, pady=5)
tb.Button(log_frame, text="删除书籍", command=delete_book, bootstyle="primary").grid(row=0, column=99, sticky='e', padx=10, pady=5)
log_frame.columnconfigure(6, weight=1)  # 让最后一列自动扩展，使按钮贴右


# 进度显示部分
progress_frame = tb.LabelFrame(root, text="进度显示", bootstyle="primary")
progress_frame.pack(fill="both", expand=True, padx=10, pady=5)

update_display()
schedule_auto_refresh()
root.update_idletasks()
root.geometry("")
root.mainloop()
