#-*- coding:utf-8 -*-

# from Queue import Queue

class LEContext(object):
    def __init__(self, s1, s2, findall=False):
        self.dim_in = s1.m
        self.dim_out = s1.n
        assert s2.m == s1.m
        assert s2.n == s1.n
        self.size_in = 2**self.dim_in
        self.size_out = 2**self.dim_out
        self.s1 = tuple(s1)
        self.s2 = tuple(s2)
        self.s1pre = s1.preimages()
        self.s2pre = s2.preimages()

        self.ret = []
        self.findall = findall

    def run(self):
        if self.s1[0] == 0 and self.s2[0] != 0:
            return False
        if self.s1[0] != 0 and self.s2[0] == 0:
            return False

        s = LEState(self)
        x, y = s.dual_forward(0, 0)
        assert s.learn(1, x, y)
        if not s.reduce_from_out(0, 0):
            return False
        s.check()

        if self.findall:
            return self.ret
        assert len(self.ret) <= 1
        return self.ret[0] if self.ret else False

    def input_range(self, no_zero=False):
        if no_zero:
            return range(1, self.size_in)
        else:
            return range(self.size_in)

    def output_range(self, no_zero=False):
        if no_zero:
            return range(1, self.size_out)
        else:
            return range(self.size_out)

class LEState(object):
    SIDE_A = 0
    SIDE_B = 1

    def __init__(self, ctx, linear_maps=None, unknown_inputs=None, unknown_outputs=None, possible_outputs=None):
        self.ctx = ctx

        self.linear_maps = linear_maps or [{0: 0}, {0: 0}]
        self.unknown_inputs = unknown_inputs or [set(self.ctx.input_range(no_zero=True)) for i in xrange(2)]
        self.unknown_outputs = unknown_outputs or [set(self.ctx.input_range(no_zero=True)) for i in xrange(2)]
        self.possible_outputs = possible_outputs or {}

        self.queue = Queue()
        self.depth = 0

    def copy(self):
        lm2 = [self.linear_maps[i].copy() for i in xrange(2)]
        ui2 = [self.unknown_inputs[i].copy() for i in xrange(2)]
        uo2 = [self.unknown_outputs[i].copy() for i in xrange(2)]
        po2 = self.possible_outputs.copy()
        st = LEState(self.ctx, lm2, ui2, uo2, po2)
        st.depth = self.depth + 1
        return st

    def dual_forward(self, inp, out):
        dual_inp = self.ctx.s1[out]
        dual_out = self.ctx.s2[inp]
        return dual_inp, dual_out

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

    def expand_horizontal(self, side, inp, out):
        if len(self.linear_maps[side]) < len(self.ctx.s1) / 2:
            for old_inp, old_out in self.linear_maps[side].items():
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

    def reduce_from_out(self, inp, out):
        pre_out = self.ctx.s1pre[inp]
        pre_inp = self.ctx.s2pre[out]
        if len(pre_inp) != len(pre_out):
            return False
        for x in pre_inp:
            if x in self.possible_outputs and self.possible_outputs[x] != pre_out:
                return False
            self.possible_outputs[x] = pre_out
        return True

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
                if side == 0:
                    # inp -> out easy
                    new_inp2, new_out2 = self.dual_forward(new_inp, new_out)
                    if not self.learn(side ^ 1, new_inp2, new_out2, queue=True):
                        return False
                else:
                    # out -> inp marks preimages
                    if not self.reduce_from_out(new_inp, new_out):
                        return False

        if len(self.linear_maps[0]) == self.ctx.size_in and len(self.linear_maps[1]) == self.ctx.size_out:
            return self.result_ready()

        # queues are empty
        # need to guess
        inp = min(self.unknown_inputs[0],
            key=lambda inp: len(self.possible_outputs[inp]) if inp in self.possible_outputs else len(self.ctx.s1))
        outs = self.possible_outputs.get(inp, self.unknown_outputs[0])
        for out in outs:
            if out not in self.unknown_outputs[0]:
                continue
            sub = self.copy()
            sub.learn(0, inp, out)
            res = sub.check()
            if res and not self.ctx.findall:
                return res
        return False

    def result_ready(self):
        A = self.ctx.sbox(self.linear_maps[0][x] for x in self.ctx.input_range())
        if not A.is_linear():
            return False
        B = self.ctx.sbox(self.linear_maps[1][x] for x in self.ctx.output_range())
        if not B.is_linear():
            return False

        # result is fine, now yield or continue?
        self.ctx.ret.append((A, B))
        return not self.ctx.findall
# TODO: bug on
#(9, 28, 19, 33, 18, 42, 38, 5, 40, 4, 4, 0, 30, 25, 21, 42, 43, 7, 0, 36, 43, 30, 2, 0, 19, 43, 6, 31, 15, 41, 1, 8, 28, 10, 6, 31, 35, 6, 3, 14, 5, 15, 6, 17, 36, 17, 12, 28, 39, 39, 41, 30, 5, 18, 14, 0, 16, 40, 33, 19, 33, 28, 5, 7, 38, 29, 22, 32, 26, 41, 21, 18, 24, 40, 5, 24, 0, 10, 27, 27, 3, 34, 22, 14, 12, 15, 19, 14, 26, 0, 22, 37, 6, 39, 33, 7, 28, 38, 4, 26, 18, 18, 26, 42, 21, 39, 0, 7, 11, 0, 1, 13, 35, 26, 2, 35, 25, 41, 18, 3, 38, 40, 26, 22, 34, 6, 20, 10, 6, 33, 20, 35, 21, 13, 0, 32, 14, 40, 31, 40, 0, 37, 21, 12, 29, 40, 9, 39, 23, 24, 8, 23, 11, 12, 30, 33, 16, 9, 43, 40, 29, 2, 5, 38, 31, 1, 19, 10, 21, 24, 38, 32, 31, 20, 42, 20, 37, 23, 7, 3, 0, 22, 18, 8, 23, 9, 38, 39, 23, 14, 42, 25, 13, 43, 30, 21, 32, 21, 29, 16, 35, 38, 13, 8, 25, 8, 16, 38, 38, 12, 15, 22, 22, 5, 27, 17, 14, 5, 27, 11, 11, 10, 35, 22, 1, 28, 29, 30, 4, 22, 15, 7, 2, 15, 43, 11, 13, 11, 42, 33, 27, 43, 2, 26, 42, 36, 3, 30, 35, 37, 10, 0, 35, 37, 29, 27)
# n=8, selfequiv linear
