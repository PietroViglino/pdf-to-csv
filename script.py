from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import csv

file_name = 'ANNO_2009'
# text = extract_text(f'pdf-data/{file_name}.pdf', laparams=LAParams(char_margin=5.0, boxes_flow=None)) # fine until 2009 (included) / not 100% accurate
text = extract_text(f'pdf-data/{file_name}.pdf', laparams=LAParams(char_margin=5.0, word_margin=0.05, boxes_flow=None)) # to avoid numbers merging / 100% accurate until 2010

with open(f'txt/{file_name}_read.txt', 'w') as f:
    f.write(text)

# text = text.replace('    01    02    03    04    05    06    07    08    09    10    11    12    13    14    15    16    17    18    19    20    21    22    23    24    25    26    27    28    29    30    31', '@')
text = text.replace('    01     02     03     04     05     06     07     08     09     10     11     12     13     14     15     16     17     18     19     20     21     22     23     24     25     26     27     28     29     30     31', '@')

text = text.replace('PRESIDENZA DEL CONSIGLIO DEI MINISTRI-SERVIZI TECNICI NAZIONALI-SERVIZIO IDROGRAFICO E MAREOGRAFICO NAZIONALE-RETE MAREOGRAFICA NAZIONALE', '@') # for 2002
text = text.replace("APAT-AGENZIA PER LA PROTEZIONE DELL’AMBIENTE E PER I SERVIZI TECNICI-SERVIZIO MAREOGRAFICO-RETE MAREOGRAFICA NAZIONALE", '@') # for 2003, 2004, 2005, 2006, 2007
text = text.replace('ISPRA-ISTITUTO SUPERIORE PER LA PROTEZIONE E LA RICERCA AMBIENTALE-SERVIZIO MAREOGRAFICO-RETE MAREOGRAFICA NAZIONALE', '@') # for 2008, 2009, 2010, 2011, 2012, 2013, 2014

text = text.replace("""Livello (mm)-Pressione (hp)-Temperatura Aria (gr C)     
Valori giornalieri medi (me), minimi (mi) e massimi (ma)
""", '')
text = text.split('@')
text = [_ for _ in text if 'Lme' not in _]
text.append('000')

with open(f'txt/{file_name}_splitted.txt', 'w') as f:
    for block in text:
        f.write(block)

cleaned_text = []
for index in range(len(text) - 2):
    if text[index] is not None and not text[index].replace(' ', '').strip()[0].isdigit():
        new_block = text[index] + text[index + 1]
        cleaned_text.append(new_block)
        continue

data = []
for block in cleaned_text:
    data_dict = {"title": None, "values": []}
    block = block.split('\n')
    for line in block:
        if line != '' and line is not None and not line.startswith('Livello marino') and not line.startswith('Valori orari'):
            if not line[0].isdigit() and data_dict is not None:
                data_dict['title'] = [_.replace('\x0c', '') for _ in line.split(' ') if _ != ' ' and _ != '']
            if line[0].isdigit():
                line = line.replace('- -', '-- ')
                line = [_ for _ in line.split(' ') if _ != '' and _ != None]
                hour = line[0]
                for day, value in enumerate(line[1:]):
                    day = str(day + 1).zfill(2)
                    data_dict['values'].append((hour, day, value))
    data.append(data_dict)

months = ['GENNAIO', 'FEBBRAIO', 'MARZO', 'APRILE', 'MAGGIO', 'GIUGNO', 'LUGLIO', 'AGOSTO', 'SETTEMBRE', 'OTTOBRE', 'NOVEMBRE', 'DICEMBRE']

for dictionary in data:
    to_csv = []
    if len(dictionary['title']) == 4:
        title = [dictionary['title'][0] + '_' + dictionary['title'][1], dictionary['title'][2], dictionary['title'][3]]
        # to_csv_sub.append(title)
    elif len(dictionary['title']) == 3:
        title = [dictionary['title'][0], dictionary['title'][1], dictionary['title'][2]]
        # to_csv_sub.append([title[0], title[1]])
    values = dictionary['values']
    values = sorted(values, key= lambda x: x[1])
    for value_tup in values:
        year = title[2]
        month = str(months.index(title[1]) + 1).zfill(2)
        iso_date = year + '-'+ month + '-' + value_tup[1] + 'T' + value_tup[0] + ':00:00Z'
        to_csv.append([iso_date, value_tup[2]])  
    with open(f'output/{year}/{title[0]}_{year}.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        for line in to_csv:
            writer.writerow(line)