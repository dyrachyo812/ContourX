"""
Contour Extractor
Зависимости: customtkinter, opencv-python, pillow, numpy
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image
import os
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG       = "#0e0e0e"
SURFACE  = "#161618"
CARD     = "#1c1c1f"
CARD2    = "#222226"
BORDER   = "#2e2e33"
ACCENT   = "#a855f7"
ACCENT_H = "#9333ea"
WHITE    = "#ffffff"
GRAY1    = "#a1a1aa"
GRAY2    = "#52525b"
GRAY3    = "#27272a"

WIN_W, WIN_H = 1060, 760
PREV_W, PREV_H = 455, 330

# ── Обработка ────────────────────────────────────────────

def load_safe(path):
    try:
        img = Image.open(path).convert("RGB")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except:
        return None

def process(cv_img, blur, low, high, method):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    k = max(1, int(blur) | 1)
    blurred = cv2.GaussianBlur(gray, (k, k), 0)
    if method == "canny":
        lo = min(int(low), int(high) - 5)
        edges = cv2.Canny(blurred, lo, int(high))
    else:
        block = max(11, (int(low) // 5) * 2 + 11)
        block = block if block % 2 == 1 else block + 1
        edges = cv2.adaptiveThreshold(blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, block, 4)
    return cv2.bitwise_not(edges)

def to_ctk(cv_gray, size):
    pil = Image.fromarray(cv_gray).convert("RGB")
    pil.thumbnail(size, Image.LANCZOS)
    return ctk.CTkImage(light_image=pil, dark_image=pil, size=pil.size)

def bgr_to_ctk(cv_bgr, size):
    pil = Image.fromarray(cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2RGB))
    pil.thumbnail(size, Image.LANCZOS)
    return ctk.CTkImage(light_image=pil, dark_image=pil, size=pil.size)

# ── Карточка превью ──────────────────────────────────────

class PreviewCard(ctk.CTkFrame):
    def __init__(self, master, label, **kw):
        super().__init__(master, fg_color=CARD, corner_radius=14,
                         border_width=1, border_color=BORDER, **kw)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(top, text=label,
                     font=("Segoe UI", 11, "bold"),
                     text_color=GRAY1).pack(side="left")
        self.badge = ctk.CTkLabel(top, text="",
                                  font=("Segoe UI", 9),
                                  text_color=ACCENT,
                                  fg_color=GRAY3,
                                  corner_radius=6,
                                  padx=8, pady=2)
        self.badge.pack(side="right")
        self.img_label = ctk.CTkLabel(self, text="",
                                      width=PREV_W, height=PREV_H,
                                      fg_color=SURFACE, corner_radius=8)
        self.img_label.pack(padx=12, pady=(0, 12))
        self._placeholder()

    def _placeholder(self):
        self.img_label.configure(image=None, text="Нет изображения",
                                 font=("Segoe UI", 12), text_color=GRAY2)

    def set_image(self, ctk_img, info=""):
        self.img_label.configure(image=ctk_img, text="")
        self.img_label._image = ctk_img
        if info:
            self.badge.configure(text=info)

# ── Ползунок ─────────────────────────────────────────────

class Slider(ctk.CTkFrame):
    def __init__(self, master, label, from_, to, initial, on_change, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._cb = on_change
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x")
        ctk.CTkLabel(head, text=label,
                     font=("Segoe UI", 10),
                     text_color=GRAY1).pack(side="left")
        self.val = ctk.CTkLabel(head, text=str(int(initial)),
                                font=("Segoe UI", 10, "bold"),
                                text_color=WHITE)
        self.val.pack(side="right")
        self.sl = ctk.CTkSlider(self, from_=from_, to=to,
                                progress_color=ACCENT,
                                button_color=WHITE,
                                button_hover_color="#c084fc",
                                fg_color=GRAY3,
                                command=self._on)
        self.sl.set(initial)
        self.sl.pack(fill="x", pady=(3, 0))

    def _on(self, v):
        self.val.configure(text=str(int(v)))
        if self._cb: self._cb()

    def get(self): return self.sl.get()

# ── Главное окно ─────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Contour Extractor")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{WIN_W}x{WIN_H}+{(sw-WIN_W)//2}+{(sh-WIN_H)//2}")
        self.original_cv = None
        self.result_cv   = None
        self.file_path   = ""
        self._busy       = False
        self._ui()

    def _ui(self):
        # ── Навбар ────────────────────────────────────────
        nav = ctk.CTkFrame(self, fg_color=SURFACE, height=52, corner_radius=0)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        logo = ctk.CTkFrame(nav, fg_color="transparent")
        logo.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(logo, text="Contour",
                     font=("Segoe UI", 16, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkLabel(logo, text="X",
                     font=("Segoe UI", 16, "bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(logo, text="   ·   превращаем фото в арт",
                     font=("Segoe UI", 10), text_color=GRAY2).pack(side="left")

        # ── Превью ────────────────────────────────────────
        previews = ctk.CTkFrame(self, fg_color="transparent")
        previews.pack(fill="x", padx=20, pady=(14, 0))
        self.card_orig   = PreviewCard(previews, "Оригинал")
        self.card_orig.pack(side="left", padx=(0, 8))
        self.card_result = PreviewCard(previews, "Контур")
        self.card_result.pack(side="left")

        # ── Нижняя панель ─────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14,
                              border_width=1, border_color=BORDER)
        bottom.pack(fill="x", padx=20, pady=12)

        # Одна строка из трёх секций
        row = ctk.CTkFrame(bottom, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=16)

        # ── Секция 1: Кнопки (фиксированная ширина) ───────
        s1 = ctk.CTkFrame(row, fg_color="transparent", width=185)
        s1.pack(side="left", fill="y", padx=(0, 18))
        s1.pack_propagate(False)

        self.btn_load = ctk.CTkButton(
            s1, text="↑  Загрузить фото",
            font=("Segoe UI", 12, "bold"),
            height=40, fg_color=ACCENT, hover_color=ACCENT_H,
            text_color=WHITE, corner_radius=10, command=self._load)
        self.btn_load.pack(fill="x", pady=(0, 8))

        self.btn_save = ctk.CTkButton(
            s1, text="↓  Сохранить контур",
            font=("Segoe UI", 12, "bold"),
            height=40, fg_color=CARD2, text_color=GRAY1,
            hover_color=GRAY3, border_width=1, border_color=BORDER,
            corner_radius=10, state="disabled", command=self._save)
        self.btn_save.pack(fill="x")

        # ── Разделитель ────────────────────────────────────
        ctk.CTkFrame(row, fg_color=BORDER, width=1).pack(
            side="left", fill="y", padx=(0, 18))

        # ── Секция 2: Алгоритм (фиксированная ширина) ─────
        s2 = ctk.CTkFrame(row, fg_color="transparent", width=180)
        s2.pack(side="left", fill="y", anchor="n", padx=(0, 18))
        s2.pack_propagate(False)

        ctk.CTkLabel(s2, text="АЛГОРИТМ",
                     font=("Segoe UI", 9, "bold"), text_color=GRAY2).pack(anchor="w")

        self.method_var = ctk.StringVar(value="Canny")
        ctk.CTkSegmentedButton(
            s2, values=["Canny", "Adaptive"],
            variable=self.method_var,
            font=("Segoe UI", 11), width=175,
            fg_color=GRAY3, selected_color=ACCENT,
            selected_hover_color=ACCENT_H,
            unselected_color=GRAY3, unselected_hover_color=CARD2,
            text_color=WHITE,
            command=lambda _: self._change()
        ).pack(anchor="w", pady=(6, 0))

        ctk.CTkLabel(s2, text="Canny — универсальный\nAdaptive — сложное освещение",
                     font=("Segoe UI", 9), text_color=GRAY2,
                     justify="left").pack(anchor="w", pady=(6, 0))

        # ── Разделитель ────────────────────────────────────
        ctk.CTkFrame(row, fg_color=BORDER, width=1).pack(
            side="left", fill="y", padx=(0, 18))

        # ── Секция 3: Три слайдера вертикально ────────────
        # fill="both" + expand=True — занимает ВЕСЬ остаток ширины
        s3 = ctk.CTkFrame(row, fg_color="transparent")
        s3.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(s3, text="ПАРАМЕТРЫ ФИЛЬТРА",
                     font=("Segoe UI", 9, "bold"), text_color=GRAY2).pack(anchor="w", pady=(0, 8))

        self.sl_blur = Slider(s3, "Размытие",      1,   15,   3, self._change)
        self.sl_blur.pack(fill="x", pady=(0, 8))

        self.sl_low  = Slider(s3, "Нижний порог",  0,  200,  50, self._change)
        self.sl_low.pack(fill="x", pady=(0, 8))

        self.sl_high = Slider(s3, "Верхний порог", 50, 400, 150, self._change)
        self.sl_high.pack(fill="x")

        # ── Статус ────────────────────────────────────────
        self.status_lbl = ctk.CTkLabel(
            bottom, text="Загрузите изображение для начала работы",
            font=("Segoe UI", 9), text_color=GRAY2)
        self.status_lbl.pack(pady=(0, 10))

    # ── Логика ──────────────────────────────────────────

    def _load(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Все изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                       ("Все файлы", "*.*")])
        if not path: return
        self.file_path = path
        cv_img = load_safe(path)
        if cv_img is None:
            messagebox.showerror("Ошибка", f"Не удалось открыть:\n{path}")
            return
        self.original_cv = cv_img
        h, w = cv_img.shape[:2]
        self.card_orig.set_image(bgr_to_ctk(cv_img, (PREV_W, PREV_H)), f"{w}×{h}")
        self.status_lbl.configure(text=f"Файл: {os.path.basename(path)}   •   {w}×{h} px")
        self._run()
        self.btn_save.configure(state="normal", text_color=WHITE)

    def _change(self):
        if self.original_cv is not None: self._run()

    def _run(self):
        if self._busy: return
        self._busy = True
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        method = "canny" if self.method_var.get() == "Canny" else "adaptive"
        result = process(self.original_cv,
                         self.sl_blur.get(), self.sl_low.get(),
                         self.sl_high.get(), method)
        self.result_cv = result
        img = to_ctk(result, (PREV_W, PREV_H))
        self.after(0, lambda: self.card_result.set_image(img, "готово ✓"))
        self._busy = False

    def _save(self):
        if self.result_cv is None: return
        base = os.path.splitext(os.path.basename(self.file_path))[0]
        path = filedialog.asksaveasfilename(
            title="Сохранить контур",
            initialfile=f"{base}_contour.png",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Все файлы", "*.*")])
        if not path: return
        try:
            Image.fromarray(self.result_cv).save(path)
            self.status_lbl.configure(text=f"Сохранено: {os.path.basename(path)}")
            messagebox.showinfo("Готово", f"Файл сохранён:\n{path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    App().mainloop()
