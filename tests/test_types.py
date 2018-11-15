from shadowdp.types import TypeSystem


def test_type_system():
    types = TypeSystem()
    types.update_distance('a', '*', '*')
    assert types.get_distance('a') == ('__LANG_distance_a', '__LANG_distance_shadow_a')
