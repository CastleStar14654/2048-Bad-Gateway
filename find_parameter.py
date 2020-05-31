#!/usr/bin/env python

import sys

sys.path.append('sessdsa.2048/src/tools/')
from round_match import main

import restart

base_powers = (1.5, 1.75, 2, 2.25, 2.5)
enemy_weights = (1, 1.25, 1.5)

groups = [(b, e) for b in base_powers for e in enemy_weights]
groups.remove((2, 1.25))

num = int(sys.argv[1])
assert 0 <= num < 8

if num == 8:
    print('self begin')
    main(['../../../restart.py', f'../../../restart.py'], debug=True, REPEAT=40, MAXTIME=40)
    print('self end')
else:
    groups = groups[2 * num: 2 * num + 2]
    for b, e in groups:
        b = str(b).replace('.', '')
        e = str(e).replace('.', '')
        print(b, e, 'begin')
        main(['../../../restart.py', f'../../../restart_{b}_{e}.py'], debug=True, REPEAT=40, MAXTIME=40)
        print(b, e, 'end')
