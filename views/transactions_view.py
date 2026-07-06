from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFormLayout, QFrame, QMessageBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QDoubleSpinBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QSizePolicy

class TransactionsView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(24)

        # =====================================================================
        # ESQUERDA: HISTÓRICO DE TRANSAÇÕES (TABELA)
        # =====================================================================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        title_box = QHBoxLayout()
        title = QLabel("Histórico / Gastos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        tip = QLabel("(Dê duplo clique em uma linha para remover)")
        tip.setStyleSheet("font-size: 12px; color: #a8a8b3; font-style: italic; padding-top: 10px;")
        title_box.addWidget(title)
        title_box.addWidget(tip)
        title_box.addStretch()
        left_layout.addLayout(title_box)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Categoria", "Conta", "Valor"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Evento de duplo clique para remoção
        self.table.doubleClicked.connect(self.delete_transaction_clicked)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #19191d;
                border: 1px solid #29292e;
                border-radius: 8px;
                gridline-color: #202024;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #202024;
                color: #a8a8b3;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        left_layout.addWidget(self.table)
        
        main_layout.addWidget(left_container, stretch=3)

        # =====================================================================
        # DIREITA: FORMULÁRIO DE CADASTRO
        # =====================================================================
        right_panel = QFrame()
        right_panel.setFixedWidth(360)
        right_panel.setStyleSheet("""
            QFrame { background-color: #19191d; border: 1px solid #29292e; border-radius: 8px; }
            QLabel { border: none; color: #a8a8b3; font-size: 13px; }
            QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit {
                background-color: #202024; border: 1px solid #29292e;
                border-radius: 6px; padding: 10px; color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus { border: 1px solid #00b37e; }
            QCheckBox { color: #ffffff; border: none; }
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(16)

        form_title = QLabel("Nova Transação")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff; border: none; margin-bottom: 10px;")
        right_layout.addWidget(form_title)

        form = QFormLayout()
        form.setSpacing(12)

        self.txt_description = QLineEdit()
        self.txt_description.setPlaceholderText("Ex: Supermercado, Aluguel...")
        self.txt_description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.txt_amount = QDoubleSpinBox()
        self.txt_amount.setRange(0.00, 999999.99)
        self.txt_amount.setPrefix("R$ ")
        self.txt_amount.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.cb_type = QComboBox()
        self.cb_type.addItems(["Despesa", "Receita"])
        self.cb_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.cb_category = QComboBox()
        self.cb_category.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_account = QComboBox()
        self.cb_account.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.txt_date = QDateEdit()
        self.txt_date.setCalendarPopup(True)
        self.txt_date.setDate(QDate.currentDate())
        self.txt_date.setDisplayFormat("dd/MM/yyyy")
        self.txt_date.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.txt_installments = QDoubleSpinBox()
        self.txt_installments.setRange(1, 360)
        self.txt_installments.setDecimals(0)
        self.txt_installments.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.chk_is_fixed = QCheckBox("Marcar como fixa (Mensal)")

        form.addRow("Descrição:", self.txt_description)
        form.addRow("Valor:", self.txt_amount)
        form.addRow("Tipo:", self.cb_type)
        form.addRow("Categoria:", self.cb_category)
        form.addRow("Conta:", self.cb_account)
        form.addRow("Data:", self.txt_date)
        form.addRow("Parcelas:", self.txt_installments)
        form.addRow("", self.chk_is_fixed)
        
        right_layout.addLayout(form)

        self.btn_save = QPushButton("Lançar Transação")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #00b37e; color: #ffffff; font-weight: bold;
                border: none; border-radius: 6px; padding: 12px; font-size: 14px;
            }
            QPushButton:hover { background-color: #00875f; }
        """)
        self.btn_save.clicked.connect(self.save_transaction)
        right_layout.addWidget(self.btn_save)

        right_layout.addStretch()
        main_layout.addWidget(right_panel)

        self.update_view_data()

    def update_view_data(self):
        """Atualiza os comboboxes com dados recentes e redesenha a tabela."""
        self.cb_category.clear()
        categories = self.manager.get_categories()
        for cat in categories:
            self.cb_category.addItem(cat["name"], cat["id"])

        self.cb_account.clear()
        accounts = self.manager.get_accounts()
        for acc in accounts:
            self.cb_account.addItem(acc["name"], acc["id"])

        self.table.setRowCount(0)
        transactions = self.manager.get_transactions()
        
        for t in reversed(transactions):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            cat_name = next((c["name"] for c in categories if c["id"] == t["category_id"]), "Sem Cat.")
            acc_name = next((a["name"] for a in accounts if a["id"] == t["account_id"]), "Sem Conta")
            
            try:
                date_obj = QDate.fromString(t["date"], "yyyy-MM-dd")
                date_str = date_obj.toString("dd/MM/yyyy")
            except:
                date_str = t["date"]

            desc_text = t["description"]
            if t.get("is_fixed", False):
                desc_text += " 📌"

            # Insere o ID real oculto no item de data
            date_item = QTableWidgetItem(date_str)
            date_item.setData(Qt.UserRole, t["id"]) 
            
            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, QTableWidgetItem(desc_text))
            self.table.setItem(row, 2, QTableWidgetItem(cat_name))
            self.table.setItem(row, 3, QTableWidgetItem(acc_name))
            
            val_item = QTableWidgetItem(f"R$ {t['amount']:.2f}")
            if t["type"] == "Despesa":
                val_item.setForeground(Qt.red)
            else:
                val_item.setForeground(Qt.green)
            self.table.setItem(row, 4, val_item)

    def delete_transaction_clicked(self, model_index):
        """Identifica a linha clicada, extrai o ID oculto e deleta atualizando o sistema."""
        row = model_index.row()
        date_item = self.table.item(row, 0)
        if not date_item:
            return

        transaction_id = date_item.data(Qt.UserRole)
        description = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja apagar a movimentação '{description}'?\nO saldo da conta e gráficos serão atualizados.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.manager.delete_transaction(transaction_id)
            if success:
                self.update_view_data()
                
                # Avisa a janela principal para atualizar o Dashboard em tempo real
                main_window = self.window()
                if hasattr(main_window, "refresh_all_views"):
                    main_window.refresh_all_views()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível remover a transação do banco.")

    def save_transaction(self):
        description = self.txt_description.text().strip()
        amount = self.txt_amount.value()
        transaction_type = self.cb_type.currentText()
        category_id = self.cb_category.currentData()
        account_id = self.cb_account.currentData()
        
        date_str = self.txt_date.date().toString("yyyy-MM-dd")
        installments = int(self.txt_installments.value())
        is_fixed = self.chk_is_fixed.isChecked()

        if not description:
            QMessageBox.warning(self, "Aviso", "Insira uma descrição válida.")
            return
        if amount <= 0:
            QMessageBox.warning(self, "Aviso", "O valor precisa ser maior que R$ 0.00.")
            return
        if not category_id or not account_id:
            QMessageBox.warning(self, "Aviso", "Cadastre e selecione uma conta e uma categoria antes.")
            return

        self.manager.add_transaction(
            amount=amount,
            category_id=category_id,
            account_id=account_id,
            description=description,
            transaction_type=transaction_type,
            date=date_str,
            installments=installments,
            is_fixed=is_fixed
        )

        self.txt_description.clear()
        self.txt_amount.setValue(0.0)
        self.txt_installments.setValue(1)
        self.chk_is_fixed.setChecked(False)
        self.update_view_data()
        
        # Atualiza o dashboard também ao criar uma nova transação
        main_window = self.window()
        if hasattr(main_window, "refresh_all_views"):
            main_window.refresh_all_views()