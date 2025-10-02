"""
Toast-уведомления для GUI приложения
Неблокирующие всплывающие уведомления в стиле push-notifications
"""

import customtkinter as ctk
from typing import Literal


class Toast(ctk.CTkFrame):
    """Неблокирующее всплывающее уведомление"""

    def __init__(
        self,
        parent,
        message: str,
        duration: int = 3000,
        type: Literal["success", "info", "warning", "error"] = "info"
    ):
        super().__init__(parent, corner_radius=10)

        self.message = message
        self.duration = duration

        # Более яркие и приятные цвета для уведомлений
        colors = {
            "success": "#28a745",  # приятный зеленый
            "info": "#17a2b8",     # яркий голубой
            "warning": "#ffc107",  # яркий желтый
            "error": "#dc3545"     # яркий красный
        }

        # Иконки для типов
        icons = {
            "success": "✅",
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌"
        }

        # Цвет текста в зависимости от типа
        text_colors = {
            "success": "white",
            "info": "white",
            "warning": "#212529",  # темный текст для желтого фона
            "error": "white"
        }

        fg_color = colors.get(type, colors["info"])
        icon = icons.get(type, icons["info"])
        text_color = text_colors.get(type, "white")

        self.configure(fg_color=fg_color)

        # Иконка
        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=18),
            width=30,
            text_color=text_color
        )
        icon_label.pack(side="left", padx=(15, 5), pady=10)

        # Сообщение
        msg_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=300,
            text_color=text_color
        )
        msg_label.pack(side="left", padx=(5, 15), pady=10, fill="x", expand=True)

        # Автоматическое скрытие
        self.after(duration, self.hide)

    def show(self, x: int, y: int):
        """Показать уведомление в указанной позиции"""
        self.place(x=x, y=y)

    def hide(self):
        """Скрыть уведомление с анимацией"""
        # Плавное исчезновение (опционально, зависит от возможностей CTk)
        self.place_forget()
        self.destroy()


class ToastManager:
    """Менеджер toast-уведомлений"""

    def __init__(self, parent):
        self.parent = parent
        self.toasts = []
        self.y_offset = 20  # Начальный отступ сверху
        self.spacing = 10   # Расстояние между уведомлениями
        self.max_toasts = 3  # Максимальное количество уведомлений

    def show(
        self,
        message: str,
        type: Literal["success", "info", "warning", "error"] = "info",
        duration: int = 3000
    ):
        """Показать toast-уведомление"""
        # Если достигнут лимит - удаляем самое старое (последнее в списке)
        if len(self.toasts) >= self.max_toasts:
            oldest_toast = self.toasts[-1]  # Последнее = самое старое (внизу)
            oldest_toast.hide()
            self.toasts.remove(oldest_toast)

        # Создаем toast
        toast = Toast(self.parent, message, duration, type)

        # Вычисляем позицию (правый верхний угол)
        window_width = self.parent.winfo_width()
        toast_width = 350
        x = window_width - toast_width - 20

        # Новое уведомление всегда вверху (y_offset)
        y = self.y_offset

        # Показываем
        toast.show(x, y)

        # Добавляем в начало списка (новые - сверху)
        self.toasts.insert(0, toast)

        # Перепозиционируем все уведомления
        self._reposition_toasts()

        # Удаляем из списка после скрытия
        self.parent.after(duration, lambda: self._remove_toast(toast))

    def _remove_toast(self, toast):
        """Удалить toast из списка"""
        if toast in self.toasts:
            self.toasts.remove(toast)
            # Перепозиционируем оставшиеся уведомления
            self._reposition_toasts()

    def _reposition_toasts(self):
        """Перепозиционировать все уведомления"""
        window_width = self.parent.winfo_width()
        toast_width = 350
        x = window_width - toast_width - 20

        for index, toast in enumerate(self.toasts):
            y = self.y_offset + index * (60 + self.spacing)
            toast.place(x=x, y=y)

    def success(self, message: str, duration: int = 3000):
        """Показать success-уведомление"""
        self.show(message, "success", duration)

    def info(self, message: str, duration: int = 3000):
        """Показать info-уведомление"""
        self.show(message, "info", duration)

    def warning(self, message: str, duration: int = 3000):
        """Показать warning-уведомление"""
        self.show(message, "warning", duration)

    def error(self, message: str, duration: int = 3000):
        """Показать error-уведомление"""
        self.show(message, "error", duration)
