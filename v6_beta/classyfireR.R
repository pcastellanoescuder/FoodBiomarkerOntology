library(classyfireR)
library(tidyverse)

data <- vroom::vroom("/home/pol/Escritorio/FBOnto/FBOnto_paper/Annotation/Annotation_file.csv" , delim = ",")
  
keys <- data$InChIKey[!is.na(data$InChIKey)]

classification_list <- map(keys, get_classification)

names(classification_list) <- keys

classification_list[sapply(classification_list, is.null)] <- NULL

classification_tibble <-
  map2(classification_list, names(classification_list), ~ {
    add_column(.x, ID = rep(.y))
  }) %>% bind_rows()

###

classification_list <- map(classification_list, ~{select(.,-CHEMONT)})

spread_tibble <- purrr:::map(classification_list, ~{
  spread(., Level, Classification)  
}) %>% bind_rows() %>% data.frame()

rownames(spread_tibble) <- names(classification_list)

classification_tibble <-  tibble(
  InChIKey = rownames(spread_tibble),
  Kingdom = spread_tibble$kingdom,
  SuperClass = spread_tibble$superclass,
  Class = spread_tibble$class,
  SubClass = spread_tibble$subclass,
  Level5 = spread_tibble$level.5,
  Level6 = spread_tibble$level.6,
  Level7 = spread_tibble$level.7
)


#write_excel_csv(classification_tibble, "FBOnto_classification_tibble.csv")

###############

anot <- read_csv("/home/pol/Escritorio/FBOnto/FBOnto_paper/Annotation/Annotation_file.csv")

results <- merge(anot, classification_tibble, by = "InChIKey")

results <- results[, c(2,11:ncol(results))]

## 

results7 <- results[!is.na(results$Level7) ,]
write.csv(results7, "results7.csv")

results6 <- results[!is.na(results$Level6) & is.na(results$Level7) ,]
write.csv(results6, "results6.csv")

results5 <- results[!is.na(results$Level5) & is.na(results$Level6) & is.na(results$Level7) ,]
write.csv(results5, "results5.csv")

results4 <- results[!is.na(results$SubClass) & is.na(results$Level5) & is.na(results$Level6) & is.na(results$Level7) ,]
write.csv(results4, "results4.csv")

results3 <- results[!is.na(results$Class) & is.na(results$SubClass) & is.na(results$Level5) & is.na(results$Level6) & is.na(results$Level7) ,]
write.csv(results3, "results3.csv")




nrow(results5[results5$MetaboliteName %in% results6$MetaboliteName ,])


















