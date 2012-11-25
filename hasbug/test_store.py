
import boto
import boto.dynamodb.exceptions
import time
import unittest
import hasbug
import hasbug.testing as testing
import hasbug.store as store

@unittest.skipIf(not testing.enable_database, "Database test is disabled")
class DatabaseTest(unittest.TestCase):
    def test_hello(self):
        conn = boto.connect_dynamodb()
        tables = conn.list_tables()
        self.assertTrue(u'hello' in tables)


class TestModel(object):
    pass


class TestBag(hasbug.Bag):
    def __init__(self, *args, **kwargs):
        super(TestBag, self).__init__(*args, **kwargs)
        self.model_class = TestModel
    
    @classmethod
    def fill_mock_table(cls, table):
        pass


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.target = hasbug.Store(testing.TABLE_NAME if testing.enable_database else None, [TestBag])

    @unittest.skipIf(not testing.enable_database, "Database test is disabled")
    def test_fresh(self):
        self.assertFalse(self.target.fresh)

    def test_hello(self):
        self.assertIsInstance(self.target.testbag, TestBag)

    def test_bag(self):
        target_bag = self.target.testbag
        self.assertEquals(target_bag.name, "testbag")
        self.assertEquals(target_bag.to_internal_range("0"), u"testbag.0")

        created = target_bag.new_item(hash="foobar", ord="0", attrs={"foo": "Foo"})
        created.put_attribute("bar", "Bar")
        created.put()
        created.save()

        found = target_bag.get_item("foobar", "0")
        self.assertEquals("Foo", found.get("foo"))
        self.assertEquals("Bar", found.get("bar"))

        found.delete()
        def run():
            deleted = target_bag.get_item("foobar", "0")
        self.assertRaises(store.ItemNotFoundError, run)

