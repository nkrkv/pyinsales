pyinsales — это набор биндингов для API популярной e-commerce платформы InSales,
целью которого является облегчение разработки дополнений к платформе на Python’е.

Биндинги выделены из приложения [Incrates](http://incrates.ru), для которого они были
созданы изначально. Они достаточно низкоуровневые и универсальные, поэтому и были
выделены в отдельный Open Source проект.

Установка
---------

`$ pip install pyinsales`

Зависимости
-----------

 * iso8601 для работы с датами

Быстродействие
--------------

Самое узкое место — разбор входящего XML. Оно было многократно оптимизировано и сейчас
основывается на высокоскоростном парсере Expat, написанном на C и работающем по модели
SAX.

Таким образом даже обработка гигантского потока данных не отнимет большого количества
памяти и вычислительных ресурсов.

Примеры
-------

```python
>>> from pprint import pprint
>>> from insales import InSalesApi

>>> api = InSalesApi.from_credentials('your-account-name', 'your-api-key', 'your-api-pass')

>>> orders = api.get_orders(per_page=2, page=3)
>>> pprint(orders)
... [{u'accepted-at': None,
...   u'id': 749627,
...   u'client': {u'client-group-id': None,
...               u'created-at': datetime.datetime(2012, 8, 11, 14, 21, 21, tzinfo=<FixedOffset u'+04:00'>),
...               u'email': None,
...               u'fields-values': [],
...               u'id': 696407,
...               u'middlename': None,
...               u'name': u'Вася Пупкин',
...               u'phone': u'+79031034423',
...               u'registered': False,
...               u'subscribe': True,
...               u'surname': None,
...               u'updated-at': datetime.datetime(2012, 8, 11, 14, 21, 21, tzinfo=<FixedOffset u'+04:00'>)},
...   u'comment': None,
...   u'created-at': datetime.datetime(2012, 8, 11, 14, 21, 21, tzinfo=<FixedOffset u'+04:00'>),
...   u'delivered-at': None,
...   u'delivery-date': None,
...   u'delivery-description': u'Почта России',
... # ...

>>> order = api.create_order({
...     'client': {
...         'phone': '+70000000000',
...         'name': u'Вася',
...     },
...     'order-lines-attributes': [{
...         'variant-id': 4274495,
...         'quantity': 3,
...     }],
...     'payment-gateway-id': 79172,
...     'delivery-variant-id': 21797,
... })

>>> pprint(order)
... [{u'accepted-at': None,
...   u'id': 749629,
...   u'client': {u'client-group-id': None,
...               u'created-at': datetime.datetime(2012, 8, 11, 14, 23, 24, tzinfo=<FixedOffset u'+04:00'>),
...               u'email': None,
...               u'fields-values': [],
...               u'id': 696412,
...               u'middlename': None,
...               u'name': u'Вася Пупкин',
...               u'phone': u'+7000000000',
...               u'registered': False,
...               u'subscribe': True,
...               u'surname': None,
...               u'updated-at': datetime.datetime(2012, 8, 11, 14, 23, 24, tzinfo=<FixedOffset u'+04:00'>)},
...   u'comment': None,
...   u'created-at': datetime.datetime(2012, 8, 11, 14, 23, 24, tzinfo=<FixedOffset u'+04:00'>),
...   u'delivered-at': None,
...   u'delivery-date': None,
...   u'delivery-description': u'Почта России',
... # ...

>>> order = api.update_order(749629, {
...     'fulfillment-status': 'accepted',
...     'order-lines-attributes': [{
...         'variant-id': 4274495,
...         'quantity': 2,
...     }],
... })

>>> pprint(order)
... [{u'accepted-at': datetime.datetime(2012, 8, 11, 14, 24, 47, tzinfo=<FixedOffset u'+04:00'>),
...   u'id': 749629,
...   u'client': {u'client-group-id': None,
...               u'created-at': datetime.datetime(2012, 8, 11, 14, 23, 24, tzinfo=<FixedOffset u'+04:00'>),
...               u'email': None,
...               u'fields-values': [],
...               u'id': 696412,
...               u'middlename': None,
...               u'name': u'Вася Пупкин',
...               u'phone': u'+7000000000',
...               u'registered': False,
...               u'subscribe': True,
...               u'surname': None,
...               u'updated-at': datetime.datetime(2012, 8, 11, 14, 23, 24, tzinfo=<FixedOffset u'+04:00'>)},
...   u'comment': None,
...   u'created-at': datetime.datetime(2012, 8, 11, 14, 23, 24, tzinfo=<FixedOffset u'+04:00'>),
...   u'delivered-at': None,
...   u'delivery-date': None,
...   u'delivery-description': u'Почта России',
... # ...

>>> api.delete_order(749629)
```

Философия
---------

 * Все ответы от InSales возвращаются как вложенные структуры данных с правильной типизацией.
   Для дат используется `datetime`, для вещественных чисел — `Decimal` и т.д.
 * Все строковые значения в возвращаемых ответах приводятся к `unicode`
 * Все методы для обновления и создания объектов принимают произвольные
   структуры данных. То есть имена и набор полей в них никак не форсируются
   со стороны pyinsales. Это обеспечивает прямую совместимость с возможными будущими нововведениями InSales
   За документацией о необходимых и допустимых параметрах следует обращаться на
   [InSales API Wiki](http://wiki.insales.ru/wiki/%D0%9A%D0%BE%D0%BC%D0%B0%D0%BD%D0%B4%D1%8B_API)
 * Все передаваемые в параметрах строки могут быть как `unicode`, так и `str` в кодировке UTF-8
 * Все передаваемые для get-запросов аргументов приводятся к строкам должным образом. В том
   числе `datetime` переводятся в строковый формат, принятый в InSales
 * Если метод должен возвращать список объектов (заказы, товары и т.п.), и этот список оказывается
   пустым, метод возвращает `[]`, не `None`

Методы InSalesApi
-----------------

Для параметров суффикс `_id` означает ID объекта на платформе InSales. Он
может быть или `int` или строкой. Суффикс `_data` означает вложенную структуру
данных из словарей и списков, точный формат которой определяется
REST-endpoint’ом со стороны InSales для данного конкретного метода.

```python
#========================================================================
# Заказы
#========================================================================
get_orders(self, per_page=25, page=1, updated_since=None):
get_order(self, order_id):
update_order(self, order_id, order_data):
delete_order(self, order_id):
create_order(self, order_data):
get_order_delivery_variants(self, order_data):
get_order_payment_gateways(self, order_data):

#========================================================================
# Поля заказов
#========================================================================
get_orders_fields(self):

#========================================================================
# Категории на складе
#========================================================================
get_categories(self):
get_category(self, category_id):
add_category(self, category_data):
update_category(self, category_id, category_data):
delete_category(self, category_id):

#========================================================================
# Категории на сайте
#========================================================================
get_collections(self):
get_collection(self, collection_id):
add_collection(self, collection_data):
update_collection(self, collection_id, collection_data):
delete_collection(self, collection_id):

#========================================================================
# Свойства товаров
#========================================================================
get_option_names(self):
get_option_name(self, option_name_id):
add_option_name(self, option_name):
update_option_name(self, option_name_id, option_name_data):
delete_option_name(self, option_name_id):

#========================================================================
# Значения свойств
#========================================================================
get_option_values(self, option_name_id=None):
get_option_value(self, option_name_id, option_value_id):
add_option_value(self, option_name_id, option_value_data):
update_option_value(self, option_name_id, option_value_id, option_value_data):
delete_option_value(self, option_name_id, option_value_id):

#========================================================================
# Товары
#========================================================================
get_products(self, limit=50, page=1, updated_since=None):
get_product(self, product_id):
add_product(self, product_data):
update_product(self, product_id, product_data):
delete_product(self, product_id):

#========================================================================
# Модификации товаров
#========================================================================
get_product_variants(self, product_id):
get_product_variant(self, product_id, variant_id):
add_product_variant(self, product_id, variant_data):
update_product_variant(self, product_id, variant_id, variant_data):
delete_product_variant(self, product_id, variant_id):

#========================================================================
# Изображения товара
#========================================================================
get_product_images(self, product_id):
get_product_image(self, product_id, image_id):
add_product_image(self, product_id, image_data):
update_product_image(self, product_id, image_id, image_data):
delete_product_image(self, product_id, image_id):

#========================================================================
# Размещение товара
#========================================================================
get_collects(self, product_id=None, collection_id=None):
add_collect(self, collect_data):
update_collect(self, collect_id, collect_data):
delete_collect(self, collect_id):

#========================================================================
# Веб-хуки
#========================================================================
get_webhooks(self):
get_webhook(self, webhook_id):
add_webhook(self, webhook):
update_webhook(self, webhook_id, webhook_data):
delete_webhook(self, webhook_id):

#========================================================================
# Биллинг
#========================================================================
get_recurring_application_charge(self):
add_recurring_application_charge(self, recurring_application_charge_data):
update_recurring_application_charge(self, recurring_application_charge_data):
```

Лицензия
--------

pyinsales распространяется на условиях лицензии MIT.

Автор
-----

Виктор Накоряков ([nailxx](https://github.com/nailxx))
