library(tidyverse)
library(data.table)

fobi <- readr::read_csv("fobi-merged.csv")
fobi <- fobi[!(is.na(fobi$`http://purl.obolibrary.org/obo/FOBI_00422`)) ,]

fobi <- fobi[, c(4, 21)]
colnames(fobi) <- c("food", "label")

fobi <- data.table(fobi)

dt_out <- fobi[, list(metabolite = label,
                      food = unlist(strsplit(food, '\t'))), 
               by = 1:nrow(fobi)]
dt_out$nrow <- NULL
dt_out$metabolite <- gsub("'", '', dt_out$metabolite)

# write.csv(dt_out, "191202_fobi_relations", row.names = F)
