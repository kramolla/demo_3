import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QMessageBox, QLineEdit,
    QComboBox, QDialog
)
from db.connection import engine
from sqlalchemy.orm import Session
session = Session(engine)
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import Qt
from sqlalchemy import func
from db.models.partner import PartnerModel
from db.models.order import OrderModel
from db.models.product import ProductModel

class PartnerCard(QFrame):
    """Карточка партнёра с основными данными и действиями."""
    def __init__(self, partner, discount, parent=None):
        super().__init__(parent)
        self.partner = partner
        self.setObjectName("partnerCard")
        self.setStyleSheet(
            "#partnerCard  { \n"
                "margin: 10px; \n"
                "border: 2px solid black;\n"
            "}"
        )
        self.layout = QHBoxLayout(self)

        # Левая часть карточки с основными данными.
        left_layout = QVBoxLayout()
        name_label = QLabel(f"{partner.partner_type} | {partner.name}")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        director_label = QLabel(f"Директор: {partner.director}")
        phone_label = QLabel(f"{partner.phone}")
        rating_label = QLabel(f"Рейтинг: {partner.rating}")

        left_layout.addWidget(name_label)
        left_layout.addWidget(director_label)
        left_layout.addWidget(phone_label)
        left_layout.addWidget(rating_label)

        # Правая часть карточки с кнопками действий.
        right_layout = QVBoxLayout()
        discount_label = QLabel(f"{discount}%")
        discount_label.setFont(QFont("Arial", 16, QFont.Bold))
        discount_label.setStyleSheet("color: #66bb6a;")
        discount_label.setAlignment(Qt.AlignRight)

        # Кнопки для просмотра истории и редактирования.
        button_layout = QHBoxLayout()
        self.show_history_button = QPushButton("История продаж")
        self.show_history_button.setCursor(Qt.PointingHandCursor)
        self.edit_partner_button = QPushButton("Изменить партнёра")
        self.edit_partner_button.setCursor(Qt.PointingHandCursor)

        button_layout.addWidget(self.show_history_button)
        button_layout.addWidget(self.edit_partner_button)

        right_layout.addWidget(discount_label)
        right_layout.addLayout(button_layout)

        # Добавляем оба лейаута в основной.
        self.layout.addLayout(left_layout)
        self.layout.addLayout(right_layout)

class PartnerList(QWidget):
    """Основное окно с отображением списка партнёров."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Список партнёров")
        self.setGeometry(100, 100, 800, 600)
        self.history_windows = []  # Храним открытые окна истории.
        self.content_layout = None  # Лейаут для карточек партнёра.

        main_layout = QVBoxLayout(self)

        # Заголовок окна.
        header_layout = QHBoxLayout(self)
        header_layout.setAlignment(Qt.AlignCenter)

        title_icon_label = QLabel()
        title_icon_label.setPixmap(QPixmap("./icons/Master_pol.png").scaled(100, 100))
        title_label = QLabel("Партнёры")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title_icon_label)
        header_layout.addWidget(title_label)
        main_layout.addLayout(header_layout)

        # Прокручиваемая область для карточек партнёров.
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        self.refresh_list()  # Загружаем список партнёров при старте.

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Кнопка добавления нового партнёра.
        add_partner_button = QPushButton("Добавить партнёра")
        add_partner_button.clicked.connect(self.add_partner)
        main_layout.addWidget(add_partner_button)

        self.setLayout(main_layout)

        # Настройка тёмной темы для окна.
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: #67BA80;
                border-radius: 5px;
                color: #e0e0e0;
                padding: 5px 15px;
                border: none;
            }
        """)

    def show_history(self, partner_id):
        """Открытие окна истории продаж для конкретного партнёра."""
        history_window = PartnerHistory(partner_id)
        self.history_windows.append(history_window)  # Сохраняем ссылку на окно.
        history_window.show()
        history_window.destroyed.connect(lambda: self.cleanup_history_windows(history_window))

    def cleanup_history_windows(self, window):
        """Удаление закрытого окна истории из списка."""
        if window in self.history_windows:
            self.history_windows.remove(window)

    def add_partner(self):
        """Открытие окна для добавления нового партнёра."""
        dialog = EditPartnerDialog()
        if dialog.exec():
            self.refresh_list()  # Обновляем список после добавления.

    def edit_partner(self, partner):
        """Открытие окна для редактирования информации о партнёре."""
        dialog = EditPartnerDialog(partner)
        if dialog.exec():
            self.refresh_list()  # Обновляем список после изменения.

    def refresh_list(self):
        """Обновление списка партнёров."""
        # Удаляем старые виджеты из лейаута.
        while self.content_layout.count() > 0:
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Перезагружаем данные из базы.
        self.partners = session.query(PartnerModel).order_by(PartnerModel.id).all()

        # Создаём карточки заново.
        for partner in self.partners:
            discount = calculate_discount(partner.id)  # Рассчитываем скидку для партнёра.
            card = PartnerCard(partner=partner, discount=discount)
            self.content_layout.addWidget(card)

            # Подключаем сигналы для кнопок.
            card.show_history_button.clicked.connect(lambda _, p=partner: self.show_history(p.id))
            card.edit_partner_button.clicked.connect(lambda _, p=partner: self.edit_partner(p))

# Функция для расчёта скидки на основе общего количества заказов партнёра.
def calculate_discount(partner_id):
    # Получаем общее количество заказанных единиц продукции для данного партнёра.
    total_quantity = session.query(func.sum(OrderModel.quantity)).filter(OrderModel.partner_id == partner_id).scalar() or 0
    # Логика определения скидки в зависимости от объёма.
    if total_quantity > 300000:
        return 15
    elif total_quantity > 50000:
        return 10
    elif total_quantity > 10000:
        return 5
    else:
        return 0

