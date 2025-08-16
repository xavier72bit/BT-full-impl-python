import json
import hashlib


__all__ = ['compute_hash']


def compute_hash(data: dict) -> str:
    """
    计算字典类型的数据hash:
        dict -> json str -> hash result

    :param data: 字典类型的数据
    :return: str
    """
    data_json = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(data_json).hexdigest()
