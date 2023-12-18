import pandas as pd
from circlize import CircosPlot
import matplotlib.pyplot as plt

# Read the CSV file into a pandas DataFrame with row and column names
file_path = 'your_data.csv'
data = pd.read_csv(file_path, index_col=0)  # Assuming first column contains row names

# Display the content of the DataFrame (optional)
print(data)

# Create a CircosPlot object with the data
fig, ax = plt.subplots(figsize=(8, 8))
circular_plot = CircosPlot(ax=ax)
circular_plot.plot(data.values)

# Adding labels to the Circos plot
circular_plot.set_labels(data.index)  # Set row names as labels

# Show the Circos plot
plt.title('Circos Plot of Matrix with Row and Column Names')
plt.show()
