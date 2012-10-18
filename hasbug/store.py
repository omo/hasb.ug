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

    def __init__(self, name, bag_classes=[], should_have_table=False):
        self._conn = boto.connect_dynamodb()
        has_table = should_have_table or (name in self._conn.list_tables())
        if has_table:
            self._table = self._conn.get_table(name)
            self._fresh = False
        else:
            schema = self._conn.create_schema(hash_key_name=self.hash_key_name, hash_key_proto_value='S', range_key_name=self.range_key_name, range_key_proto_value='S')
            self._table = self._conn.create_table(name=name, schema=schema, read_units=self.READ_UNIT, write_units=self.WRITE_UNIT)
            self._fresh = True
        for bag in [cls(self._table) for cls in bag_classes]:
            setattr(self, bag.name, bag)

    @property
    def fresh(self):
        return self._fresh

    @classmethod
    def drop(cls, name):
        conn = boto.connect_dynamodb()
        if name in conn.list_tables():
            conn.delete_table(conn.get_table(name))


class Bag(object):
    range_key_name = "range"
    table_key_name = "hash"

    def __init__(self, table):
        self.table = table
        self.name = self.__class__.__name__.lower()

    @classmethod
    def to_internal_key(cls, k):
        return "#" + k

    @classmethod
    def from_internal_key(cls, i):
        if i.find("#") < 0:
            raise ValueError(i + " is not a hash key")
        return i[1:]

    def _bless(self, attr):
        boilerplate = { "created_at": datetime.datetime.utcnow().isoformat() }
        boilerplate.update(attr)
        return boilerplate

    def range_of(self, index):
        return u".".join([self.name, str(index)])

    def new_item(self, key, at=0, attrs={}):
        return self.table.new_item(range_key=self.range_of(at), hash_key=self.to_internal_key(key), attrs=self._bless(attrs))
    
    def get_item(self, key, at=0):
        try:
            return self.table.get_item(range_key=self.range_of(at), hash_key=self.to_internal_key(key))
        except exceptions.DynamoDBKeyNotFoundError, ex:
            raise ItemNotFoundError(str(ex))

    def insert_item(self, item):
        try:
            item.put(expected_value={ Store.hash_key_name: False, Store.range_key_name: False })
        except exceptions.DynamoDBConditionalCheckFailedError, ex:
            raise ItemInvalidError(str(ex))

    def list_item(self, at):
        filter = { Store.range_key_name: condition.EQ(self.range_of(at)) }
        return self.table.scan(scan_filter=filter)

