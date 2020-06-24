import types
import collections
from google.protobuf.internal.containers \
    import RepeatedScalarFieldContainer, RepeatedCompositeFieldContainer

cpp_implementation = True
try:
    import google.protobuf.pyext._message as __message
except ImportError:
    cpp_implementation = False

_simple_types = (int, long, float, basestring, bool)
_list_types   = (RepeatedScalarFieldContainer, 
                    RepeatedCompositeFieldContainer)
if cpp_implementation:
    _list_types = _list_types + (__message.RepeatedCompositeContainer,
                    __message.RepeatedScalarContainer)

def pb2json(pb, strip_keys=None):
    result = {}
    def get_json(pb, result):
        for field_descriptor, value in pb.ListFields():
            if strip_keys and field_descriptor.name in strip_keys:
                continue
            if isinstance(value, _simple_types):
                result[field_descriptor.name] = value
            elif isinstance(value, _list_types):
                for one_value in value._values if hasattr(value, "_values") else value:
                    if isinstance(one_value, _simple_types):
                        result.setdefault(field_descriptor.name, []). \
                            append(one_value)
                    else:
                        result.setdefault(field_descriptor.name, []). \
                            append(get_json(one_value, {}))
            else:
                get_json(value, result.setdefault(field_descriptor.name, {}))
        return result
    return get_json(pb, result)

class json2pb:
    def __init__(self, pb_module, root_name, strip_keys=None):
        self._module = pb_module if type(pb_module) == types.ModuleType \
                            else __import__(pb_module)
        self._root = getattr(self._module, root_name)()
        self._strip_keys = strip_keys or []

    def deal_sequence(self, k, v, root):
        for _ in v:
            if isinstance(_, _simple_types):
                getattr(root, k).append(_)
            elif isinstance(_, collections.Sequence):
                pass
            elif isinstance(_, collections.Mapping):
                node = getattr(root, k).add()
                self.deal_mapping(_, node)
        return root

    def deal_mapping(self, obj, root):
        for k, v in obj.items():
            if k in self._strip_keys or k not in root.DESCRIPTOR.fields_by_name:
                continue
            if isinstance(v, _simple_types):
                setattr(root, k, v)
            elif isinstance(v, collections.Mapping):
                self.deal_mapping(v, getattr(root, k))
            elif isinstance(v, collections.Sequence):
                self.deal_sequence(k, v, root)
        return root

    def get_pb(self, json_obj):
        assert isinstance(json_obj, collections.Mapping)
        self.deal_mapping(json_obj, self._root)
        return self._root

