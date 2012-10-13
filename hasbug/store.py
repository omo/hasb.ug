
import datetime
import boto
import boto.dynamodb.exceptions

NotFoundError = boto.dynamodb.exceptions.DynamoDBKeyNotFoundError

class Store(object):
    READ_UNIT   = 1
    WRITE_UNIT  = 1

    def __init__(self, name, bag_classes=[], should_have_table=False):
        self._conn = boto.connect_dynamodb()
        has_table = should_have_table or (name in self._conn.list_tables())
        if has_table:
            self._table = self._conn.get_table(name)
            self._fresh = False
        else:
            schema = self._conn.create_schema(hash_key_name='hash', hash_key_proto_value='S', range_key_name='range', range_key_proto_value='S')
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
    def __init__(self, table):
        self.table = table

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def _bless(self, attr):
        boilerplate = { "created_at": datetime.datetime.utcnow().isoformat() }
        boilerplate.update(attr)
        return boilerplate

    def range_of(self, index):
        return u".".join([self.name, str(index)])

    def new_item(self, key, at=0, attrs={}):
        return self.table.new_item(hash_key=key, range_key=self.range_of(at), attrs=self._bless(attrs))

    def get_item(self, key, at=0):
        return self.table.get_item(hash_key=key, range_key=self.range_of(at))