from tabula import convert_into, read_pdf
import PyPDF2 # uninstall
import os
import csv
import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer

def tabula_pdf_to_csv(input_folder=os.getcwd(), output_folder=os.getcwd()):
    for file_name in os.listdir(input_folder):
        # generate csv with read data (tabula)
        if file_name.endswith('.pdf'):
            base_name = file_name.replace('.pdf', '')
            convert_into(f'./pdf-data/{file_name}', f'./temp/{base_name}.csv', output_format='csv', pages='all') # pages='all'
        # get titles separately using PyPDF2
        with open(f'./pdf-data/{file_name}', 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            titles = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                text = text.split('\n')
                for index, line in enumerate(text):
                    if index + 2 <= len(text):
                        if not text[index][0].isdigit() and text[index + 1][:7] == 'Livello' and text[index][0] != '-':
                            title_list = [_ for _ in text[index].split(' ') if _ != '']
                            val_id = text[index + 4].replace(' ', '')[2:32]
                            titles.append({"title": title_list, "val_id": val_id})
        # clean and update data with titles
        with open(f'temp/{base_name}.csv') as csv_file:
            lines = csv_file.readlines()
            table = []
            title = '------'  # title placeholder
            for line in lines:
                if line[:3] == '01,':
                    table.append([title])
                    table.append(['hh\dd','01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'])
                for i in range(0,25):
                    i = str(i).zfill(2) + ','
                    if line[:3] == i:
                        line = line.replace('\n', '').replace(',', ' ')
                        line = line.split(' ')
                        line = [_ for _ in line if _ != '']
                        table.append(line)
            for i, line in enumerate(table):
                for title_val in titles:
                    if ''.join(line)[2:32] == title_val['val_id']:
                        table[i - 2] = title_val['title']
        # generate output as csv file from table
        with open(f'{output_folder}_old/{base_name}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(table)
    print('Done')

months = ['GENNAIO', 'FEBBRAIO', 'MARZO', 'APRILE', 'MAGGIO', 'GIUGNO', 'LUGLIO', 'AGOSTO', 'SETTEMBRE', 'OTTOBRE', 'NOVEMBRE', 'DICEMBRE']

def pdfreader_pdf_to_csv(input_folder=os.getcwd(), output_folder=os.getcwd()):
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.pdf'):
            fd = open(f'./pdf-data/{file_name}', "rb")
            viewer = SimplePDFViewer(fd)
            data = []
            for canvas in viewer:
                page_strings = canvas.strings
                joined = ''.join(page_strings)
                page_strings = joined.split('Livello (mm)-Pressione')[0]
                title = page_strings.split('Valori orari')[0].split(' ')
                title = [_.strip() for _ in title if _ != ' ' and _ != ''][:3]
                if title[0] == 'Reggio':
                    title[0] = 'Reggio_Calabria'
                    title.pop(1)
                    title.append(''.join([_ for _ in file_name if _.isdigit()]))
                if title[0] == 'Porto':
                    title[0] = 'Porto_Empedocle'
                    title.pop(1)
                    title.append(''.join([_ for _ in file_name if _.isdigit()]))
                page_strings = page_strings.split('Valori orari')[1]
                page_strings = page_strings.split('3101')[1]
                result = []
                for char in page_strings:
                    if char == '-':
                        result.extend([' ', char])
                    else:
                        result.append(char)
                page_strings = ''.join(result)
                numbers = page_strings.split()
                grouped_numbers = [numbers[i:i+31] for i in range(0, len(numbers), 31)]
                for group in grouped_numbers[:-1]:
                    group[-1] = group[-1][:-2]
                # grouped_numbers = list(map(list, zip(*grouped_numbers)))
                data.append({"title": title, "values": grouped_numbers})
            year = ''.join([_ for _ in file_name if _.isdigit()])

            for dictionary in data:
                values = dictionary['values']
                month = months.index(dictionary["title"][1]) + 1
                # n = 24
                # fill = [None] * n
                # values = [sublist[:n] + fill[len(sublist):] for sublist in values]
                result = []
                day = 1
                for i in range(len(values[0])):
                    try:
                        hour = 1
                        for j in range(len(values)):
                            try:
                                value = values[j][i]   
                                line = [f'{year}/{month}/{day} {hour}', value]
                                result.append(line)
                                hour += 1
                            except Exception as e:
                                print(f'{dictionary["title"][1].lower()}:', e)
                                continue
                        day += 1
                    except Exception as e:
                        print(f'{dictionary["title"][1].lower()}:', e)
                        continue
                with open(f'{output_folder}/{dictionary["title"][0]}_{dictionary["title"][2]}_{dictionary["title"][1].lower()}.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(result)

if __name__ == '__main__':
    # tabula_pdf_to_csv(input_folder='pdf-data', output_folder='output)
    pdfreader_pdf_to_csv(input_folder='test', output_folder='output')
