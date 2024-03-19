library(circlize)
library(readxl)
library(tibble)

#file_path <- '/Users/gavinkoma/Documents/lab_projects/circos_graphing/Mouse3circostest.xlsx'
#data <- read_excel(file_path,col_names = TRUE)
#str(data)
#head(data)

data = read.csv('unsure.csv')

# Set the values in the "..1" column as row names
row <- data$X
row.names(data) <- data$X
data <- data[,-1]

chordDiagram(data)

#okay so i think we need to make three graphs that show the data
#pos:neg
#pos:p
#p:neg

