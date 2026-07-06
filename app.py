import os
import json
import uuid
from datetime import datetime

class FinanceManager:
    def __init__(self):
        # Define o caminho do banco de dados local na pasta data/data.json
        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "data.json"))
        self._ensure_storage_exists()
        self.data = self._load_data()

    def _ensure_storage_exists(self):
        """Garante que o diretório e o arquivo JSON existam com uma estrutura inicial padrão."""
        data_dir = os.path.dirname(self.file_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(self.file_path):
            initial_structure = {
                "accounts": [],
                "categories": [
                    {"id": "1", "name": "Alimentação", "type": "Despesa", "monthly_limit": 0.0},
                    {"id": "2", "name": "Transporte", "type": "Despesa", "monthly_limit": 0.0},
                    {"id": "3", "name": "Saúde", "type": "Despesa", "monthly_limit": 0.0},
                    {"id": "4", "name": "Salário", "type": "Receita", "monthly_limit": 0.0},
                    {"id": "5", "name": "Investimentos", "type": "Receita", "monthly_limit": 0.0}
                ],
                "transactions": []
            }
            self._save_to_disk(initial_structure)

    def _load_data(self):
        """Carrega os dados salvos do disco para a memória."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"accounts": [], "categories": [], "transactions": []}

    def _save_to_disk(self, data=None):
        """Escreve o estado atual da memória de volta ao arquivo JSON."""
        if data is None:
            data = self.data
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # =========================================================================
    # GESTÃO DE CONTAS / CARTEIRAS
    # =========================================================================
    def add_account(self, name: str, account_type: str, initial_balance: float, monthly_income: float = 0.0):
        """Cadastra uma nova conta bancária ou carteira física."""
        account = {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "type": account_type,
            "balance": float(initial_balance),
            "monthly_income": float(monthly_income)
        }
        self.data["accounts"].append(account)
        self._save_to_disk()
        return account

    def update_account_balance(self, account_id: str, new_balance: float):
        """Altera diretamente o saldo atual de uma conta."""
        for acc in self.data["accounts"]:
            if acc["id"] == account_id:
                acc["balance"] = float(new_balance)
                self._save_to_disk()
                return True
        return False

    def update_account_monthly_income(self, account_id: str, new_income: float):
        """Altera diretamente a renda mensal fixa prevista de uma conta específica."""
        for acc in self.data["accounts"]:
            if acc["id"] == account_id:
                acc["monthly_income"] = float(new_income)
                self._save_to_disk()
                return True
        return False

    def delete_account(self, account_id: str):
        """Remove permanentemente uma conta e limpa seus lançamentos atrelados."""
        self.data["accounts"] = [acc for acc in self.data["accounts"] if acc["id"] != account_id]
        self.data["transactions"] = [t for t in self.data["transactions"] if t["account_id"] != account_id]
        self._save_to_disk()
        return True

    def get_accounts(self):
        """Retorna todas as contas injetando propriedades ausentes por retrocompatibilidade."""
        for acc in self.data["accounts"]:
            if "monthly_income" not in acc:
                acc["monthly_income"] = 0.0
        return self.data["accounts"]

    # =========================================================================
    # GESTÃO DE CATEGORIAS (COM SUPORTE A METAS/LIMITES E EXCLUSÃO)
    # =========================================================================
    def add_category(self, name: str, category_type: str, monthly_limit: float = 0.0):
        """Adiciona uma nova categoria salvando o teto de gastos estipulado."""
        for cat in self.data["categories"]:
            if cat["name"].lower() == name.strip().lower() and cat["type"] == category_type:
                cat["monthly_limit"] = float(monthly_limit)
                self._save_to_disk()
                return cat

        category = {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "type": category_type,
            "monthly_limit": float(monthly_limit)
        }
        self.data["categories"].append(category)
        self._save_to_disk()
        return category

    def delete_category(self, category_id: str):
        """Remove permanentemente uma categoria da lista."""
        self.data["categories"] = [cat for cat in self.data["categories"] if cat["id"] != category_id]
        self._save_to_disk()
        return True

    def get_categories(self):
        """Retorna a lista de categorias garantindo que o campo monthly_limit exista."""
        for cat in self.data["categories"]:
            if "monthly_limit" not in cat:
                cat["monthly_limit"] = 0.0
        return self.data["categories"]

    # =========================================================================
    # MOVIMENTAÇÕES FINANCEIRAS
    # =========================================================================
    def add_transaction(self, amount: float, category_id: str, account_id: str, description: str, 
                        transaction_type: str, date: str = None, installments: int = 1, is_fixed: bool = False):
        """Registra movimentações tratando divisões em parcelas mensais futuras automáticas."""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        base_date = datetime.strptime(date, "%Y-%m-%d")
        installment_amount = float(amount) / installments

        for i in range(installments):
            year = base_date.year + (base_date.month + i - 1) // 12
            month = (base_date.month + i - 1) % 12 + 1
            day = min(base_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
            
            future_date_str = f"{year}-{month:02d}-{day:02d}"
            desc_suffix = f" ({i+1}/{installments})" if installments > 1 else ""
            
            transaction = {
                "id": str(uuid.uuid4()),
                "amount": installment_amount,
                "date": future_date_str,
                "category_id": category_id,
                "account_id": account_id,
                "description": f"{description}{desc_suffix}",
                "type": transaction_type,
                "is_fixed": is_fixed
            }

            self._update_balances_on_creation(transaction)
            self.data["transactions"].append(transaction)
            
        self._save_to_disk()

    def _update_balances_on_creation(self, transaction):
        """Ajusta internamente o saldo atual da conta de destino na criação."""
        for acc in self.data["accounts"]:
            if acc["id"] == transaction["account_id"]:
                if transaction["type"] == "Receita":
                    acc["balance"] += transaction["amount"]
                elif transaction["type"] == "Despesa":
                    acc["balance"] -= transaction["amount"]

    def delete_transaction(self, transaction_id: str):
        """Remove a transação e estorna/devolve o valor ao saldo da respectiva conta."""
        transaction_to_remove = None
        for t in self.data["transactions"]:
            if t["id"] == transaction_id:
                transaction_to_remove = t
                break

        if transaction_to_remove:
            for acc in self.data["accounts"]:
                if acc["id"] == transaction_to_remove["account_id"]:
                    if transaction_to_remove["type"] == "Receita":
                        acc["balance"] -= transaction_to_remove["amount"]
                    elif transaction_to_remove["type"] == "Despesa":
                        acc["balance"] += transaction_to_remove["amount"]
                    break
            
            self.data["transactions"] = [t for t in self.data["transactions"] if t["id"] != transaction_id]
            self._save_to_disk()
            return True
        return False

    def get_transactions(self):
        """Retorna todas as transações gravadas."""
        return self.data["transactions"]

    # =========================================================================
    # MOTOR DE MÉTRICAS DO DASHBOARD
    # =========================================================================
    def get_dashboard_metrics(self):
        """Calcula o balanço e a saúde financeira consolidada baseada no mês corrente."""
        accounts = self.get_accounts()
        transactions = self.get_transactions()
        
        current_balance = sum(acc["balance"] for acc in accounts)
        total_monthly_income_expected = sum(acc.get("monthly_income", 0.0) for acc in accounts)
        
        current_month = datetime.now().strftime("%Y-%m")
        total_income_real = 0.0
        total_expense = 0.0

        for t in transactions:
            if t["date"].startswith(current_month):
                if t["type"] == "Receita":
                    total_income_real += t["amount"]
                elif t["type"] == "Despesa":
                    total_expense += t["amount"]

        display_income = max(total_income_real, total_monthly_income_expected)
        savings = display_income - total_expense

        return {
            "current_balance": current_balance,
            "monthly_income": display_income,
            "monthly_expense": total_expense,
            "savings": savings,
            "recent_transactions": sorted(transactions, key=lambda x: x["date"], reverse=True)[:5]
        }