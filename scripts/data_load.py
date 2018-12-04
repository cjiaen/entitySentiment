
import os
import glob
import pandas as pd

RAW_DATA_PATH = r"C:\Users\calvintan\Documents\Projects\SPS\SPS Advanced Analytics Platform\demo\data"

df = pd.DataFrame(index=range(75000), columns=['content','sentiment'])
row_count = 0
for folder in os.listdir(RAW_DATA_PATH):
    updated_path = os.path.join(RAW_DATA_PATH, folder)
    for txt_file in glob.iglob(updated_path + r'\*.txt'):
        with open(os.path.join(updated_path, txt_file),'r',encoding='utf-8') as f:
            df.iloc[row_count,0] = f.read()
            df.iloc[row_count,1] = folder
            row_count = row_count + 1
        if row_count%1000 == 0: print("Completed {} files".format(row_count))
df.to_csv("sentiment_data.csv", index = False)

#load df
df = pd.read_csv("sentiment_data.csv")