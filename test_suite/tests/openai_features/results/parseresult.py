import os

with open('/home/great/projects/eva_apps/evadb-slack-bot/test_suite/tests/openai_features/results/result final for feature embedders.tx', 'r') as f:
    k = f.readlines()
    kb = []
    i = 0
    c = -1
    while(i<len(k)):
        if 'Knowledge body' in k[i]:
            kb.append([])
            c+=1
        if '#######' in k[i]:
            
