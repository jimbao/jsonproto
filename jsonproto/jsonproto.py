#!/usr/bin/env python3

"""
Write proto format to stdout from json data

--data: JSON data to convert to proto
--field-numbers: Field numbers for proto

Example:

$ python jsonproto.py --data '{"name": "John", "age": 30, "details" : {"ssn": "blah"}}' --field-numbers '{"name": 1, "age": 2, "details.ssn": 5}' > output.bin
$ python jsonproto.py --data '{"name": "John", "age": 30}' --field-numbers '{"name": 1, "age": 2}' > output.bin
$ python jsonproto.py --data '{"name": "John", "age": 30}' > output.bin

"""

import json
import os
import sys
import hashlib
from importlib.metadata import version
from argparse import ArgumentParser, Namespace
from typing import Tuple, Union

from google.protobuf import (
    json_format,
    descriptor_pb2,
    message_factory,
    descriptor_pool,
)
from google.protobuf.message import Message
from collections import OrderedDict

field_types = {
    float: descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE,
    int: descriptor_pb2.FieldDescriptorProto.TYPE_INT64,
    str: descriptor_pb2.FieldDescriptorProto.TYPE_STRING,
    bool: descriptor_pb2.FieldDescriptorProto.TYPE_BOOL,
    OrderedDict: descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
    dict: descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE,
}

file_prefix = "jsonproto.v1.Generated_"


def create_parser() -> ArgumentParser:
    argument_parser = ArgumentParser()
    argument_parser.add_argument(
        "--data", default="{}", type=str, help="JSON data to convert to proto"
    )
    argument_parser.add_argument(
        "--field-numbers", default="{}", type=str, help="Field numbers for proto"
    )
    argument_parser.add_argument(
        "--version", help="Print version and exit", action="store_true"
    )

    return argument_parser


def find_proto_class(pool: descriptor_pool.DescriptorPool, name: str) -> Message:
    proto_descriptor = pool.FindMessageTypeByName(name)
    proto_cls = message_factory.GetMessageClass(proto_descriptor)
    return proto_cls


def get_proto_name(dict_data: dict) -> str:
    fields_hash = hashlib.sha1()
    for f_name, f_type in dict_data.items():
        fields_hash.update(f_name.encode("utf-8"))
        fields_hash.update(str(f_type).encode("utf-8"))
    proto_class_name = file_prefix + fields_hash.hexdigest()
    return proto_class_name


def create_proto_class(
    data: Union[dict, list],
    field_numbers={},
    field_key="",
    pool_instance=descriptor_pool.DescriptorPool(),
) -> Message:
    proto_class_name = get_proto_name(data)
    proto_file_name = proto_class_name + ".proto"

    try:
        proto_cls = find_proto_class(pool=pool_instance, name=proto_class_name)
        return proto_cls
    except KeyError:
        # The factory's DescriptorPool doesn't know about this class yet.
        pass

    package, name = proto_class_name.rsplit(".", 1)
    file_proto = descriptor_pb2.FileDescriptorProto()
    file_proto.name = os.path.join(package.replace(".", "/"), proto_file_name)
    file_proto.package = package
    desc_proto = file_proto.message_type.add()
    desc_proto.name = name

    for i, (k, v) in enumerate(data.items(), 1):
        field_proto = desc_proto.field.add()
        default = descriptor_pb2.FieldDescriptorProto()
        field_type = default.type
        value = None

        if isinstance(v, list):
            field_proto.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
            if v:
                field_type = field_types[type(v[-1])]
                value = v[-1]
        else:
            field_type = field_types[type(v)]
            field_proto.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
            value = v

        field_proto.name = k
        field_proto.number = field_numbers.get(field_key + k) or i
        field_proto.type = field_type
        if field_type == descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE:
            field_proto.type_name = get_proto_name(value)
            create_proto_class(
                data=value,
                field_numbers=field_numbers,
                field_key=field_key + k + ".",
                pool_instance=pool_instance,
            )

    pool_instance.Add(file_proto)
    return find_proto_class(pool_instance, proto_class_name)


def json_to_proto(data: dict = {}, field_numbers: dict = {}) -> Tuple[bytes, Message]:
    proto_class = create_proto_class(data=data, field_numbers=field_numbers)
    proto_msg = json_format.ParseDict(data, proto_class())
    proto_data = proto_msg.SerializeToString()
    return proto_data, proto_class


def run(args: Namespace):
    data: dict = json.loads(args.data, object_pairs_hook=OrderedDict)
    numbers: dict = json.loads(args.field_numbers)
    (proto, _) = json_to_proto(data, numbers)
    sys.stdout.buffer.write(proto)


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.version:
        sys.stdout.buffer.write((version("jsonproto") + "\n").encode("utf-8"))
        exit(0)
    run(args)


if __name__ == "__main__":
    main()
