from dragonmapper import hanzi


def to_pinyin(sent):
    return hanzi.to_pinyin(sent, accented=False)
