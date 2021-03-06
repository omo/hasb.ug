# -*- coding: utf-8 -*-

import datetime, json, types
import boto
import boto.dynamodb.exceptions as exceptions
import boto.dynamodb.condition as condition
import hasbug.validation as validation

class ItemError(Exception):
    def __init__(self, message):
        super(ItemError, self).__init__(message)  

class ItemNotFoundError(ItemError):
    pass

class ItemInvalidError(ItemError):
    pass

def bagging(cm):
    bagging.marked[cm] = True
    return cm
bagging.marked = {}


def storing(cm):
    storing.marked[cm] = True
    return cm
storing.marked = {}


class DelegationHelper(object):
    def _make_delegation_maker(self, cls, b):
        def invoker(*args, **kwargs):
            return b.__get__(cls)(self, *args, **kwargs)
        return invoker

    def _delegate_from_class(self, cls, marked):
        for k, v in cls.__dict__.items():
            if isinstance(v, classmethod) and v in marked:
                setattr(self, k, self._make_delegation_maker(cls, v))


class Store(DelegationHelper):
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
            self._delegate_from_class(mc, storing.marked)
            setattr(self, mc.bag_name, self._make_bag(mc))

    @property
    def fresh(self):
        return self._fresh

    @classmethod
    def drop(cls, name):
        conn = boto.connect_dynamodb()
        if name in conn.list_tables():
            conn.delete_table(conn.get_table(name))


class Bag(DelegationHelper):
    range_key_name = "range"
    table_key_name = "hash"

    def __init__(self, model_class, table, **kwargs):
        self.table = table
        self.model_class = model_class
        self._delegate_from_class(self.model_class, bagging.marked)
            
    @classmethod
    def _to_item_hash(cls, k):
        return "#" + k

    @classmethod
    def _from_item_hash(clses, i):
        if i.find("#") < 0:
            raise ValueError(i + " is not a hash key")
        return i[1:]

    @property
    def _item_range_prefix(self):
        return self.name

    def _to_item_range(self, ord):
        return u".".join([self._item_range_prefix, ord])

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
    
    def _list_item(self):
        filter = { Store.range_key_name: condition.BEGINS_WITH(self._item_range_prefix) }
        return self.table.scan(scan_filter=filter)

    def _query_item(self, key):
        return self.table.query(self._to_item_hash(key), condition.BEGINS_WITH(self._item_range_prefix))

    @property
    def name(self):
        return self.model_class.bag_name

    def add(self, m, can_replace=False):
        try:
            m.validate().raise_if_invalid()
            item_toadd = self._new_item(key=m.key, ord=m.ord, attrs=m.to_item_values())
            self._insert_item(item_toadd, can_replace)
            self._decorate(m, item_toadd)
            return m
        except ItemError, e:
            raise m.translate_error(e) or e

    def find(self, key, ord=None):
        # FIXME: Better to wrap the exception?
        return self.to_m(self._get_item(key, ord or self.model_class.default_ord_value))

    def list(self):
        # FIXME: should use generator
        return [ self.to_m(i) for i in self._list_item() ]

    def query(self, key):
        # FIXME: should use generator
        return [ self.to_m(i) for i in self._query_item(key) ]

    def remove(self, m):
        m._item.delete()

    def remove_found(self, key, ord=None):
        # XXX: Use one-shot underling API.
        try:
            found = self.find(key, ord)
            self.remove(found)
        except ItemNotFoundError:
            pass
        
    def to_m(self, item):
        model = self.model_class.from_item(item)
        self._decorate(model, item)
        return model

    def _decorate(self, model, item):
        model._item = item


class StuffAttr(object):
    def __init__(self, name):
        self.name = name


class StuffKey(StuffAttr):
    pass


class StuffOrd(StuffAttr):
    pass


class StuffMeta(type):
    @classmethod
    def make_getter(cls, attr):
        def generated_getter(self):
            return self._dict.get(attr.name)
        return generated_getter

    def find_key_attr_name(cls, attrs):
        found = [a.name for a in attrs if isinstance(a, StuffKey)]
        if not found:
            if cls.__name__ != "Stuff":
                raise Exception("Stuff needs key attribute: " + str(cls))
            return None
        return found[0]

    def find_ord_attr_name(cls, attrs):
        found = [a.name for a in attrs if isinstance(a, StuffOrd)]
        if not found:
            return None
        return found[0]

    def __new__(mcs, name, bases, dict):
        cls = type.__new__(mcs, name, bases, dict)
        attrs = dict.get("attributes", [])
        for attr in attrs:
            setattr(cls, attr.name, property(StuffMeta.make_getter(attr)))
        setattr(cls, "key_attr_name", cls.find_key_attr_name(attrs))
        setattr(cls, "ord_attr_name", cls.find_ord_attr_name(attrs))
        return cls


class Stuff(object):
    __metaclass__ = StuffMeta

    default_ord_value = "0"
    ord_attr_name = ""
    key_attr_name = ""

    def __init__(self, dict={}):
        self._dict = dict

    def get_value(self, name):
        return self._dict[name]

    def __eq__(self, other):
        return self._dict == other._dict

    def to_item_values(self):
        return { "dict": json.dumps(self._dict) }

    def validate(self):
        v = validation.Validator(self)
        return v

    def translate_error(self, exception):
        return None

    @property
    def dict(self):
        return self._dict

    @classmethod
    def from_item(cls, item):
        d = item.get("dict")
        return cls(json.loads(d) if d else {})

    @property
    def ord(self):
        if self.ord_attr_name:
            assert hasattr(self, self.ord_attr_name)
            return getattr(self, self.ord_attr_name, None) or self.default_ord_value
        return self.default_ord_value

    @property
    def key(self):
        assert self.key_attr_name
        assert hasattr(self, self.key_attr_name)
        return getattr(self, self.key_attr_name, None)

    @classmethod
    def fill_mock_bag(cls, bag):
        pass


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
            key = self._key_from(item.range_key, item.hash_key)
            if self._items.get(key):
                raise ItemInvalidError("conflict: " + key)
        self._items[self._key_from(item.range_key, item.hash_key)] = item

    def delete_item(self, item):
        del self._items[self._key_from(item.range_key, item.hash_key)]

    def scan(self, scan_filter):
        return self._items.values()

    def query(self, hash, cond):
        assert hash
        assert isinstance(cond, condition.BEGINS_WITH)
        return [ i for i in self._items.values() if i.hash_key == hash and i.range_key.startswith(cond.v1) ]
