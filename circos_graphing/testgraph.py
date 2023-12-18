from pycirclize import Circos
import pandas as pd

# Read the CSV file into a pandas DataFrame
file_path = 'Mouse3circostest.csv'
data = pd.read_csv(file_path, index_col=0)  # Assuming the first column contains row names/index

# Display the content of the DataFrame (optional)
#print(data)

links = []

# Iterate through the DataFrame to extract link data
for row_index, row in data.iterrows():
    for col_index, value in row.items():
        links.append([row_index, col_index, value])  # Assuming row_index and col_index are entity names

# Display the content of links (optional)
#print(links)

# Read the CSV file into a pandas DataFrame
data = pd.read_csv(file_path)

# Extract unique column names
unique_column_names = data.columns.tolist()
print("Unique Column Names:")
print(unique_column_names)

data = data.astype(int)

# Initialize from matrix (Can also directly load tsv matrix file)
circos = Circos.initialize_from_matrix(
    data,
    space=3,
    r_lim=(93, 100),
    cmap="tab10",
    ticks_interval=500,
    label_kws=dict(r=94, size=12, color="white"),
)

print(matrix_df)
fig = circos.plotfig()
plt.show()












