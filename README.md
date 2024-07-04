# jsonproto
Make protobuf messages without generating protos or reflection

Convert json into proto bytes on stdout

```
--data: JSON data to convert to proto
--field-numbers: Field numbers for proto (Optional)
```

Examples:
```bash

$ jsonproto --data '{"name": "Jimmy", "age": 42, "details" : {"ssn": "blah"}}' --field-numbers '{"name": 1, "age": 2, "details.ssn": 5}' > output.bin
$ jsonproto --data '{"name": "Jimmy", "age": 42}' --field-numbers '{"name": 1, "age": 2}' > output.bin
$ jsonproto --data '{"name": "Jimmy", "age": 42}' > output.bin
```
