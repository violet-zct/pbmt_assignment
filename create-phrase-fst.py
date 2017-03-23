import sys
from collections import defaultdict

fout = open(sys.argv[2], "w")

init_id = ()
stateid = defaultdict(lambda: len(stateid), {init_id: 0})
with open(sys.argv[1], 'r') as phrase_txt:
    for line in phrase_txt:
        dep, enp, p = line.strip().split('\t')
        last_state = init_id
        for de_word in dep.split():
            current_state = last_state + (de_word, None)
            if current_state not in stateid:
                fout.write('%d %d %s <eps>\n' % (stateid[last_state], stateid[current_state], de_word))
            last_state = current_state
        for en_word in enp.split():
            current_state = last_state + (None, en_word)
            if current_state not in stateid:
                fout.write('%d %d <eps> %s\n' % (stateid[last_state], stateid[current_state], en_word))
            last_state = current_state
        fout.write('%d %d <eps> <eps> %s\n' % (stateid[last_state], stateid[init_id], p))
    fout.write('0 0 </s> </s>\n')
    fout.write('0 0 <unk> <unk>\n')
    fout.write('0\n')

fout.close()