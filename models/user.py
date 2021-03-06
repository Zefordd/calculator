import hashlib
from aiohttp_session import get_session

from sqlalchemy import create_engine

from sqlalchemy import Column, Integer, String, Float, ForeignKey, update

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref



engine = create_engine('sqlite:///my_db.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    file_url = Column(String, nullable=True)

    def __init__(self, login, password, file_url):
        self.login = login
        self.password = password
        self.file_url = file_url

    def __repr__(self):
        return "(login='%s', password='%s')" % (self.login, self.password)

    @staticmethod
    async def create_new_user(data):
        login = data['login']
        if session.query(User).filter(User.login==login).first():
            return dict(error='login is alreay in use')

        if data['login'] and data['password'] and data['password_2'] and data['password'] == data['password_2']:
            password = hashlib.sha256(data['password'].encode('utf8')).hexdigest()
            new_user = User(login, password, '')
            session.add(new_user)
            session.commit()
        else:
            return dict(error='wrong password or empty slot')

    @staticmethod
    async def get_user(login):
        if session.query(User).filter(User.login == login).first():
            password = session.query(User).filter(User.login == login).first().password
            file_url = session.query(User).filter(User.login == login).first().file_url
            login = session.query(User).filter(User.login == login).first().login
            return dict(login=login, password=password, file_url=file_url)

        return None

    @staticmethod
    async def save_user_file_url(login, file_url):
        session.query(User).filter(User.login == login).\
              update({"file_url": (file_url)})
        session.commit()

    @staticmethod
    async def save_user_file(file_path, user_file):
        with open(file_path, 'wb') as f:
            content = user_file.file.read()
            f.write(content)
            f.close()

    @staticmethod
    async def save_user_zip_file(file_path, zip_file_name):
        import zipfile
        with zipfile.ZipFile(file_path + '.zip', 'w') as zf:
            zf.write(zip_file_name, compress_type=zipfile.ZIP_DEFLATED)
            zf.close()

    @staticmethod
    async def get_delta_size(file_1,file_2):
        import os
        return(os.path.getsize(file_1) - os.path.getsize(file_2))



class Customer(User):
    balance = Column(Float)
    spent_money = Column(Float)

    def __init__(self, *args, **kwargs):
        super(Customer, self).__init__(*args, **kwargs)

    @staticmethod
    async def increase_balance(login, data):
        amount = float(data['amount'])
        current_balance = session.query(Customer).filter(Customer.login == login).first().balance or 0
        total = amount + current_balance
        session.query(Customer).filter(Customer.login == login).update({"balance": round(total, 2)})
        session.commit()

    @staticmethod
    async def get_customer_data(login):
        if session.query(Customer).filter(Customer.login == login).first():
            customer_info = {}
            balance = session.query(Customer).filter(Customer.login == login).first().balance
            customer_info['login'] = login
            customer_info['balance'] = balance
            customer_info['orders'] = await Customer.get_all_customer_orders(login)
            return customer_info

    @staticmethod
    async def get_all_customer_orders(customer):
        """
            Возвращает словарь со всеми заказами пользователя.
            {'Предмет': [количество, картинка товара]}
        """
        if session.query(Customer).filter(Customer.login == customer).first():
            customer = session.query(Customer).filter(Customer.login == customer).first()
            items = session.query(Orders).filter(Orders.customer_login == customer.login).all()
            item_names = []
            orders = {}

            for item in items:
                item_names.append(item.item_name)
                if item.item_name in orders:
                    orders[item.item_name][0] += 1
                else:
                    orders[item.item_name] = [0,0]
                    orders[item.item_name][0] = 1
                    
            for name in orders.keys():
                img = await Item.get_item_img(name)
                orders[name][1] = img

            return orders

class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_login = Column(String)
    item_name = Column(String)

    @staticmethod
    async def make_order(customer, item):
        """
            Записывает в БД 'orders' заказ пользователя
            Принимает на вход имя пользователя(логин) и имя заказа(название предмета)
        """
        try:
            customer = session.query(Customer).filter(Customer.login == customer).first()
            item = session.query(Item).filter(Item.name == item).first()
            order = Orders(customer_login=customer.login, item_name=item.name)
            session.add(order)
            session.commit()
        except AttributeError:
            #print('Item or customer does not exist')
            pass

    @staticmethod
    async def order_price(orders, login):
        price = 0
        for name, multiplier in orders.items():
            price += multiplier*session.query(Item).filter(Item.name == name).first().cost

        current_balance = session.query(Customer).filter(Customer.login == login).first().balance or 0
        if current_balance - price >= 0:
            session.query(Customer).filter(Customer.login == login).update({"balance": round(current_balance - price, 2)})
            session.commit()
            return True
        else:
            return False



    @staticmethod
    async def delete_customer_orders(login):
        session.query(Orders).filter(Orders.customer_login == login).delete()
        session.commit()


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    cost = Column(Float)
    item_img = Column(String)
    description = Column(String)

    @staticmethod
    async def add_item(item_name, cost, item_img, description):
        name = item_name
        if session.query(Item).filter(Item.name==name).first():
            return dict(error='item name must be unique')
        else:
            new_item = Item(name=name, cost=cost, item_img=item_img, description=description)
            session.add(new_item)
            session.commit()

    @staticmethod
    async def get_items_info():
        items_info = []
        result = session.query(Item.name).all()
        names = [value for value, in result]
        for name in names:
            item = {}
            item['name'] = session.query(Item).filter(Item.name == name).first().name
            item['cost'] = session.query(Item).filter(Item.name == name).first().cost
            item['item_img'] = session.query(Item).filter(Item.name == name).first().item_img
            item['description'] = session.query(Item).filter(Item.name == name).first().description
            items_info.append(item)
        return(items_info)
    
    @staticmethod
    async def get_item_img(name):
        img = session.query(Item).filter(Item.name == name).first().item_img
        return img





"""
DELETE ME!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import asyncio
asyncio.get_event_loop().run_until_complete(Orders.make_order('test', 'siga'))

def add_column(engine, table_name, column):
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))

Base.metadata.create_all(engine)  # создание таблицы
Item.__table__.drop(engine)

column = Column('file_url', String, primary_key=False)  # добавить новый столбец
add_column(engine, 'users', column)

session.query(Item).filter(Item.name == 'cup').update({"cost": 10}) # обновить значение 

DELETE ME!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
