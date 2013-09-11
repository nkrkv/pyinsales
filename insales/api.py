# -*- coding: utf-8; -*-

from insales.parsing import parse
from insales.composing import compose
from insales.connection import Connection


class InSalesApi(object):

    arrays = {
        'variants'              : 'variant',
        'variants-attributes'   : 'variant',
        'options'               : 'option',
        'option-names'          : 'option-name',
        'option-values'         : 'option-value',
        'orders'                : 'order',
        'order-lines-attributes': 'order-line-attributes',
        'images'                : 'image',
    }

    @classmethod
    def from_credentials(cls, account, api_key, password, **kwargs):
        return cls(Connection(account, api_key, password, **kwargs))

    def __init__(self, connection):
        self.connection = connection

    #========================================================================
    # Заказы
    #========================================================================
    def get_orders(self, per_page=25, page=1):
        return self._get('/admin/orders.xml', {'per_page': per_page, 'page': page}) or []

    def get_order(self, order_id):
        return self._get('/admin/orders/%s.xml' % order_id)

    def update_order(self, order_id, order_data):
        return self._update('/admin/orders/%s.xml' % order_id, order_data, root='order')

    def delete_order(self, order_id):
        self._delete('/admin/orders/%s.xml' % order_id)

    def create_order(self, order_data):
        return self._add('/admin/orders.xml', order_data, root='order')

    def get_order_delivery_variants(self, order_data):
        return self._post('/admin/orders/delivery_variants.xml',
                          order_data, root='order')

    def get_order_payment_gateways(self, order_data):
        return self._post('/admin/orders/payment_gateways.xml',
                          order_data, root='order')

    #========================================================================
    # Поля заказов
    #========================================================================
    def get_orders_fields(self):
        return self._get('/admin/orders/fields.xml')

    #========================================================================
    # Категории на складе
    #========================================================================
    def get_categories(self):
        return self._get('/admin/categories.xml') or []

    def get_category(self, category_id):
        return self._get('/admin/categories/%s.xml' % category_id)

    def add_category(self, category_data):
        return self._add('/admin/categories.xml', category_data, root='category')

    def update_category(self, category_id, category_data):
        return self._update('/admin/categories/%s.xml' % category_id,
                            category_data, root='category')

    def delete_category(self, category_id):
        self._delete('/admin/categories/%s.xml' % category_id)

    #========================================================================
    # Категории на сайте
    #========================================================================
    def get_collections(self):
        return self._get('/admin/collections.xml') or []

    def get_collection(self, collection_id):
        return self._get('/admin/collections/%s.xml' % collection_id)

    def add_collection(self, collection_data):
        return self._add('/admin/collections.xml', collection_data, root='collection')

    def update_collection(self, collection_id, collection_data):
        return self._update('/admin/collections/%s.xml' % collection_id,
                            collection_data, root='collection')

    def delete_collection(self, collection_id):
        self._delete('/admin/collections/%s.xml' % collection_id)
    
    #========================================================================
    # Свойства товаров
    #========================================================================
    def get_option_names(self):
        return self._get('/admin/option_names.xml') or []

    def get_option_name(self, option_name_id):
        return self._get('/admin/option_names/%s.xml' % option_name_id)

    def add_option_name(self, option_name):
        return self._add('/admin/option_names.xml', option_name, root='option-name')

    def update_option_name(self, option_name_id, option_name_data):
        return self._update('/admin/option_names/%s.xml' % option_name_id,
                            option_name_data, root='option-name')

    def delete_option_name(self, option_name_id):
        self._delete('/admin/option_names/%s.xml' % option_name_id)

    #========================================================================
    # Значения свойств
    #========================================================================
    def get_option_values(self, option_name_id=None):
        if option_name_id:
            path = '/admin/option_names/%s/option_values.xml' % option_name_id
        else:
            path = '/admin/option_values.xml'
        return self._get(path) or []

    def get_option_value(self, option_name_id, option_value_id):
        return self._get('/admin/option_names/%s/option_values/%s.xml' %
                         (option_name_id, option_value_id))

    def add_option_value(self, option_name_id, option_value_data):
        return self._add('/admin/option_names/%s/option_values.xml' % option_name_id, 
                         option_value_data, root='option-value')

    def update_option_value(self, option_name_id, option_value_id, option_value_data):
        return self._update('/admin/option_names/%s/option_values/%s.xml' %
                            (option_name_id, option_value_id),
                            option_value_data, root='option_value')

    def delete_option_value(self, option_name_id, option_value_id):
        self._delete('/admin/option_names/%s/option_values/%s.xml' %
                     (option_name_id, option_value_id))

    #========================================================================
    # Товары
    #========================================================================
    def get_products(self, limit=50, page=1, updated_since=None):
        qargs = {
            'limit': limit,
            'page': page,
        }
        if updated_since:
            qargs['updated_since'] = updated_since
        return self._get('/admin/products.xml', qargs) or []

    def get_product(self, product_id):
        return self._get('/admin/products/%s.xml' % product_id)

    def add_product(self, product_data):
        return self._add('/admin/products.xml', product_data, root='product')

    def update_product(self, product_id, product_data):
        return self._update('/admin/products/%s.xml' % product_id, product_data,
                            root='product')

    def delete_product(self, product_id):
        return self._delete('/admin/products/%s.xml' % product_id)

    #========================================================================
    # Модификации товаров
    #========================================================================
    def get_product_variants(self, product_id):
        return self._get('/admin/products/%s/variants.xml' % product_id) or []

    def get_product_variant(self, product_id, variant_id):
        return self._get('/admin/products/%s/variants/%s.xml' % (product_id, variant_id))

    def add_product_variant(self, product_id, variant_data):
        return self._add('/admin/products/%s/variants.xml' % product_id,
                         variant_data, root='variant')

    def update_product_variant(self, product_id, variant_id, variant_data):
        return self._update('/admin/products/%s/variants/%s.xml' %
                            (product_id, variant_id),
                            variant_data, root='variant')

    def delete_product_variant(self, product_id, variant_id):
        self._delete('/admin/products/%s/variants/%s.xml' % (product_id, variant_id))

    #========================================================================
    # Изображения товара
    #========================================================================
    def get_product_images(self, product_id):
        return self._get('/admin/products/%s/images.xml' % product_id) or []

    def get_product_image(self, product_id, image_id):
        return self._get('/admin/products/%s/images/%s.xml' % (product_id, image_id))

    def add_product_image(self, product_id, image_data):
        return self._add('/admin/products/%s/images.xml' % product_id,
                         image_data, root='image')

    def update_product_image(self, product_id, image_id, image_data):
        return self._update('/admin/products/%s/images/%s.xml' % (product_id, image_id),
                            image_data, root='image')

    def delete_product_image(self, product_id, image_id):
        self._delete('/admin/products/%s/images/%s.xml' % (product_id, image_id))

    #========================================================================
    # Размещение товара
    #========================================================================
    def get_collects(self, product_id=None, collection_id=None):
        qargs = {}
        if product_id:
            qargs['product_id'] = product_id
        if collection_id:
            qargs['collection_id'] = collection_id

        return self._get('/admin/collects.xml', qargs) or []

    def add_collect(self, collect_data):
        return self._add('/admin/collects.xml', collect_data, root='collect')

    def update_collect(self, collect_id, collect_data):
        return self._update('/admin/collects/%s.xml' % collect_id,
                            collect_data, root='collect')

    def delete_collect(self, collect_id):
        return self._delete('/admin/collects/%s.xml' % collect_id)

    #========================================================================
    # Веб-хуки
    #========================================================================
    def get_webhooks(self):
        return self._get('/admin/webhooks.xml') or []

    def get_webhook(self, webhook_id):
        return self._get('/admin/webhooks/%s.xml' % webhook_id)

    def add_webhook(self, webhook):
        return self._add('/admin/webhooks.xml', webhook, root='webhook')

    def update_webhook(self, webhook_id, webhook_data):
        return self._update('/admin/webhooks/%s.xml' % webhook_id,
                            webhook_data, root='webhook')

    def delete_webhook(self, webhook_id):
        self._delete('/admin/webhooks/%s.xml' % webhook_id)

    #========================================================================
    # Биллинг
    #========================================================================
    def get_recurring_application_charge(self):
        return self._get('/admin/recurring_application_charge.xml')

    def add_recurring_application_charge(self, recurring_application_charge_data):
        return self._add('/admin/recurring_application_charge.xml',
                         recurring_application_charge_data,
                         root='recurring-application-charge')

    def update_recurring_application_charge(self, recurring_application_charge_data):
        return self._update('/admin/recurring_application_charge.xml',
                            recurring_application_charge_data,
                            root='recurring-application-charge')

    #========================================================================
    def _get(self, endpoint, qargs={}):
        return self._req('get', endpoint, qargs)

    def _add(self, endpoint, data, root):
        xml = compose(data, root=root, arrays=self.arrays)
        return self._req('post', endpoint, xml)

    _post = _add

    def _update(self, endpoint, data, root):
        xml = compose(data, root=root, arrays=self.arrays)
        return self._req('put', endpoint, xml)

    def _delete(self, endpoint):
        return self._req('delete', endpoint)

    def _req(self, method, *args, **kwargs):
        response = getattr(self.connection, method)(*args, **kwargs)
        return parse(response)
