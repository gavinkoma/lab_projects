path="/Users/gavinkoma/Documents/lab_projects/pain_project/iter0/cpperfect.h5"

# Install rhdf5 if not already installed
# BiocManager::install("rhdf5")

library(rhdf5)

# Load the HDF5 file
h5_file <- path
h5_data <- h5ls(h5_file)  # View the structure

# Function to read a single element
read_element <- function(group_name) {
  list(
    id = h5read(h5_file, paste0(group_name, "/id")),
    strain = as.factor(h5read(h5_file, paste0(group_name, "/strain"))),
    stimulus = as.factor(h5read(h5_file, paste0(group_name, "/stimulus"))),
    time.series = h5read(h5_file, paste0(group_name, "/time_series"))
  )
}

# Read all elements into an R list
element_names <- unique(h5_data$group[h5_data$group != "/"])
nested_list_r <- lapply(element_names, read_element)

str(nested_list_r)  # Examine the structure

# try it in paws...
library(pawscore)
wimmer.tracks <- nested_list_r
wimmer.tracks <- lapply(element_names, read_element)
# adjust some parameters for our rat data:
params <- set_parameters(window.threshold=1,shake.filter.threshold = 1)
paw.features <- lapply(wimmer.tracks, function(track) {
  extract_features(track$time.series, parameters = params, diagnostics=TRUE)
})

# get strain information for each track
strains <- sapply(wimmer.tracks, function(track) track$strain)

# compute pain scores - needs more info...
#scores <- pain_score(paw.features, strains=strains)

# Let's just look at the first one:
paw1 <- wimmer.tracks[[1]]$time.series
ft <- extract_features(paw1,diagnostics=TRUE)
plot(ft)
# yah it doesn't know the end is garbage...
plot(ft, clipped = TRUE)
#> .libPaths()
# [1] "/Library/Frameworks/R.framework/Versions/4.2-arm64/Resources/library"

# Wow great! Now let's plot them all!
# Create a PDF device to capture all plots
pdf("wimmertracks_sf1.pdf", width = 8, height = 6)  # Adjust size as needed
# Iterate over your big list and generate plots for each element
for (i in seq_along(wimmer.tracks)) {
  # Call your custom plot function
  plot(paw.features[[i]])
  
  # Add an overall title using the "video" field from the current list element
  video_title <- wimmer.tracks[[i]][["id"]]
  title(main = video_title, outer = TRUE, line = -2, cex.main = 1.5)  # Outer title
}

# Close the PDF device to save the file
dev.off()