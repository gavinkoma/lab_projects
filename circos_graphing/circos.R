library(circlize)
data = read.csv('Mouse3circostest.csv')
new_row_names = data$X

new_data <- data.frame(data[, -1])  # Exclude the 'NewRowNames' column from the new dataframe
rownames(new_data) <- new_row_names  # Set 'NewRowNames' as row names

# Create a chord diagram with the matrix data
chordDiagram(new_data, transparency = 0.5)


# Load the circlize library
data = read.csv('unsure.csv')
new_row_names = data$X

new_data <- data.frame(data[, -1])  # Exclude the 'NewRowNames' column from the new dataframe
rownames(new_data) <- new_row_names  # Set 'NewRowNames' as row names

library(circlize)

# Assuming 'data' contains your 25x25 matrix data

# Create a chord diagram with the matrix data
chordDiagram(data, transparency = 0.5)

# Get row and column names
rownames <- rownames(data)
colnames <- colnames(data)

# Define track heights for row and column names
track_height <- 0.5

# Add row names as labels on the outer track
circos.text(rep(1 + track_height * 0.5, length(rownames)), 
            seq_along(rownames), labels = rownames,
            facing = "inside", niceFacing = TRUE, 
            col = "black", cex = 0.5, 
            font = 2, 
            adj = c(0, 0))

# Add column names as labels on the inner track
circos.text(seq_along(colnames), 
            rep(1 + track_height * 0.5, length(colnames)), 
            labels = colnames,
            facing = "clockwise", niceFacing = TRUE, 
            col = "black", cex = 0.5, 
            font = 2, 
            adj = c(0, 0))

