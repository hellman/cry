from .base import bases
from .gen import gen

try:
    from sage.crypto.sbox import SBox
except:
    # old version
    from sage.crypto.mq import SBox
bases.append(SBox)

SBox2 = type("SBox2", tuple(bases), {
    "__doc__": """Extended SBox class""",
})
SBox2.new = SBox2
SBox2.gen.new = SBox2
SBox2.gen.SBox2 = SBox2

for base in bases:
    base.SBox2 = base.cls = base.new = SBox2
    base.base = SBox
