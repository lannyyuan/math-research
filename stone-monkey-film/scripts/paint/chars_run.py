"""python3 chars_run.py [name ...]  —— 画指定的（或全部）精灵。名字是各 @sprite 函数的名字。"""
import sys
import chars_new, chars_b, chars_c, chars_d   # noqa
from chars_new import REG

if __name__ == '__main__':
    names = sys.argv[1:] or list(REG)
    for n in names:
        REG[n]()
