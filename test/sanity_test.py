import unittest
from jsonproto import jsonproto


class TestJsonToProto(unittest.TestCase):
    def test_simple_json_to_proto(self):
        data = {"name": "Jimmy", "age": 42}
        proto_data, msg_class = jsonproto.json_to_proto(data)
        self.assertIsNotNone(proto_data)
        msg = msg_class()
        msg.ParseFromString(proto_data)
        self.assertEqual(msg.name, "Jimmy")

    def test_with_fields_json_to_proto(self):
        data = {"name": "Jimmy", "age": 42}
        field_numbers = {"name": 4, "age": 10}
        proto_data, msg_class = jsonproto.json_to_proto(data, field_numbers)
        self.assertIsNotNone(proto_data)
        msg = msg_class()
        msg.ParseFromString(proto_data)
        self.assertEqual(msg.name, "Jimmy")

    def test_with_nested_json_to_proto(self):
        data = {
            "name": "Jimmy",
            "age": 42,
            "address": {"street": "Main St", "city": "New York"},
        }
        field_numbers = {
            "name": 4,
            "age": 10,
            "address": 3,
            "address.street": 3,
            "address.city": 5,
        }
        proto_data, msg_class = jsonproto.json_to_proto(data, field_numbers)
        self.assertIsNotNone(proto_data)
        msg = msg_class()
        msg.ParseFromString(proto_data)
        self.assertEqual(msg.name, "Jimmy")
        self.assertEqual(msg.address.street, "Main St")
        self.assertEqual(msg.address.city, "New York")

    def test_with_list_as_repeated_strings(self):
        data = {"name": "Jimmy", "age": 42, "children": ["Cleo", "Clara"]}
        field_numbers = {"name": 4, "age": 10, "children": 3}
        proto_data, msg_class = jsonproto.json_to_proto(data, field_numbers)
        self.assertIsNotNone(proto_data)

        msg = msg_class()
        msg.ParseFromString(proto_data)
        self.assertEqual(msg.name, "Jimmy")
        self.assertEqual(msg.children, ["Cleo", "Clara"])

    def test_with_list_as_repeated_objects(self):
        data = {"name": "Jimmy", "age": 42, "children": [{"data": 1}, {"data": 2}]}
        field_numbers = {"name": 4, "age": 10, "children": 3}
        proto_data, msg_class = jsonproto.json_to_proto(data, field_numbers)
        self.assertIsNotNone(proto_data)
        msg = msg_class()
        msg.ParseFromString(proto_data)
        self.assertEqual(msg.name, "Jimmy")
        self.assertEqual(msg.children[0].data, 1)
        self.assertEqual(msg.children[1].data, 2)

    def test_with_empty_list(self):
        data = {"name": "Jimmy", "age": 42, "children": []}
        proto_data, msg_class = jsonproto.json_to_proto(data)
        self.assertIsNotNone(proto_data)
        msg = msg_class()
        msg.ParseFromString(proto_data)
        self.assertEqual(msg.name, "Jimmy")
        self.assertEqual(msg.children, [])
