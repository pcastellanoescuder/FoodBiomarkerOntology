library(tidyverse)
library(classyfireR)

new_met <- readxl::read_excel("update ontology.xlsx")

# new_met <- new_met %>%
#   filter(is.na(FOBI)) %>%
#   filter(!is.na(`INCHI KEY`)) %>%
#   filter(!is.na(food)) %>%
#   select(metabolite, food) %>%
#   separate_rows(food, sep = ",", convert = FALSE) %>%
#   mutate(food = str_trim(food),
#          food = str_replace_all(food, "Fruits", "plant fruit food product"),
#          food = str_replace_all(food, "Vegetables", "vegetable food product"),
#          food = str_replace_all(food, "Coffe", "coffee based beverage product"),
#          food = str_replace_all(food, "Tea", "tea based beverage product"),
#          food = str_replace_all(food, "Cacao", "cacao food product"),
#          food = str_replace_all(food, "Whole_Grain_Cereals", "Whole grain cereal products"),
#          food = str_replace_all(food, "Legumes", "legume food product"),
#          food = str_replace_all(food, "Nuts", "nut (whole or part)"),
#          food = str_replace_all(food, "red_wine", "red wine"),
#          food = str_replace_all(food, "olive_oil", "olive oil"),
#          food = str_replace_all(food, "apple", "apple (whole)"),
#          food = str_replace_all(food, "Banana", "banana (whole, ripe)"),
#          food = str_replace_all(food, "Berries", "berry (whole, raw)"),
#          food = str_replace_all(food, "Whole_Grain_Oat", "whole oats (raw)"),
#          food = str_replace_all(food, "producte", "product"))
  
# classification_result <- list()
# 
# for(i in 1:nrow(new_met)){
#   
#   classification_result[[i]] <- get_classification(new_met$`INCHI KEY`[i])
#   
# }
  

# xlsx::write.xlsx(new_met, "files/relations.xlsx")

new_met <- new_met %>%
  filter(is.na(FOBI)) %>%
  filter(!is.na(`INCHI KEY`))

library(ontologyIndex)

path <- "../ontology/fobi.obo"

ontology <- get_ontology(path, extract_tags = "everything")
mynames <- data.frame(metabolite = ontology$name)
mynames$FOBI <- gsub("_", ":", rownames(mynames))

final <- merge(mynames, new_met, by = "metabolite")

xlsx::write.xlsx(final[,1:2], "files/FOBI.xlsx")

