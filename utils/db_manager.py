import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

class DBManager:
    def __init__(self):
        # Garante que o diretório 'database' exista
        os.makedirs('database', exist_ok=True)
        self.engine = create_engine('sqlite:///database/bot.db')
        self.Session = sessionmaker(bind=self.engine)
        self.Base = declarative_base()
        self._define_models()
        self.Base.metadata.create_all(self.engine)

    def _define_models(self):
        class User(self.Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            discord_id = Column(String, unique=True, nullable=False)
            transactions = relationship('Transaction', back_populates='user', cascade="all, delete-orphan")
            categories = relationship('Category', back_populates='user', cascade="all, delete-orphan")
            goals = relationship('Goal', back_populates='user', cascade="all, delete-orphan")

            def __repr__(self):
                return f"<User(id={self.id}, discord_id='{self.discord_id}')>"

        class Transaction(self.Base):
            __tablename__ = 'transactions'
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
            type = Column(String, nullable=False) # 'gasto' ou 'renda'
            value = Column(Float, nullable=False)
            category = Column(String) # Para gastos
            source = Column(String)   # Para rendas
            description = Column(Text)
            date = Column(DateTime, default=datetime.now)

            user = relationship('User', back_populates='transactions')

            def __repr__(self):
                return f"<Transaction(id={self.id}, type='{self.type}', value={self.value})>"

        class Category(self.Base):
            __tablename__ = 'categories'
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
            name = Column(String, nullable=False)

            user = relationship('User', back_populates='categories')

            def __repr__(self):
                return f"<Category(id={self.id}, name='{self.name}')>"

        class Goal(self.Base):
            __tablename__ = 'goals'
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
            name = Column(String, nullable=False)
            target_value = Column(Float, nullable=False)
            current_value = Column(Float, default=0.0)
            due_date = Column(DateTime)
            completed = Column(Integer, default=0) # 0 para False, 1 para True

            user = relationship('User', back_populates='goals')

            def __repr__(self):
                return f"<Goal(id={self.id}, name='{self.name}', target={self.target_value})>"

        self.User = User
        self.Transaction = Transaction
        self.Category = Category
        self.Goal = Goal

    def get_or_create_user(self, discord_id):
        """Retorna o objeto User, criando-o se não existir."""
        with self.Session() as session:
            user = session.query(self.User).filter_by(discord_id=discord_id).first()
            if not user:
                user = self.User(discord_id=discord_id)
                session.add(user)
                session.commit()
                session.refresh(user) # Garante que o ID do novo usuário seja populado
            return user # Retorna o objeto User, não apenas o ID

    def add_transaction(self, user_obj, type, value, category=None, source=None, description=None):
        """Adiciona uma transação para um objeto User."""
        with self.Session() as session:
            # Re-anexa o objeto user à sessão atual se ele for de uma sessão anterior
            user = session.merge(user_obj) 
            
            transaction = self.Transaction(
                user_id=user.id,
                type=type,
                value=value,
                category=category,
                source=source,
                description=description
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction

    def get_transactions_by_month(self, user_obj, year, month):
        """Obtém transações para um objeto User em um mês/ano específico."""
        with self.Session() as session:
            user = session.merge(user_obj)
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            return session.query(self.Transaction).filter(
                self.Transaction.user_id == user.id,
                self.Transaction.date >= start_date,
                self.Transaction.date < end_date
            ).order_by(self.Transaction.date).all()

    def add_category(self, user_obj, name):
        """Adiciona uma categoria para um objeto User."""
        with self.Session() as session:
            user = session.merge(user_obj)
            existing_category = session.query(self.Category).filter_by(user_id=user.id, name=name.lower()).first()
            if existing_category:
                return False, f"A categoria '{name}' já existe."
            
            new_category = self.Category(user_id=user.id, name=name.lower())
            session.add(new_category)
            session.commit()
            session.refresh(new_category)
            return True, f"Categoria '{name}' adicionada com sucesso."

    def get_categories(self, user_obj):
        """Obtém categorias para um objeto User."""
        with self.Session() as session:
            user = session.merge(user_obj)
            return session.query(self.Category).filter_by(user_id=user.id).all()

    def delete_category(self, user_obj, name):
        """Deleta uma categoria para um objeto User e remove transações associadas."""
        with self.Session() as session:
            user = session.merge(user_obj)
            category_to_delete = session.query(self.Category).filter_by(user_id=user.id, name=name.lower()).first()
            if not category_to_delete:
                return False, f"A categoria '{name}' não foi encontrada."

            # Deletar transações associadas a esta categoria
            session.query(self.Transaction).filter_by(user_id=user.id, category=name.lower()).delete()
            
            session.delete(category_to_delete)
            session.commit()
            return True, f"Categoria '{name}' e suas transações associadas deletadas com sucesso."

    def create_goal(self, user_obj, name, target_value, due_date=None):
        """Cria uma nova meta para um objeto User."""
        with self.Session() as session:
            user = session.merge(user_obj)
            existing_goal = session.query(self.Goal).filter_by(user_id=user.id, name=name).first()
            if existing_goal:
                return None, f"Já existe uma meta com o nome '{name}'."

            goal = self.Goal(
                user_id=user.id,
                name=name,
                target_value=target_value,
                due_date=due_date
            )
            session.add(goal)
            session.commit()
            session.refresh(goal)
            return goal, "Meta criada com sucesso."

    def get_goals(self, user_obj):
        """Obtém todas as metas para um objeto User."""
        with self.Session() as session:
            user = session.merge(user_obj)
            return session.query(self.Goal).filter_by(user_id=user.id).all()

    def contribute_to_goal(self, user_obj, goal_id, amount):
        """Adiciona valor a uma meta existente para um objeto User."""
        with self.Session() as session:
            user = session.merge(user_obj)
            goal = session.query(self.Goal).filter_by(id=goal_id, user_id=user.id).first()
            if not goal:
                return False, "Meta não encontrada ou não pertence a você."
            
            if amount <= 0:
                return False, "O valor da contribuição deve ser positivo."

            goal.current_value += amount
            if goal.current_value >= goal.target_value:
                goal.completed = 1 # Marca como concluída
                session.commit()
                return True, f"Você contribuiu R$ {amount:,.2f} para a meta '{goal.name}'. Meta concluída! 🎉"
            else:
                session.commit()
                return True, f"Você contribuiu R$ {amount:,.2f} para a meta '{goal.name}'. Progresso atual: R$ {goal.current_value:,.2f} de R$ {goal.target_value:,.2f}."

    def complete_goal(self, user_obj, goal_id):
        """Marca uma meta como 100% concluída para um objeto User."""
        with self.Session() as session:
            user = session.merge(user_obj)
            goal = session.query(self.Goal).filter_by(id=goal_id, user_id=user.id).first()
            if not goal:
                return False, "Meta não encontrada ou não pertence a você."
            
            if goal.completed == 1:
                return False, f"A meta '{goal.name}' já está marcada como concluída."

            goal.current_value = goal.target_value # Garante que o valor atual seja igual ao alvo
            goal.completed = 1
            session.commit()
            return True, f"Meta '{goal.name}' marcada como concluída! ✅"

    def delete_goal(self, user_obj, goal_id):
        """Deleta uma meta para um objeto User."""
        with self.Session() as session:
            user = session.merge(user_obj)
            goal_to_delete = session.query(self.Goal).filter_by(id=goal_id, user_id=user.id).first()
            if not goal_to_delete:
                return False, "Meta não encontrada ou não pertence a você."
            
            session.delete(goal_to_delete)
            session.commit()
            return True, f"Meta '{goal_to_delete.name}' deletada com sucesso."