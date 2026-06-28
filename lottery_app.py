import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class LotteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("课堂随机抽奖器")
        self.root.geometry("600x700")

        self.class_file = os.path.join(os.path.dirname(__file__), "class_profiles.json")
        self.class_profiles = {}
        self.current_class_name = "默认班级"
        self.students = []
        self.high_prob = {}
        self.normal_weight = 1

        self.load_class_profiles()
        self.setup_ui()
        self.refresh_class_combo()
        self.update_student_list()
        
    def setup_ui(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== 班级管理区域 =====
        class_frame = ttk.LabelFrame(main_frame, text="🏫 班级管理", padding="10")
        class_frame.pack(fill=tk.X, pady=5)

        class_control_frame = ttk.Frame(class_frame)
        class_control_frame.pack(fill=tk.X, pady=2)

        ttk.Label(class_control_frame, text="班级:").pack(side=tk.LEFT, padx=2)
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(class_control_frame, textvariable=self.class_var, width=16, state="readonly")
        self.class_combo.pack(side=tk.LEFT, padx=2)
        self.class_combo.bind("<<ComboboxSelected>>", lambda event: self.switch_class())

        self.class_name_entry = ttk.Entry(class_control_frame, width=15)
        self.class_name_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(class_control_frame, text="切换", command=self.switch_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(class_control_frame, text="保存", command=self.save_current_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(class_control_frame, text="新建", command=self.create_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(class_control_frame, text="删除", command=self.delete_class).pack(side=tk.LEFT, padx=2)

        # ===== 学生管理区域 =====
        group_label = ttk.LabelFrame(main_frame, text="📋 学生管理", padding="10")
        group_label.pack(fill=tk.X, pady=5)
        
        # 添加学生
        add_frame = ttk.Frame(group_label)
        add_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(add_frame, text="姓名:").pack(side=tk.LEFT, padx=2)
        self.name_entry = ttk.Entry(add_frame, width=15)
        self.name_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(add_frame, text="权重:").pack(side=tk.LEFT, padx=2)
        self.weight_entry = ttk.Entry(add_frame, width=8)
        self.weight_entry.insert(0, "1")
        self.weight_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(add_frame, text="➕ 添加学生", command=self.add_student).pack(side=tk.LEFT, padx=5)
        
        # 学生列表
        list_frame = ttk.Frame(group_label)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 使用Treeview显示列表
        style = ttk.Style()
        style.configure("Treeview", rowheight=40, font=("Microsoft YaHei", 10))
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 10, "bold"))

        columns = ("序号", "姓名", "权重")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        self.tree.configure(selectmode="extended")
        self.tree.heading("序号", text="序号")
        self.tree.heading("姓名", text="姓名")
        self.tree.heading("权重", text="权重")
        self.tree.column("序号", width=60, anchor="center")
        self.tree.column("姓名", width=220, anchor="center")
        self.tree.column("权重", width=90, anchor="center")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 操作按钮
        btn_frame = ttk.Frame(group_label)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="🗑️ 删除选中", command=self.delete_student).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ 批量删除", command=self.batch_delete_students).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ 修改权重", command=self.update_weight).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📊 重置权重", command=self.reset_weights).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📂 批量导入", command=self.batch_import).pack(side=tk.LEFT, padx=2)
        
        # ===== 抽奖区域 =====
        lottery_frame = ttk.LabelFrame(main_frame, text="🎰 抽奖区域", padding="10")
        lottery_frame.pack(fill=tk.X, pady=5)
        
        # 显示参与人数
        self.count_label = ttk.Label(lottery_frame, text="参与人数：0 人")
        self.count_label.pack(pady=2)
        
        # 结果显示
        self.result_var = tk.StringVar(value="等待抽奖...")
        result_label = ttk.Label(lottery_frame, textvariable=self.result_var, 
                                 font=("Arial", 24, "bold"), foreground="red")
        result_label.pack(pady=10)
        
        # 抽奖按钮
        btn_lottery = ttk.Button(lottery_frame, text="🎯 开始抽奖", 
                                 command=self.start_lottery, width=20)
        btn_lottery.pack(pady=5)
        
        # 动画速度控制
        speed_frame = ttk.Frame(lottery_frame)
        speed_frame.pack(pady=5)
        ttk.Label(speed_frame, text="动画速度:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=50)
        speed_scale = ttk.Scale(speed_frame, from_=10, to=100, orient=tk.HORIZONTAL, 
                               variable=self.speed_var, length=150)
        speed_scale.pack(side=tk.LEFT, padx=5)
        self.speed_label = ttk.Label(speed_frame, text="50ms")
        self.speed_label.pack(side=tk.LEFT)
        speed_scale.configure(command=lambda v: self.speed_label.config(text=f"{int(float(v))}ms"))
        
        # ===== 历史记录 =====
        history_frame = ttk.LabelFrame(main_frame, text="📝 历史记录", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, height=6, state="disabled")
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(history_frame, text="清空历史", command=self.clear_history).pack(pady=2)
        
    def load_class_profiles(self):
        """从文件加载班级学生名单数据。"""
        if os.path.exists(self.class_file):
            try:
                with open(self.class_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.class_profiles = data
            except Exception:
                self.class_profiles = {}

        if not self.class_profiles:
            self.class_profiles = {
                "默认班级": {
                    "students": ["范留硕", "段硕", "黄廉体", "庹雅欣", "肖衔"],
                    "high_prob": {"肖衔": 100, "段硕": 100},
                    "normal_weight": 1,
                }
            }

        if self.current_class_name not in self.class_profiles:
            self.current_class_name = next(iter(self.class_profiles.keys()))

        profile = self.class_profiles[self.current_class_name]
        self.students = list(profile.get("students", []))
        self.high_prob = dict(profile.get("high_prob", {}))
        self.normal_weight = profile.get("normal_weight", 1)

    def save_class_profiles(self):
        """把当前班级数据保存到文件。"""
        with open(self.class_file, "w", encoding="utf-8") as f:
            json.dump(self.class_profiles, f, ensure_ascii=False, indent=2)

    def refresh_class_combo(self):
        """刷新班级选择下拉框。"""
        if hasattr(self, "class_combo"):
            values = list(self.class_profiles.keys())
            self.class_combo["values"] = values
            if self.current_class_name in values:
                self.class_var.set(self.current_class_name)
            elif values:
                self.current_class_name = values[0]
                self.class_var.set(self.current_class_name)

    def load_current_class(self):
        """加载当前班级的数据到界面。"""
        if self.current_class_name in self.class_profiles:
            profile = self.class_profiles[self.current_class_name]
            self.students = list(profile.get("students", []))
            self.high_prob = dict(profile.get("high_prob", {}))
            self.normal_weight = profile.get("normal_weight", 1)

    def save_current_class(self):
        """保存当前班级的学生名单和权重。"""
        if not self.current_class_name:
            return
        self.class_profiles[self.current_class_name] = {
            "students": list(self.students),
            "high_prob": dict(self.high_prob),
            "normal_weight": self.normal_weight,
        }
        self.save_class_profiles()

    def switch_class(self):
        """切换到另一个班级。"""
        target_name = self.class_var.get().strip()
        if not target_name or target_name == self.current_class_name:
            return

        self.save_current_class()
        self.current_class_name = target_name
        self.load_current_class()
        self.update_student_list()

    def create_class(self):
        """新建一个班级。"""
        class_name = self.class_name_entry.get().strip()
        if not class_name:
            messagebox.showwarning("警告", "请输入班级名称")
            return
        if class_name in self.class_profiles:
            messagebox.showwarning("警告", f"班级 '{class_name}' 已存在")
            return

        self.class_profiles[class_name] = {
            "students": [],
            "high_prob": {},
            "normal_weight": 1,
        }
        self.current_class_name = class_name
        self.students = []
        self.high_prob = {}
        self.normal_weight = 1
        self.save_class_profiles()
        self.refresh_class_combo()
        self.class_name_entry.delete(0, tk.END)
        self.update_student_list()
        messagebox.showinfo("成功", f"已创建班级：{class_name}")

    def delete_class(self):
        """删除当前班级。"""
        if len(self.class_profiles) <= 1:
            messagebox.showwarning("警告", "至少保留一个班级")
            return

        class_name = self.class_var.get().strip()
        if not class_name:
            return

        if messagebox.askyesno("确认删除", f"确定要删除班级 '{class_name}' 吗？"):
            del self.class_profiles[class_name]
            self.current_class_name = next(iter(self.class_profiles.keys()))
            self.load_current_class()
            self.save_class_profiles()
            self.refresh_class_combo()
            self.update_student_list()

    def get_student_weight(self, name):
        """获取学生的权重"""
        return self.high_prob.get(name, self.normal_weight)
    
    def update_student_list(self):
        """更新学生列表显示"""
        # 清空现有列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加学生
        for i, name in enumerate(self.students, 1):
            weight = self.get_student_weight(name)
            self.tree.insert("", tk.END, values=(i, name, weight))
        
        # 更新人数
        self.count_label.config(text=f"参与人数：{len(self.students)} 人")
    
    def add_student(self):
        """添加学生"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入学生姓名")
            return
        
        if name in self.students:
            messagebox.showwarning("警告", f"学生 '{name}' 已存在")
            return
        
        try:
            weight = int(self.weight_entry.get())
            if weight < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("警告", "权重必须为正整数")
            return
        
        self.students.append(name)
        if weight > self.normal_weight:
            self.high_prob[name] = weight

        self.save_current_class()
        self.update_student_list()
        self.name_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.weight_entry.insert(0, "1")
        messagebox.showinfo("成功", f"已添加学生：{name}（权重：{weight}）")
    
    def delete_student(self):
        """删除选中的学生（支持多选）"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的学生")
            return

        names = [self.tree.item(item)['values'][1] for item in selected]
        names_text = "、".join(names)

        if messagebox.askyesno("确认删除", f"确定要删除这 {len(names)} 名学生吗？\n\n{names_text}"):
            for name in names:
                if name in self.students:
                    self.students.remove(name)
                if name in self.high_prob:
                    del self.high_prob[name]
            self.save_current_class()
            self.update_student_list()
    
    def update_weight(self):
        """修改选中学生的权重"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要修改的学生")
            return
        
        item = self.tree.item(selected[0])
        name = item['values'][1]
        
        # 弹出输入框
        dialog = tk.Toplevel(self.root)
        dialog.title("修改权重")
        dialog.geometry("250x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"修改 '{name}' 的权重:").pack(pady=5)
        weight_var = tk.StringVar(value=str(self.get_student_weight(name)))
        entry = ttk.Entry(dialog, textvariable=weight_var, width=10)
        entry.pack(pady=5)
        
        def confirm():
            try:
                new_weight = int(weight_var.get())
                if new_weight < 1:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("警告", "权重必须为正整数")
                return
            
            # 更新权重
            if new_weight > self.normal_weight:
                self.high_prob[name] = new_weight
            elif name in self.high_prob:
                del self.high_prob[name]
            
            self.save_current_class()
            self.update_student_list()
            dialog.destroy()
            messagebox.showinfo("成功", f"已更新 '{name}' 的权重为 {new_weight}")
        
        ttk.Button(dialog, text="确认", command=confirm).pack(pady=5)
    
    def reset_weights(self):
        """重置所有权重为1"""
        if messagebox.askyesno("确认重置", "确定要将所有学生权重重置为1吗？"):
            self.high_prob.clear()
            self.save_current_class()
            self.update_student_list()
            messagebox.showinfo("成功", "所有权重已重置为1")

    def batch_delete_students(self):
        """批量删除学生（保留多选功能，避免误解）"""
        messagebox.showinfo("提示", "请在学生列表中按住 Ctrl 或 Shift 选择多个学生，然后点击“删除选中”按钮")
    
    def batch_import(self):
        """批量导入学生"""
        dialog = tk.Toplevel(self.root)
        dialog.title("批量导入")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="每行一个学生，格式：姓名,权重").pack(pady=5)
        ttk.Label(dialog, text="示例：张三,5").pack()
        
        text_area = scrolledtext.ScrolledText(dialog, height=12)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def import_data():
            content = text_area.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("警告", "请输入学生数据")
                return
            
            count = 0
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(',')
                name = parts[0].strip()
                if not name:
                    continue
                
                weight = 1
                if len(parts) > 1:
                    try:
                        weight = int(parts[1].strip())
                    except ValueError:
                        weight = 1
                
                if name not in self.students:
                    self.students.append(name)
                    if weight > self.normal_weight:
                        self.high_prob[name] = weight
                    count += 1
            
            self.save_current_class()
            self.update_student_list()
            dialog.destroy()
            messagebox.showinfo("成功", f"成功导入 {count} 名学生")
        
        ttk.Button(dialog, text="导入", command=import_data).pack(pady=5)
    
    def start_lottery(self):
        """开始抽奖"""
        if not self.students:
            messagebox.showwarning("警告", "学生列表为空，请先添加学生")
            return
        
        # 构建权重列表
        weights = [self.get_student_weight(name) for name in self.students]
        
        # 抽取中奖者
        winner = random.choices(self.students, weights=weights, k=1)[0]
        
        # 动画效果
        delay = int(self.speed_var.get()) / 1000
        steps = 20
        
        for i in range(steps):
            # 最后几步显示中奖者
            if i >= steps - 5:
                temp_name = winner
            else:
                temp_name = random.choice(self.students)
            self.result_var.set(f"🎉 {temp_name}")
            self.root.update()
            time.sleep(delay)
        
        # 最终结果
        self.result_var.set(f"🏆 {winner} 🏆")
        
        # 记录历史
        self.add_history(f"🎯 中奖者：{winner}")
    
    def add_history(self, text):
        """添加历史记录"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history_text.config(state="normal")
        self.history_text.insert(tk.END, f"[{timestamp}] {text}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state="disabled")
    
    def clear_history(self):
        """清空历史记录"""
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", tk.END)
        self.history_text.config(state="disabled")


if __name__ == "__main__":
    import time
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()
