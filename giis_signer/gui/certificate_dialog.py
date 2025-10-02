"""
Диалог выбора сертификата для GUI приложения
"""

import customtkinter as ctk
from typing import Optional, List
from giis_signer.gui.certificate_manager import CertificateInfo, CertificateManager


class CertificateDialog(ctk.CTkToplevel):
    """
    Диалоговое окно для выбора сертификата из списка
    """

    def __init__(self, parent, certificate_manager: CertificateManager):
        """
        Инициализация диалога

        Args:
            parent: Родительское окно
            certificate_manager: Менеджер сертификатов
        """
        super().__init__(parent)

        self.certificate_manager = certificate_manager
        self.selected_certificate: Optional[CertificateInfo] = None

        # Настройка окна
        self.title("Выбор сертификата")
        self.geometry("700x500")
        self.resizable(True, True)

        # Центрируем окно относительно родителя
        self.transient(parent)
        self.grab_set()

        # Создаем интерфейс
        self._create_widgets()

        # Загружаем сертификаты
        self._load_certificates()

        # Фокусируемся на окне
        self.focus()

    def _create_widgets(self):
        """Создание виджетов диалога"""
        # Заголовок
        title_label = ctk.CTkLabel(
            self,
            text="Выберите сертификат для подписания",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(20, 10), padx=20)

        # Фрейм для списка
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Скроллбар для списка
        self.cert_listbox = ctk.CTkScrollableFrame(list_frame)
        self.cert_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Фрейм для информации о сертификате
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(pady=10, padx=20, fill="x")

        info_label = ctk.CTkLabel(
            info_frame,
            text="Информация о сертификате:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        info_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.info_text = ctk.CTkTextbox(info_frame, height=100)
        self.info_text.pack(fill="x", padx=10, pady=(0, 10))
        self.info_text.configure(state="disabled")

        # Фрейм для кнопок
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10, padx=20, fill="x")

        # Кнопка "Обновить"
        refresh_button = ctk.CTkButton(
            button_frame,
            text="Обновить список",
            command=self._refresh_certificates,
            width=150
        )
        refresh_button.pack(side="left", padx=5)

        # Кнопка "Выбрать"
        select_button = ctk.CTkButton(
            button_frame,
            text="Выбрать",
            command=self._on_select,
            width=150
        )
        select_button.pack(side="right", padx=5)

        # Кнопка "Отмена"
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=self._on_cancel,
            width=150,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_button.pack(side="right", padx=5)

        # Переменная для хранения выбранной радиокнопки
        self.selected_cert_var = ctk.StringVar(value="")

    def _load_certificates(self):
        """Загрузка списка сертификатов"""
        try:
            certificates = self.certificate_manager.get_certificates(refresh=False)

            if not certificates:
                no_certs_label = ctk.CTkLabel(
                    self.cert_listbox,
                    text="Сертификаты не найдены",
                    text_color="gray"
                )
                no_certs_label.pack(pady=20)
                return

            for cert in certificates:
                self._add_certificate_item(cert)

        except Exception as e:
            error_label = ctk.CTkLabel(
                self.cert_listbox,
                text=f"Ошибка при загрузке сертификатов:\n{str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)

    def _add_certificate_item(self, cert: CertificateInfo):
        """
        Добавить элемент сертификата в список

        Args:
            cert: Информация о сертификате
        """
        # Фрейм для каждого сертификата
        cert_frame = ctk.CTkFrame(self.cert_listbox)
        cert_frame.pack(fill="x", pady=2, padx=5)

        # Радиокнопка с именем сертификата
        radio = ctk.CTkRadioButton(
            cert_frame,
            text=cert.get_display_name(),
            variable=self.selected_cert_var,
            value=cert.thumbprint,
            command=lambda: self._on_certificate_selected(cert)
        )
        radio.pack(side="left", padx=10, pady=10)

        # Индикатор действительности
        if cert.is_valid:
            status_label = ctk.CTkLabel(
                cert_frame,
                text="✓ Действителен",
                text_color="green",
                width=100
            )
        else:
            status_label = ctk.CTkLabel(
                cert_frame,
                text="✗ Недействителен",
                text_color="red",
                width=100
            )
        status_label.pack(side="right", padx=10)

    def _on_certificate_selected(self, cert: CertificateInfo):
        """
        Обработчик выбора сертификата

        Args:
            cert: Выбранный сертификат
        """
        # Обновляем информационное поле
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", cert.get_tooltip())
        self.info_text.configure(state="disabled")

    def _refresh_certificates(self):
        """Обновить список сертификатов"""
        # Очищаем текущий список
        for widget in self.cert_listbox.winfo_children():
            widget.destroy()

        # Сбрасываем выбор
        self.selected_cert_var.set("")
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.configure(state="disabled")

        # Загружаем заново
        self._load_certificates()

    def _on_select(self):
        """Обработчик кнопки "Выбрать" """
        thumbprint = self.selected_cert_var.get()

        if not thumbprint:
            # Показываем предупреждение
            warning_window = ctk.CTkToplevel(self)
            warning_window.title("Предупреждение")
            warning_window.geometry("300x150")
            warning_window.transient(self)
            warning_window.grab_set()

            label = ctk.CTkLabel(
                warning_window,
                text="Пожалуйста, выберите сертификат",
                font=ctk.CTkFont(size=14)
            )
            label.pack(pady=20)

            ok_button = ctk.CTkButton(
                warning_window,
                text="OK",
                command=warning_window.destroy,
                width=100
            )
            ok_button.pack(pady=10)

            return

        # Находим выбранный сертификат
        self.selected_certificate = self.certificate_manager.find_certificate_by_thumbprint(thumbprint)
        self.destroy()

    def _on_cancel(self):
        """Обработчик кнопки "Отмена" """
        self.selected_certificate = None
        self.destroy()

    def get_selected_certificate(self) -> Optional[CertificateInfo]:
        """
        Получить выбранный сертификат

        Returns:
            CertificateInfo или None если не выбран
        """
        return self.selected_certificate
