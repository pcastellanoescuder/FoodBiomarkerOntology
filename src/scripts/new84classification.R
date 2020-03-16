library(tidyverse)
library(purrr)

new_chemicals <- readxl::read_excel("files/FOBI_new_metabolites.xlsx")
load("files/84classyfied.RData")

names(df) <- new_chemicals$metabolite

res <- map_df(df, ~as.data.frame(.x), .id = "id")
res <- res %>% group_by(id) %>% slice(n()) %>% ungroup()

# xlsx::write.xlsx(res, "files/new84chems.xlsx", row.names = T)

missclassified <- new_chemicals[!(new_chemicals$metabolite %in% res$id) ,]

# xlsx::write.xlsx(missclassified, "files/missclassified.xlsx", row.names = T)

#######################################################################################################################

new_hmdb <- new_chemicals[!is.na(new_chemicals$HMDB),]
new_kegg <- new_chemicals[!is.na(new_chemicals$KEGG),]

# xlsx::write.xlsx(new_hmdb, "files/new_hmdb.xlsx", row.names = T)
# xlsx::write.xlsx(new_kegg, "files/new_kegg.xlsx", row.names = T)
