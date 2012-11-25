# -*- coding: utf-8 -*-

import datetime
import boto
import boto.dynamodb.exceptions as exceptions
import boto.dynamodb.condition as condition

class ItemNotFoundError(Exception):
    def __init__(self, message):
        super(ItemNotFoundError, self).__init__(message)  


class ItemInvalidError(Exception):
    def __init__(self, message):
        super(ItemInvalidError, self).__init__(message)  


class Store(object):
    READ_UNIT   = 1
    WRITE_UNIT  = 1

    hash_key_name = 'hash'
    range_key_name = 'range'

    def _make_bag(self, model_class):
        if self._mock:
            bag = Bag(model_class=model_class, table=MockTable())
            model_class.fill_mock_bag(bag)
            return bag
        else:
            return Bag(model_class=model_class, table=self._table)

    def _make_connection(self, name, should_have_table):
        self._conn = boto.connect_dynamodb()
        has_table = should_have_table or (name in self._conn.list_tables())
        if has_table:
            self._table = self._conn.get_table(name)
            self._fresh = False
        else:
            schema = self._conn.create_schema(hash_key_name=self.hash_key_name, hash_key_proto_value='S', range_key_name=self.range_key_name, range_key_proto_value='S')
            self._table = self._conn.create_table(name=name, schema=schema, read_units=self.READ_UNIT, write_units=self.WRITE_UNIT)
            self._fresh = True

    def __init__(self, name, model_classes=[], should_have_table=False):
        self._mock = name == None
        if not self._mock:
            self._make_connection(name, should_have_table)
        for mc in model_classes:
            setattr(self, mc.bag_name, self._make_bag(mc))

    @property
    def fresh(self):
        return self._fresh

    @classmethod
    def drop(cls, name):
        conn = boto.connect_dynamodb()
        if name in conn.list_tables():
            conn.delete_table(conn.get_table(name))


class Stuff(object):
    default_ord_value = "0"
    ord_prop_name = "no_such_ord"
    key_prop_name = "no_such_key"

    @property
    def ord(self):
        return getattr(self, self.ord_prop_name, self.default_ord_value)

    @property
    def key(self):
        return getattr(self, self.key_prop_name, self.default_ord_value)


class Bag(object):
    range_key_name = "range"
    table_key_name = "hash"

    def __init__(self, model_class, table, **kwargs):
        self.table = table
        self.model_class = model_class

    @classmethod
    def _to_item_hash(cls, k):
        return "#" + k

    @classmethod
    def _from_item_hash(clses, i):
        if i.find("#") < 0:
            raise ValueError(i + " is not a hash key")
        return i[1:]

    def _to_item_range(self, ord):
        return u".".join([self.name, ord])

    def _bless(self, attr):
        boilerplate = { "created_at": datetime.datetime.utcnow().isoformat() }
        boilerplate.update(attr)
        return boilerplate

    def _new_item(self, key, ord, attrs={}):
        return self.table.new_item(range_key=self._to_item_range(ord), hash_key=self._to_item_hash(key), attrs=self._bless(attrs))
    
    def _get_item(self, key, ord):
        try:
            return self.table.get_item(range_key=self._to_item_range(ord), hash_key=self._to_item_hash(key))
        except exceptions.DynamoDBKeyNotFoundError, ex:
            raise ItemNotFoundError(str(ex))

    def _insert_item(self, item, can_replace):
        try:
            if can_replace:
                item.put()
            else:
                item.put(expected_value={ Store.hash_key_name: False, Store.range_key_name: False })
        except exceptions.DynamoDBConditionalCheckFailedError, ex:
            raise ItemInvalidError(str(ex))
    
    def _list_item(self, ord):
        filter = { Store.range_key_name: condition.BEGINS_WITH(self._to_item_range(ord)) }
        return self.table.scan(scan_filter=filter)

    @property
    def name(self):
        return self.model_class.bag_name

    def add(self, m, can_replace=False):
        m.validate().raise_if_invalid()
        self._insert_item(self._new_item(key=m.key, ord=m.ord, attrs=m.to_item_values()), can_replace)

    def find(self, key, ord=None):
        # FIXME: Better to wrap the exception?
        return self.to_m(self._get_item(key, ord or self.model_class.default_ord_value))

    def list(self, ord=None):
        # FIXME: should use generator
        return [ self.to_m(i) for i in self._list_item(ord or self.model_class.default_ord_value) ]

    def remove(self, m):
        m._item.delete()

    def to_m(self, item):
        model = self.model_class.from_item(item)
        model._item = item
        return model


class MockItem(object):
    def __init__(self, table, range_key, hash_key, attrs):
        self._table = table
        self.range_key = range_key
        self.hash_key = hash_key
        self.attrs = attrs

    def put(self, expected_value=None):
        self._table.put_item(self, expected_value)

    def save(self):
        self._table.put_item(self, None)

    def put_attribute(self, name, value):
        self.attrs[name] = value

    def get(self, name):
        return self.attrs.get(name)

    def delete(self):
        self._table.delete_item(self)


class MockTable(object):
    def __init__(self):
        self._items = {}

    @classmethod
    def _key_from(cls, range_key, hash_key):
        return ".".join([range_key, hash_key])

    def new_item(self, range_key, hash_key, attrs):
        return MockItem(self, range_key, hash_key, attrs)

    def get_item(self, range_key, hash_key):
        try:
            return self._items[self._key_from(range_key, hash_key)]
        except KeyError, ex:
            raise ItemNotFoundError(str(ex))

    def put_item(self, item, expected_value):
        if (expected_value):
            assert False == expected_value[Store.range_key_name]
            assert False == expected_value[Store.hash_key_name]
            if self._items.get(self._key_from(item.range_key, item.hash_key)):
                raise ItemInvalidError("conflict")
        self._items[self._key_from(item.range_key, item.hash_key)] = item

    def delete_item(self, item):
        del self._items[self._key_from(item.range_key, item.hash_key)]

    def scan(self, scan_filter):
        return self._items.values()