class EditPartnerDialog(QDialog):
    """Окно для добавления/редактирования информации о партнёре."""
    def __init__(self, partner=None, parent=None):
        super().__init__(parent)
        self.partner = partner
        self.setWindowIcon(QIcon("./icons/Master_pol.ico"))
        self.setWindowTitle("Добавить/Редактировать партнёра")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout(self)

        # Поля ввода для информации о партнёре
        self.type_input = QComboBox()
        self.type_input.addItems(["ООО", "ОАО", "ЗАО", "ПАО"])
        if self.partner:
            self.type_input.setCurrentText(self.partner.partner_type)  # Устанавливаем значение типа, если редактируем.

        self.name_input = QLineEdit(self.partner.name if self.partner else "")
        self.address_input = QLineEdit(self.partner.legal_address if self.partner else "")
        self.inn_input = QLineEdit(self.partner.inn if self.partner else "")
        self.director_input = QLineEdit(self.partner.director if self.partner else "")
        self.phone_input = QLineEdit(self.partner.phone if self.partner else "")
        self.phone_input.setInputMask("999 999 99 99;_")
        self.email_input = QLineEdit(self.partner.email if self.partner else "")
        self.rating_input = QLineEdit(str(self.partner.rating) if self.partner else "0")

        # Добавляем виджеты ввода в макет
        layout.addWidget(QLabel("Тип партнёра:"))
        layout.addWidget(self.type_input)
        layout.addWidget(QLabel("Наименование:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Адрес:"))
        layout.addWidget(self.address_input)
        layout.addWidget(QLabel("ИНН:"))
        layout.addWidget(self.inn_input)
        layout.addWidget(QLabel("ФИО директора:"))
        layout.addWidget(self.director_input)
        layout.addWidget(QLabel("Телефон"))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Рейтинг:"))
        layout.addWidget(self.rating_input)

        # Кнопки "Сохранить" и "Отмена"
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_partner)  # Сохранение данных в БД.
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)  # Закрытие окна без сохранения.
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def save_partner(self):
        """Сохранение данных о партнёре в базу данных."""
        try:
            # Проверяем, что обязательные поля заполнены.
            if not self.name_input.text().strip():
                raise ValueError("Поле 'Имя партнёра' не может быть пустым.")

            if not self.address_input.text().strip():
                raise ValueError("Поле 'Адрес' не может быть пустым.")

            if not self.inn_input.text().isdigit():
                raise ValueError("ИНН должен быть числом.")
            if len(self.inn_input.text()) != 10 or len(self.inn_input.text()) != 12:
                raise ValueError("Длина ИНН должна быть равна 10 или 12.")

            if not self.director_input.text().strip():
                raise ValueError("Поле 'Имя директора' не может быть пустым.")

            if not self.phone_input.text().isdigit():
                raise ValueError("Номер телефона должен быть числом.")
            if len(self.phone_input.text()) != 10:
                raise ValueError("Номер телефона должен быть записан в формате XXX XXX XX XX.")

            if not self.email_input.text().strip():
                raise ValueError("Поле 'Электронная почта' не может быть пустым.")

            if not self.rating_input.text().isdigit():
                raise ValueError("Рейтинг должен быть числом.")

            if self.partner:
                # Обновление существующего партнёра.
                self.partner.partner_type = self.type_input.currentText()
                self.partner.name = self.name_input.text()
                self.partner.legal_address = self.address_input.text()
                self.partner.inn = self.inn_input.text()
                self.partner.director = self.director_input.text()
                self.partner.phone = self.phone_input.text()
                self.partner.email = self.email_input.text()
                self.partner.rating = int(self.rating_input.text())
            else:
                # Добавление нового партнёра.
                new_partner = PartnerModel(
                    partner_type=self.type_input.currentText(),
                    name=self.name_input.text(),
                    legal_address=self.address_input.text(),
                    inn=self.inn_input.text(),
                    director=self.director_input.text(),
                    phone=self.phone_input.text(),
                    email=self.email_input.text(),
                    rating=int(self.rating_input.text())
                )
                session.add(new_partner)

            # Сохраняем изменения в базе данных.
            session.commit()
            QMessageBox.information(self, "Успешно", "Партнёр сохранён!")
            self.accept()  # Закрываем диалог с успехом.
        except Exception as e:
            # Отображаем сообщение об ошибке.
            QMessageBox.critical(self, "Ошибка", str(e))

class PartnerHistory(QWidget):
    """Окно для отображения истории заказов партнёра."""
    def __init__(self, partner_id, parent=None):
        super().__init__(parent)
        self.partner_id = partner_id
        self.setWindowIcon(QIcon("./icons/Master_pol.ico"))
        self.setWindowTitle("История реализации продукции")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(self)

        # Заголовок окна.
        title = QLabel("История реализации")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Загружаем и отображаем историю заказов партнёра.
        orders = session.query(OrderModel).filter(OrderModel.partner_id == self.partner_id).all()
        for order in orders:
            product_name = session.query(ProductModel.name).filter(ProductModel.id == order.product_id).scalar()
            order_label = QLabel(f"{product_name} | {order.quantity} | {order.sale_date}")
            layout.addWidget(order_label)

        # Кнопка "Назад" для закрытия окна.
        back_button = QPushButton("Назад")
        back_button.clicked.connect(self.close)
        layout.addWidget(back_button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PartnerList()
    window.setWindowIcon(QIcon("./icons/Master_pol.ico"))
    window.show()
    sys.exit(app.exec())
