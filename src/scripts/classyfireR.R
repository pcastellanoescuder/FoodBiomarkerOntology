library(classyfireR)

data <- readxl::read_excel("files/FOBI_new_metabolites.xlsx")

df <- list()

for(i in 1:nrow(data)){
  df[[i]] <- get_classification(data$INCHI[i])
  Sys.sleep(5)
}

# save(df, file = "84classyfied.RData")
