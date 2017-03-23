import sys
from collections import defaultdict
from itertools import product

def get_vocab(fname):
    vocab = defaultdict(lambda : len(vocab))
    sents = []
    with open(fname) as fin:
        for line in fin:
            sent = []
            fields = line.strip().split()
            for field in fields:
                index = vocab[field]
                sent.append(index)
            sents.append(sent)
    return vocab, sents


def train(de_sents, en_sents, normal_vocab_size):
    iter = 30
    # a new initialization method
    transProb = defaultdict(float)
    init_e_f = defaultdict(set)
    for de_sent, en_sent in zip(de_sents, en_sents):
        for (f, e) in product(de_sent, en_sent):
            init_e_f[f].add((e, f))
    for f, eset in init_e_f.iteritems():
        init_value = [1.0 / len(eset)] * len(eset)
        transProb.update(zip(eset, init_value))
    for it in range(iter):
        e_f_count = defaultdict(lambda : 0)
        f_count = defaultdict(lambda : 0)
        for de_sent, en_sent in zip(de_sents, en_sents):
            s_e = defaultdict(lambda : 0)
            for e in en_sent:
                for f in de_sent:
                    s_e[e] += transProb[(e, f)]

            for e in en_sent:
                for f in de_sent:
                    assert s_e[e] != 0, "error, divide zero"
                    cc = transProb[(e, f)] / s_e[e]
                    e_f_count[(e, f)] += cc
                    f_count[f] += cc
        for e, f in e_f_count.keys():
            assert f_count[f] != 0, "error, divide zero"
            cc = e_f_count[(e, f)] * 1.0 / f_count[f]
            transProb[(e, f)] = cc
            # print(transProb[(e, f)])
        print("Training iteration = %d" % (it+1))
    return transProb


def getAlignment(en_sent, de_sent, transProb):
    max_pos = -3
    alignment = []
    for j, f in enumerate(de_sent):
        max_score = float("-inf")
        prior = 1.0
        for i, e in enumerate(en_sent):
            score = transProb[(e, f)] * prior
            if score > max_score:
                max_score = score
                max_pos = i
        alignment.append((max_pos, j))
    return alignment


if __name__ == '__main__':
    fde = sys.argv[1]
    fen = sys.argv[2]
    de_vocab, de_sents = get_vocab(fde)
    en_vocab, en_sents = get_vocab(fen)

    reverse = False
    inter = False
    fout = open(sys.argv[3], "w")
    if reverse:
        feTransProb = train(en_sents, de_sents, len(de_vocab))
        for en_sent, de_sent in zip(en_sents, de_sents):
            fe_align = getAlignment(de_sent, en_sent, feTransProb)
            alignment = []
            for (ff, ee) in fe_align:
                alignment.append(str(ee) + '-' + str(ff))
            fout.write(" ".join(alignment) + '\n')
        fout.close()
        exit(0)

    efTransProb = train(de_sents, en_sents, len(en_vocab))
    if inter:
        feTransProb = train(en_sents, de_sents, len(de_vocab))
        for en_sent, de_sent in zip(en_sents, de_sents):
            ef_align = getAlignment(en_sent, de_sent, efTransProb)
            fe_align = getAlignment(de_sent, en_sent, feTransProb)
            alignment = []
            for (e, f) in ef_align:
                # intersection = False
                intersection = True
                for (ff, ee) in fe_align:
                    if ff == f and ee == e:
                        intersection = True
                        break
                if intersection:
                    alignment.append(str(e) + '-' + str(f))
            fout.write(" ".join(alignment) + '\n')
    else:
        for en_sent, de_sent in zip(en_sents, de_sents):
            ef_align = getAlignment(en_sent, de_sent, efTransProb)
            alignment = []
            for (e, f) in ef_align:
                alignment.append(str(e) + '-' + str(f))
            fout.write(" ".join(alignment) + '\n')
    fout.close()