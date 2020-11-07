from typing import Union, Dict, List


class FieldError(Exception):
    pass


def verify_json_fields(obj: dict, fields: Union[List[str], Dict[str, type]]):
    if isinstance(fields, List):
        fields = {f: None for f in fields}
    for field_name, field_type in fields.items():
        if field_name not in obj:
            raise FieldError(f"Field {field_name} not found in object.")
        elif field_type is not None and isinstance(field_type, type):
            if not isinstance(obj[field_name], field_type):
                raise FieldError(f"Field type check failed, {field_name} is not {field_type}")
