import sys
from collections import defaultdict
import math

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
    rvocab = {v:k for k, v in vocab.items()}
    return vocab, rvocab, sents


def isQuasiConsecutive(tp):
    # since we don't have null alignments
    tt = sorted(tp)
    # print(tt)
    if len(tt) > 4:
        return False
    if len(tt) == 1:
        return True
    forward = True
    for i in range(1, len(tt)):
        # print(i, tt[i], tt[i-1])
        if tt[i] != tt[i-1] + 1:
            forward = False
            break
    return forward

def phrase_extraction(en_sent, de_sent, alignment):
    TP_base = defaultdict(list)
    SP_base = defaultdict(list)
    BP = []
    # print(alignment)
    for e, f in alignment:
        e = int(e)
        f = int(f)
        TP_base[e].append(f)
        SP_base[f].append(e)
    for e, f in alignment:
        if len(TP_base[e]) != 0:
            print(TP_base[e])
        if len(TP_base[f]) != 0:
            print(SP_base[f])
    for i1 in range(0, len(en_sent)):
        for i2 in range(i1, len(en_sent)):
            if i2 - i1 + 1 > 4:
                continue
            TP = []
            for i in range(i1, i2+1):
                TP.extend(TP_base[i])
            if len(TP) == 0:
                continue

            if isQuasiConsecutive(list(set(TP))):
                j1 = min(TP)
                j2 = max(TP)
                SP = []
                for j in range(j1, j2 + 1):
                    SP.extend(SP_base[j])
                if set(SP).issubset(set(range(i1, i2 + 1))):
                    BP.append((i1, i2, j1, j2))
                    while j1 > 0 and j1 not in SP_base:
                        j_prime = j2
                        while j_prime < len(de_sent) and j_prime not in SP_base:
                            BP.append((i1, i2, j1, j_prime))
                            j_prime += 1
                        j1 -= 1
    return BP

if __name__ == '__main__':
    fde = sys.argv[1]
    fen = sys.argv[2]
    falign = sys.argv[3]
    foutput = sys.argv[4]
    de_vocab, r_de_vocab, de_sents = get_vocab(fde)
    en_vocab, r_en_vocab, en_sents = get_vocab(fen)

    alignments = []
    with open(falign) as fin:
        for line in fin:
            alignment = []
            fields = line.strip().split()
            for field in fields:
                pair = field.split('-')
                alignment.append(pair)
            alignments.append(alignment)

    idx = 0
    phrases = defaultdict(dict)
    for en_sent, de_sent in zip(en_sents, de_sents):
        if idx == len(alignments):
            break
        alignment = alignments[idx]
        phrase = phrase_extraction(en_sent, de_sent, alignment)
        for p in phrase:
            enp = []
            dep = []
            for i in range(p[0], p[1]+1):
                enp.append(r_en_vocab[en_sent[i]])
            for i in range(p[2], p[3]+1):
                dep.append(r_de_vocab[de_sent[i]])
            if " ".join(dep) in phrases[" ".join(enp)]:
                phrases[" ".join(enp)][" ".join(dep)] += 1
            else:
                phrases[" ".join(enp)][" ".join(dep)] = 1
        idx += 1

    # calculate score and output
    with open(foutput, "w") as fout:
        for enp in phrases.keys():
            pp = []
            score = []
            for dep in phrases[enp].keys():
                pp.append(dep)
                score.append(phrases[enp][dep])
            tot = sum(score)
            for i, p in enumerate(pp):
                if score[i] < 3:
                    tot -= score[i]
                    break
                ss = -math.log(score[i] * 1.0/tot)
                ss = ss if ss > 0.0 else 0.000
                fout.write(p + '\t' + enp + '\t' + str(ss) + '\n')
