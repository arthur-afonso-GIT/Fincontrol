from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QDoubleSpinBox, QFormLayout, 
    QFrame, QMessageBox, QGridLayout, QScrollArea, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy

class AccountsView(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(24)

        # ================= ESQUERDA: LISTAGEM DE CONTAS =================
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        title = QLabel("Gerenciamento de Contas e Saldos")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        left_layout.addWidget(title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.grid_accounts = QGridLayout(scroll_content)
        self.grid_accounts.setSpacing(16)
        self.grid_accounts.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)
        
        main_layout.addWidget(left_container, stretch=3)

        # ================= DIREITA: FORMULÁRIO DE CADASTRO =================
        right_panel = QFrame()
        right_panel.setFixedWidth(360)
        right_panel.setStyleSheet("""
            QFrame { background-color: #19191d; border: 1px solid #29292e; border-radius: 8px; }
            QLabel { border: none; color: #a8a8b3; }
            QLineEdit, QComboBox, QDoubleSpinBox {
                background-color: #202024; border: 1px solid #29292e;
                border-radius: 6px; padding: 8px; color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus { border: 1px solid #00b37e; }
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(16)

        form_title = QLabel("Nova Conta / Carteira")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff; border: none;")
        right_layout.addWidget(form_title)

        form = QFormLayout()
        form.setSpacing(12)

        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Ex: Carteira, Nubank, Itaú...")
        self.txt_name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.cb_type = QComboBox()
        self.cb_type.addItems(["Carteira", "Conta Corrente", "Poupança", "Cartão"])
        self.cb_type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.txt_initial_balance = QDoubleSpinBox()
        self.txt_initial_balance.setRange(-999999.99, 9999999.99)
        self.txt_initial_balance.setPrefix("R$ ")
        self.txt_initial_balance.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.txt_monthly_income = QDoubleSpinBox()
        self.txt_monthly_income.setRange(0.00, 999999.99)
        self.txt_monthly_income.setPrefix("R$ ")
        self.txt_monthly_income.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        form.addRow("Nome / Descrição:", self.txt_name)
        form.addRow("Tipo:", self.cb_type)
        form.addRow("Saldo Atual Inicial:", self.txt_initial_balance)
        form.addRow("Renda Mensal Fixa:", self.txt_monthly_income)
        right_layout.addLayout(form)

        self.btn_save = QPushButton("Cadastrar Carteira/Conta")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #00b37e; color: #ffffff; font-weight: bold;
                border: none; border-radius: 6px; padding: 12px;
            }
            QPushButton:hover { background-color: #00875f; }
        """)
        self.btn_save.clicked.connect(self.save_account)
        right_layout.addWidget(self.btn_save)

        right_layout.addStretch()
        main_layout.addWidget(right_panel, stretch=1)

        self.update_view_data()

    def update_view_data(self):
        """Limpa o grid destruindo os widgets antigos de forma segura e reconstrói."""
        while self.grid_accounts.count():
            item = self.grid_accounts.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setVisible(False)
                widget.setParent(None)
                widget.deleteLater()

        accounts = self.manager.get_accounts()
        columns = 2
        
        for index, acc in enumerate(accounts):
            card = self._create_account_card(acc)
            row = index // columns
            col = index % columns
            self.grid_accounts.addWidget(card, row, col)

        self.grid_accounts.setRowStretch(self.grid_accounts.rowCount(), 1)

    def _create_account_card(self, account_data):
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #19191d; border: 1px solid #29292e; border-radius: 8px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(4)

        # Topo do Card: Alinhamento horizontal do Tipo e do Botão de Excluir
        top_layout = QHBoxLayout()
        lbl_type = QLabel(account_data["type"].upper())
        lbl_type.setStyleSheet("font-size: 11px; color: #a8a8b3; font-weight: 500; border: none;")
        top_layout.addWidget(lbl_type)
        
        top_layout.addStretch()
        
        btn_delete = QPushButton("✕")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setToolTip("Excluir esta conta")
        btn_delete.setStyleSheet("""
            QPushButton { 
                background: transparent; color: #71717a; border: none; 
                font-size: 14px; font-weight: bold; padding: 2px 6px;
            }
            QPushButton:hover { color: #f75a68; }
        """)
        btn_delete.clicked.connect(lambda checked=False, id_val=account_data["id"], name_val=account_data["name"]: self.delete_account_action(id_val, name_val))
        top_layout.addWidget(btn_delete)
        
        card_layout.addLayout(top_layout)

        lbl_name = QLabel(account_data["name"])
        lbl_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; border: none;")
        card_layout.addWidget(lbl_name)

        monthly_inc = account_data.get("monthly_income", 0.0)
        lbl_inc = QLabel(f"Renda Prevista: R$ {monthly_inc:.2f}/mês")
        lbl_inc.setStyleSheet("font-size: 12px; color: #71717a; border: none;")
        card_layout.addWidget(lbl_inc)

        card_layout.addSpacing(8)

        balance = account_data["balance"]
        lbl_balance = QLabel(f"R$ {balance:.2f}")
        if balance >= 0:
            lbl_balance.setStyleSheet("font-size: 22px; font-weight: bold; color: #00b37e; border: none;")
        else:
            lbl_balance.setStyleSheet("font-size: 22px; font-weight: bold; color: #f75a68; border: none;")
        card_layout.addWidget(lbl_balance)
        
        card_layout.addSpacing(8)

        # Layout horizontal para os botões de ajuste lado a lado
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        # Botão 1: Ajustar Saldo Manual
        btn_adjust = QPushButton("Ajustar Saldo")
        btn_adjust.setCursor(Qt.PointingHandCursor)
        btn_adjust.setStyleSheet("""
            QPushButton {
                background-color: #202024; color: #a8a8b3; font-size: 11px;
                border: 1px solid #29292e; border-radius: 4px; padding: 8px;
            }
            QPushButton:hover { background-color: #29292e; color: #ffffff; border-color: #00b37e; }
        """)
        btn_adjust.clicked.connect(lambda checked=False, id_val=account_data["id"], name_val=account_data["name"]: self.adjust_balance_prompt(id_val, name_val))
        actions_layout.addWidget(btn_adjust)

        # Botão 2: Ajustar Renda Fixa Mensal
        btn_income = QPushButton("Alterar Renda Fixa")
        btn_income.setCursor(Qt.PointingHandCursor)
        btn_income.setStyleSheet("""
            QPushButton {
                background-color: #202024; color: #a8a8b3; font-size: 11px;
                border: 1px solid #29292e; border-radius: 4px; padding: 8px;
            }
            QPushButton:hover { background-color: #29292e; color: #ffffff; border-color: #8257e5; }
        """)
        btn_income.clicked.connect(lambda checked=False, id_val=account_data["id"], name_val=account_data["name"], current_inc=monthly_inc: self.adjust_income_prompt(id_val, name_val, current_inc))
        actions_layout.addWidget(btn_income)

        card_layout.addLayout(actions_layout)
        return card

    def adjust_balance_prompt(self, account_id, account_name):
        """Abre a caixa de diálogo para ajustar o saldo atual na hora."""
        new_val, ok = QInputDialog.getDouble(
            self, "Ajustar Saldo", 
            f"Informe o saldo atual exato para '{account_name}':", 
            0.00, -999999.99, 9999999.99, 2
        )
        if ok:
            self.manager.update_account_balance(account_id, new_val)
            self.update_view_data()
            
            # Sincroniza as outras visões globais instantaneamente
            main_window = self.window()
            if hasattr(main_window, "refresh_all_views"):
                main_window.refresh_all_views()

    def adjust_income_prompt(self, account_id, account_name, current_income):
        """Abre a caixa de diálogo para ajustar a renda mensal prevista da conta."""
        new_val, ok = QInputDialog.getDouble(
            self, "Alterar Renda Fixa", 
            f"Informe a nova Renda Mensal Fixa para '{account_name}':", 
            current_income, 0.00, 999999.99, 2
        )
        if ok:
            self.manager.update_account_monthly_income(account_id, new_val)
            self.update_view_data()
            
            main_window = self.window()
            if hasattr(main_window, "refresh_all_views"):
                main_window.refresh_all_views()

    def delete_account_action(self, account_id, account_name):
        """Dispara uma confirmação antes de apagar o registro no banco."""
        confirm = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a conta '{account_name}'?\nIsso também removerá os lançamentos vinculados a ela.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.manager.delete_account(account_id)
            self.update_view_data()
            
            main_window = self.window()
            if hasattr(main_window, "refresh_all_views"):
                main_window.refresh_all_views()

    def save_account(self):
        name = self.txt_name.text().strip()
        account_type = self.cb_type.currentText()
        initial_balance = self.txt_initial_balance.value()
        monthly_income = self.txt_monthly_income.value()

        if not name:
            QMessageBox.warning(self, "Aviso", "O nome da conta é obrigatório!")
            return

        self.manager.add_account(name, account_type, initial_balance, monthly_income)
        
        self.txt_name.clear()
        self.txt_initial_balance.setValue(0.00)
        self.txt_monthly_income.setValue(0.00)
        
        self.update_view_data()
        
        # Propaga a atualização em tempo de execução para o app inteiro
        main_window = self.window()
        if hasattr(main_window, "refresh_all_views"):
            main_window.refresh_all_views()