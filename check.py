import os 

year = '2009'
for file_name in os.listdir(f'./output/{year}/'):
    if file_name.endswith('.csv'):
        with open(f'./output/{year}/{file_name}') as f:
            count = 0
            for line in f.readlines():
                count += 1
            print(file_name, 'len:', count)