library(tidyverse)

fobi <- readr::read_csv2("fobi.csv")

fobi <- fobi %>% 
  select(-Type, -X12, -`rdfs:label`) %>% 
  filter(!is.na(`Superclass(es)`)) %>% 
  map_dfc(function(x){gsub("'", '', x)}) %>%
  filter(!is.na(InChIKey))

# xlsx::write.xlsx(fobi, "fobi_metabolites.xlsx")
# write.csv(fobi, "fobi_metabolites.csv", row.names = F)