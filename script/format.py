import re
with open('words.txt', 'r') as f:
    lines = f.readlines()

for i in range(len(lines)):
    line_componenets = lines[i].split()
    if len(line_componenets) < 2:
        continue
    word = line_componenets[0]
    meanings = line_componenets[1:]
    
    for j in range(len(meanings)):
        if '&' in meanings[j]:
            continue
        new_meaning = ''
        is_aplha = True
        for c in meanings[j]:
            if (c >= 'a' and c <= 'z') and not is_aplha:
                new_meaning += '   '
            new_meaning += c
            is_aplha = (c >= 'a' and c <= 'z')
        meanings[j] = new_meaning

    lines[i] = word
    for meaning in meanings:
        lines[i] +=('   ' + meaning)
    lines[i] += '\n'
    

with open('words.txt', 'w') as f:
    f.writelines(lines)


        

