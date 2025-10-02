"""
Главное окно GUI приложения для подписания XML документов
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import re
from pathlib import Path
from typing import Optional

from ..cryptopro_signer import CryptoProSigner, CryptoProException
from ..xml_signer import XMLSigner, XMLSignerException
from .certificate_manager import CertificateManager, CertificateInfo
from .certificate_dialog import CertificateDialog
from .config import Config
from .toast import ToastManager


class GIISSignerApp(ctk.CTk):
    """
    Главное окно приложения GIIS Signer
    """

    def __init__(self):
        super().__init__()

        # Инициализация менеджеров
        self.config = Config()
        self.certificate_manager = CertificateManager()
        self.selected_certificate: Optional[CertificateInfo] = None

        # Настройка окна
        self.title("GIIS DМДК XML Signer")
        self.geometry("1000x700")

        # Инициализация toast-менеджера (после создания окна)
        self.toast = ToastManager(self)

        # Восстанавливаем геометрию окна если была сохранена
        saved_geometry = self.config.get_window_geometry()
        if saved_geometry:
            try:
                self.geometry(saved_geometry)
            except:
                pass

        # Устанавливаем тему
        ctk.set_appearance_mode(self.config.get_theme())

        # Создаем интерфейс
        self._create_widgets()

        # Загружаем последний использованный сертификат
        self._load_last_certificate()

        # Обработчик закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        """Создание виджетов главного окна"""
        # === Заголовок ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="GIIS DМДК XML Signer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")

        # Кнопка настроек темы
        theme_button = ctk.CTkButton(
            header_frame,
            text="🌓 Тема",
            command=self._toggle_theme,
            width=80
        )
        theme_button.pack(side="right", padx=5)

        # === Фрейм выбора сертификата ===
        cert_frame = ctk.CTkFrame(self)
        cert_frame.pack(fill="x", padx=20, pady=10)

        cert_label = ctk.CTkLabel(
            cert_frame,
            text="Сертификат:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cert_label.pack(side="left", padx=10, pady=10)

        self.cert_display_label = ctk.CTkLabel(
            cert_frame,
            text="Не выбран",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.cert_display_label.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        select_cert_button = ctk.CTkButton(
            cert_frame,
            text="Выбрать сертификат",
            command=self._select_certificate,
            width=180
        )
        select_cert_button.pack(side="right", padx=10, pady=10)

        # === Главная рабочая область ===
        work_frame = ctk.CTkFrame(self)
        work_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Левая панель - входной XML
        left_panel = ctk.CTkFrame(work_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        input_header = ctk.CTkFrame(left_panel, fg_color="transparent")
        input_header.pack(fill="x", padx=10, pady=10)

        input_label = ctk.CTkLabel(
            input_header,
            text="Входной XML:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        input_label.pack(side="left")

        input_import_button = ctk.CTkButton(
            input_header,
            text="📂 Импорт",
            command=self._import_file,
            width=100
        )
        input_import_button.pack(side="right", padx=2)

        input_clear_button = ctk.CTkButton(
            input_header,
            text="🗑 Очистить",
            command=self._clear_input,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        input_clear_button.pack(side="right", padx=2)

        # Поле для element_id
        element_id_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        element_id_frame.pack(fill="x", padx=10, pady=(0, 10))

        element_id_label = ctk.CTkLabel(
            element_id_frame,
            text="Element ID для подписания:",
            font=ctk.CTkFont(size=12)
        )
        element_id_label.pack(side="left", padx=(0, 10))

        self.element_id_entry = ctk.CTkEntry(
            element_id_frame,
            placeholder_text="Авто-определение из XML (например: body)"
        )
        self.element_id_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Кнопка обновления element_id
        self.refresh_element_id_button = ctk.CTkButton(
            element_id_frame,
            text="🔄",
            command=self._refresh_element_id,
            width=30,
            state="disabled",
            fg_color="gray",
            hover_color="darkgray"
        )
        self.refresh_element_id_button.pack(side="left")

        # Привязываем событие изменения element_id для активации кнопки
        self.element_id_entry.bind("<KeyRelease>", self._on_element_id_changed)

        self.input_textbox = ctk.CTkTextbox(left_panel, wrap="none")
        self.input_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Привязываем событие изменения текста для авто-определения element_id
        self.input_textbox.bind("<<Modified>>", self._on_input_text_changed)

        # Правая панель - выходной XML
        right_panel = ctk.CTkFrame(work_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        output_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        output_header.pack(fill="x", padx=10, pady=10)

        output_label = ctk.CTkLabel(
            output_header,
            text="Подписанный XML:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_label.pack(side="left")

        output_export_button = ctk.CTkButton(
            output_header,
            text="💾 Экспорт",
            command=self._export_file,
            width=100
        )
        output_export_button.pack(side="right", padx=2)

        output_copy_button = ctk.CTkButton(
            output_header,
            text="📋 Копировать",
            command=self._copy_output,
            width=100
        )
        output_copy_button.pack(side="right", padx=2)

        output_clear_button = ctk.CTkButton(
            output_header,
            text="🗑 Очистить",
            command=self._clear_output,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        )
        output_clear_button.pack(side="right", padx=2)

        self.output_textbox = ctk.CTkTextbox(right_panel, wrap="none")
        self.output_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # === Нижняя панель с кнопками действий ===
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(10, 20))

        clear_all_button = ctk.CTkButton(
            action_frame,
            text="Очистить всё",
            command=self._clear_all,
            width=150,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_all_button.pack(side="left", padx=5)

        sign_button = ctk.CTkButton(
            action_frame,
            text="✍ Подписать",
            command=self._sign_xml,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        sign_button.pack(side="right", padx=5)

    def _select_certificate(self):
        """Открыть диалог выбора сертификата"""
        dialog = CertificateDialog(self, self.certificate_manager)
        self.wait_window(dialog)

        selected = dialog.get_selected_certificate()
        if selected:
            self.selected_certificate = selected
            self.cert_display_label.configure(
                text=selected.get_display_name(),
                text_color="green"
            )
            # Сохраняем выбор
            self.config.set_last_certificate_thumbprint(selected.thumbprint)

    def _load_last_certificate(self):
        """Загрузить последний использованный сертификат"""
        thumbprint = self.config.get_last_certificate_thumbprint()
        if thumbprint:
            cert = self.certificate_manager.find_certificate_by_thumbprint(thumbprint)
            if cert:
                self.selected_certificate = cert
                self.cert_display_label.configure(
                    text=cert.get_display_name(),
                    text_color="green"
                )

    def _extract_element_id(self, xml_content: str) -> Optional[str]:
        """
        Извлекает element_id из XML по паттерну <ns:RequestData id="...">

        Args:
            xml_content: содержимое XML

        Returns:
            element_id или None если не найден
        """
        # Паттерн для поиска id в RequestData или любом другом элементе
        # Ищем конструкцию вида id="значение"
        pattern = r'<[^>]*:RequestData[^>]+id\s*=\s*["\']([^"\']+)["\']'
        match = re.search(pattern, xml_content)

        if match:
            return match.group(1)

        # Если не нашли в RequestData, ищем любой элемент с id
        pattern_generic = r'id\s*=\s*["\']([^"\']+)["\']'
        match = re.search(pattern_generic, xml_content)

        if match:
            return match.group(1)

        return None

    def _on_element_id_changed(self, event=None):
        """Обработчик изменения поля element_id для активации кнопки обновления"""
        # Получаем текущее значение в поле и из XML
        current_value = self.element_id_entry.get().strip()
        content = self.input_textbox.get("1.0", "end-1c").strip()

        if content:
            xml_value = self._extract_element_id(content)

            # Если значение совпадает с XML - кнопка неактивна
            if current_value == xml_value:
                self.refresh_element_id_button.configure(
                    state="disabled",
                    fg_color="gray",
                    hover_color="darkgray"
                )
            else:
                # Если значение отличается - кнопка активна
                self.refresh_element_id_button.configure(
                    state="normal",
                    fg_color="green",
                    hover_color="darkgreen"
                )
        else:
            # Если нет XML - деактивируем кнопку
            self.refresh_element_id_button.configure(
                state="disabled",
                fg_color="gray",
                hover_color="darkgray"
            )

    def _refresh_element_id(self):
        """Обновление element_id из XML"""
        content = self.input_textbox.get("1.0", "end-1c").strip()

        if content:
            element_id = self._extract_element_id(content)
            if element_id:
                self.element_id_entry.delete(0, "end")
                self.element_id_entry.insert(0, element_id)

                # Деактивируем кнопку после обновления
                self.refresh_element_id_button.configure(
                    state="disabled",
                    fg_color="gray",
                    hover_color="darkgray"
                )

                self.toast.success(f"Element ID обновлен: {element_id}")
            else:
                self.toast.warning("Element ID не найден в XML")
        else:
            self.toast.warning("Введите XML для определения Element ID")

    def _on_input_text_changed(self, event=None):
        """Обработчик изменения входного текста для авто-определения element_id"""
        # Сбрасываем флаг Modified для предотвращения рекурсии
        self.input_textbox.edit_modified(False)

        # Получаем текст
        content = self.input_textbox.get("1.0", "end-1c").strip()

        # Если поле element_id пустое, пробуем авто-определить
        if content and not self.element_id_entry.get():
            element_id = self._extract_element_id(content)
            if element_id:
                self.element_id_entry.delete(0, "end")
                self.element_id_entry.insert(0, element_id)

                # Кнопка остается неактивной при первом авто-определении
                self.refresh_element_id_button.configure(
                    state="disabled",
                    fg_color="gray",
                    hover_color="darkgray"
                )

    def _import_file(self):
        """Импорт XML файла"""
        last_dir = self.config.get_last_input_dir()
        filename = filedialog.askopenfilename(
            title="Выберите XML файл",
            initialdir=last_dir,
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.input_textbox.delete("1.0", "end")
                    self.input_textbox.insert("1.0", content)

                # Сохраняем директорию
                self.config.set_last_input_dir(os.path.dirname(filename))

                # Авто-определяем element_id
                element_id = self._extract_element_id(content)
                if element_id:
                    self.element_id_entry.delete(0, "end")
                    self.element_id_entry.insert(0, element_id)

                    # Деактивируем кнопку обновления при импорте
                    self.refresh_element_id_button.configure(
                        state="disabled",
                        fg_color="gray",
                        hover_color="darkgray"
                    )

                # Toast-уведомление об успешном импорте
                filename_short = os.path.basename(filename)
                self.toast.success(f"Файл импортирован: {filename_short}")

            except Exception as e:
                self.toast.error(f"Не удалось прочитать файл: {str(e)}")

    def _export_file(self):
        """Экспорт подписанного XML"""
        content = self.output_textbox.get("1.0", "end-1c")

        if not content.strip():
            self.toast.warning("Нет данных для экспорта")
            return

        last_dir = self.config.get_last_output_dir()
        filename = filedialog.asksaveasfilename(
            title="Сохранить подписанный XML",
            initialdir=last_dir,
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Сохраняем директорию
                self.config.set_last_output_dir(os.path.dirname(filename))

                filename_short = os.path.basename(filename)
                self.toast.success(f"Файл сохранен: {filename_short}")

            except Exception as e:
                self.toast.error(f"Не удалось сохранить файл: {str(e)}")

    def _copy_output(self):
        """Копировать результат в буфер обмена"""
        content = self.output_textbox.get("1.0", "end-1c")

        if not content.strip():
            self.toast.warning("Нет данных для копирования")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.toast.success("Текст скопирован в буфер обмена")

    def _clear_input(self):
        """Очистить входное поле"""
        self.input_textbox.delete("1.0", "end")
        self.element_id_entry.delete(0, "end")

        # Деактивируем кнопку обновления при очистке
        self.refresh_element_id_button.configure(
            state="disabled",
            fg_color="gray",
            hover_color="darkgray"
        )

    def _clear_output(self):
        """Очистить выходное поле"""
        self.output_textbox.delete("1.0", "end")

    def _clear_all(self):
        """Очистить оба поля"""
        self._clear_input()
        self._clear_output()

    def _sign_xml(self):
        """Подписать XML документ"""
        # Проверяем выбор сертификата
        if not self.selected_certificate:
            self.toast.warning("Пожалуйста, выберите сертификат для подписания")
            return

        # Получаем входной XML
        input_xml = self.input_textbox.get("1.0", "end-1c").strip()

        if not input_xml:
            self.toast.warning("Введите XML для подписания")
            return

        # Получаем element_id (используем значение из поля или дефолтное "body")
        element_id = self.element_id_entry.get().strip()

        if not element_id:
            # Пробуем авто-определить
            element_id = self._extract_element_id(input_xml)
            if element_id:
                self.element_id_entry.delete(0, "end")
                self.element_id_entry.insert(0, element_id)
            else:
                # Используем дефолтное значение
                element_id = "body"
                self.toast.info(f"Используется Element ID по умолчанию: '{element_id}'")

        try:
            # Создаем подписанта
            signer = CryptoProSigner(thumbprint=self.selected_certificate.thumbprint)
            signer.find_certificate()

            # Создаем XML подписанта
            xml_signer = XMLSigner(signer)

            # Подписываем
            signed_xml = xml_signer.sign_soap_request(
                input_xml,
                element_id=element_id,
                signature_element_name="CallerSignature"
            )

            # Выводим результат
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", signed_xml)

            self.toast.success(f"XML успешно подписан! Element ID: {element_id}")

        except (CryptoProException, XMLSignerException) as e:
            self.toast.error(f"Ошибка подписания: {str(e)}", duration=5000)
        except Exception as e:
            self.toast.error(f"Неожиданная ошибка: {str(e)}", duration=5000)

    def _toggle_theme(self):
        """Переключить тему оформления"""
        current = ctk.get_appearance_mode()
        new_theme = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme)
        self.config.set_theme(new_theme.lower())

    def _on_closing(self):
        """Обработчик закрытия окна"""
        # Сохраняем геометрию окна
        self.config.set_window_geometry(self.geometry())
        self.destroy()


def main():
    """Точка входа для GUI приложения"""
    app = GIISSignerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
