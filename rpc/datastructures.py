from django.utils.datastructures import MultiValueDict


class RpcMultiValueDict(MultiValueDict):
    """
    Just allow pass not list values and get only dict as argument
    """

    def __init__(self, key_to_list_mapping={}):
        for key, value in key_to_list_mapping.items():
            if not isinstance(value, (list, tuple)):
                key_to_list_mapping[key] = [value]

        super(MultiValueDict, self).__init__(key_to_list_mapping)
