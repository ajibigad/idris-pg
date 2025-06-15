
# Online Python - IDE, Editor, Compiler, Interpreter

from typing import Any, Dict, List
import traceback



class Type:
    def __init__(self, name: str):
        self.value = None
        self.name = name

    def set_value(self, value: Any):
        self.value = value

    def validate(self):
        raise NotImplementedError("Subclasses must implement validate method")
    
    def __str__(self):
        return f"{self.name}: {self.value}"
    
    def __repr__(self):
        return self.__str__()


class StringType(Type):
    def __init__(self, name:str, max_len: int = 255):
        super().__init__(name)
        self.max_len = max_len

    def set_value(self, value: Any):
        self.value = value

    def validate(self):
        assert isinstance(self.value, str), f"Value must be a string - {self.name}: {self.value}"
        assert len(self.value) <= self.max_len, f"String exceeds max length- {self.name}: {self.value}"
        assert self.value.startswith("'") and self.value.endswith("'"), \
            f"String must be enclosed in single quotes (e.g., 'value') - {self.name}: {self.value}"
        
    def __str__(self):
        return f"{self.name}: {self.value}. Max len: ({self.max_len})"


class IntType(Type):
    def __init__(self, name:str):
        super().__init__(name)
    
    def validate(self):
        if isinstance(self.value, str):
            assert self.value.isdigit(), f"Value must be an integer - {self.name}: {self.value}"
        else: 
            assert isinstance(self.value, int), f"Value must be an integer - {self.name}: {self.value}"


class Schema:
    fields: Dict[str, Type]

    def __init__(self, fields: Dict[str, Type] = None):
        self.fields = fields

    def set_values(self, values: List[Any] = None):
        if values:
            for (k, v), value in zip(self.fields.items(), values):
                v.set_value(value)
            self.build()

    def validate(self):
        for key, field in self.fields.items():
            field.validate()

    def build(self):
        self.validate()
        return self

    def __getattr__(self, key):
        if key in self.fields:
            return self.fields[key].value
        raise AttributeError(f"{key} not found")

    def __setattr__(self, key, value):
        if key in ("fields"):
            super().__setattr__(key, value)
        elif key in self.fields:
            self.fields[key].set_value(value)
        else:
            super().__setattr__(key, value)

    def __call__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.fields:
                self.fields[key].set_value(val)
        return self

    def fieldlen(self):
        return len(self.fields)
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        resp = ""
        for k, v in self.fields.items():
            resp += f"{k}: {v.value}\n"
        return resp


class Datastore:
    def __init__(self):
        self.store = []

    def save(self, data: Schema):
        self.store.append(data)
        return len(self.store) - 1, data

    def load(self, index: int):
        if index > len(self.store) - 1:
            return None
        return self.store[index]
    
    def clear(self):
        self.store = []


class User(Schema):
    fields = {
        "firstname": StringType("firstname", 255),
        "lastname": StringType("lastname", 255),
        "age": IntType("age"),
    }

class Deserializer:
    @classmethod
    def deserialize(self, schema: Schema, data: str) -> Schema:
        values = data.split(" ")
        assert len(values) == schema.fieldlen(), f"Incorrect number of fields. Expected {schema.fieldlen()}, Actual {len(values)}"
        schema.set_values(values)

        return schema

class Program:
    current_schema: str
    datastore: Datastore
    
    def __init__(self):
        self.datastore = Datastore()
        self.current_schema = None
    
    def key2type(self, key):
        if key == "string":
            return StringType
        if key == "int":
            return IntType
            
    def unpack_type(self, details: str):
        fieldname = details[0]
        typez = self.key2type(details[1])
        if typez == StringType:
            return StringType(fieldname, int(details[2]))
        if typez == IntType:
            return IntType(fieldname)
            
    def set_schema(self, schema_template: str):
        self.current_schema = schema_template
        self.datastore.clear()

    def create_schema_instance(self, schema_template: str):
        types = schema_template.split(" ")
        fields = {}
        for t in types:
            type_props = t.split("|")
            fieldname = type_props[0]
            typz = self.unpack_type(type_props)
            fields[fieldname] = typz
            
        return Schema(fields)
        
    def add(self, data: str):
        if not self.current_schema:
            print("No schema defined")
            return
        schema_instance = self.create_schema_instance(self.current_schema)
        record = Deserializer.deserialize(schema_instance, data)
        return self.datastore.save(record)
        
    def get(self, index: str):
        return self.datastore.load(int(index))
            
    def run(self):
            while True:
                try:
                    line = input(">>> ").strip()
                    if not line:
                        continue
    
                    # Split command and arguments
                    parts = line.split(" ", 1)
                    cmd = parts[0].replace("-", "_")
                    arg = parts[1] if len(parts) > 1 else ""
    
                    # Check if method exists
                    if hasattr(self, cmd):
                        method = getattr(self, cmd)
                        if callable(method):
                            print(method(arg))
                        else:
                            print(f"{cmd} is not callable")
                    else:
                        print(f"Unknown command: {cmd}")
                except EOFError:
                    print("\nExiting on EOF.")
                    exit(0)
                except Exception as e:
                    traceback.print_exc()
        

# ==== MAIN ====
def main():
    program = Program()
    program.run()

main()

def test():
    datastore = Datastore()
    
    user = User().__call__(firstname="'John'", lastname="'Doe'", age=30).build()
    i = datastore.save(user)
    datastore.load(i).print()
    
    user2 = Deserializer(User).deserialize("'25' 'Jane' '26'")
    user2.print()

