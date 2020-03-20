library(tidyverse)
library(data.table)

fobi <- readr::read_csv2("200320_fobi-export.csv")

fobi <- fobi[!is.na(fobi$BiomarkerOf), ]

fobi <- data.table(fobi)

dt_out <- fobi[, list(metabolite = Entity,
                      food = unlist(strsplit(BiomarkerOf, '\t'))), 
               by = 1:nrow(fobi)]
dt_out$nrow <- NULL
dt_out$metabolite <- gsub("'", '', dt_out$metabolite)
dt_out$food <- gsub("'", "", dt_out$food, fixed = T)

# write.csv(dt_out, "200320_fobi_relations.csv", row.names = F)
