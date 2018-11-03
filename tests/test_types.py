from lang.types import TypeSystem


def test_type_system():
    types = TypeSystem()
    types['a'] = ['*', '*']
    assert types['a'] == ['__LANG_distance_a', '__LANG_distance_shadow_a']
