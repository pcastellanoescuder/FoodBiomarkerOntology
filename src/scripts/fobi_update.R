library(tidyverse)
library(classyfireR)

new_met <- readxl::read_excel("update ontology.xlsx")

new_met <- new_met %>%
  filter(is.na(FOBI)) %>%
  filter(!is.na(`INCHI KEY`))

classification_result <- list()

for(i in 1:nrow(new_met)){
  
  classification_result[[i]] <- get_classification(new_met$`INCHI KEY`[i])
  
}
  
  
  
  

# xlsx::write.xlsx(new_met, "files/relations.xlsx")




