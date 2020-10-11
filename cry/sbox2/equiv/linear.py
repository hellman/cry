#-*- coding:utf-8 -*-

try:
    from Queue import Queue
except:
    from queue import Queue


class LEContext(object):
    def __init__(self, s1, s2, findall=False):
        self.s1 = tuple(s1)
        self.s2 = tuple(s2)
        self.s1inv = tuple(s1.inverse())
        self.s2inv = tuple(s2.inverse())

        self.ret = []
        self.findall = findall

    def run(self):
        if self.s1[0] == 0 and self.s2[0] != 0:
            return False
        if self.s1[0] != 0 and self.s2[0] == 0:
            return False

        s = LEState(self)
        x, y = s.dual(0, 0, 0)
        assert s.learn(1, x, y)
        x, y = s.dual(1, 0, 0)
        assert s.learn(0, x, y)
        s.check()

        if self.findall:
            return self.ret
        assert len(self.ret) <= 1
        return self.ret[0] if self.ret else False

    def input_range(self, no_zero=False):
        if no_zero:
            return range(1, len(self.s1))
        else:
            return range(len(self.s1))


class LEState(object):
    SIDE_A = 0
    SIDE_B = 1

    def __init__(self, ctx, linear_maps=None, unknown_inputs=None, unknown_outputs=None):
        self.ctx = ctx

        self.linear_maps = linear_maps or [{0: 0}, {0: 0}]
        self.unknown_inputs = unknown_inputs or [set(self.ctx.input_range(no_zero=True)) for i in range(2)]
        self.unknown_outputs = unknown_outputs or [set(self.ctx.input_range(no_zero=True)) for i in range(2)]

        self.queue = Queue()
        self.depth = 0

    def copy(self):
        lm2 = [self.linear_maps[i].copy() for i in range(2)]
        ui2 = [self.unknown_inputs[i].copy() for i in range(2)]
        uo2 = [self.unknown_outputs[i].copy() for i in range(2)]
        st = LEState(self.ctx, lm2, ui2, uo2)
        st.depth = self.depth + 1
        return st

    def learn(self, side, inp, out, queue=True):
        if inp in self.linear_maps[side]:
            return self.linear_maps[side][inp] == out
        elif out not in self.unknown_outputs[side]:
            return False
        self.linear_maps[side][inp] = out
        self.unknown_inputs[side].remove(inp)
        self.unknown_outputs[side].remove(out)
        if queue:
            self.queue.put((side, inp))
        return True

    def dual(self, side, inp, out):
        if side == 0:
            dual_inp = self.ctx.s1[out]
            dual_out = self.ctx.s2[inp]
        else:
            dual_out = self.ctx.s1inv[inp]
            dual_inp = self.ctx.s2inv[out]
        return dual_inp, dual_out

    def expand_horizontal(self, side, inp, out):
        if len(self.linear_maps[side]) < len(self.ctx.s1) / 2:
            for old_inp, old_out in list(self.linear_maps[side].items()):
                new_inp = inp ^ old_inp
                new_out = out ^ old_out
                yield new_inp, new_out
        else:
            for unk_inp in self.unknown_inputs[side].copy():
                old_inp = inp ^ unk_inp
                if old_inp in self.linear_maps[side]:
                    old_out = self.linear_maps[side][old_inp]
                    new_inp = inp ^ old_inp # unk_inp
                    new_out = out ^ old_out
                    yield new_inp, new_out

    def check(self):
        while self.queue.qsize() > 0:
            side, inp = self.queue.get()

            learn_inp = inp
            learn_out = self.linear_maps[side][inp]

            # learn horizontally (same side)
            for new_inp, new_out in self.expand_horizontal(side, learn_inp, learn_out):
                if not self.learn(side, new_inp, new_out, queue=False):
                    return False

                # learn vertically (other side)
                new_inp2, new_out2 = self.dual(side, new_inp, new_out)
                if not self.learn(side ^ 1, new_inp2, new_out2, queue=True):
                    return False

        if len(self.linear_maps[0]) == len(self.linear_maps[1]) == len(self.ctx.s1):
            return self.result_ready()

        # queues are empty
        # need to guess
        inp = min(self.unknown_inputs[0])
        for out in self.unknown_outputs[0]:
            sub = self.copy()
            sub.learn(0, inp, out)
            res = sub.check()
            if res and not self.ctx.findall:
                return res
        return False

    def result_ready(self):
        elems = self.ctx.input_range()
        A = self.ctx.sbox(self.linear_maps[0][x] for x in elems)
        if not A.is_linear():
            return False
        B = self.ctx.sbox(self.linear_maps[1][x] for x in elems)
        if not B.is_linear():
            return False

        # result is fine, now yield or continue?
        self.ctx.ret.append((A, B))
        return not self.ctx.findall
