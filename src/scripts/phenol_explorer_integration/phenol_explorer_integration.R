
library(tidyverse)
library(classyfireR)

composition <- readxl::read_xlsx("data/composition-data.xlsx") %>%
  rownames_to_column()

# number of compounds in Phenol-Explorer
# length(unique(composition$compound))

foods_fobitools <- fobitools::annotate_foods(foods = composition[, c(1,4)])

annotated_foods <- foods_fobitools$annotated %>%
  dplyr::rename(food = FOOD_NAME)

composition_fobi <- composition %>%
  right_join(annotated_foods, by = "food") %>%
  select(FOBI_ID, FOBI_NAME, food, compound_group, 
         compound_sub_group, compound, publication_ids, pubmed_ids)

##

compounds <- readxl::read_xls("data/compounds.xls") %>%
  select(Name, `ChEBI ID`, `PubChem ID`) %>%
  dplyr::rename(compound = Name)

composition_fobi <- composition_fobi %>%
  left_join(compounds, by = "compound") %>%
  mutate(compound = tolower(compound))

##

metabolites_fobi <- fobitools::parse_fobi(terms = "FOBI:01501", get = "des") %>%
  select(1:4) %>%
  mutate(compound = tolower(name))

# metabolites_fobi$compound[metabolites_fobi$compound %in% composition_fobi$compound]
# unique(composition_fobi$compound[composition_fobi$compound %in% metabolites_fobi$compound])

composition_fobi <- composition_fobi %>%
  left_join(metabolites_fobi, by = "compound") %>%
  filter(!duplicated(.))

# paste result at "http://cts.fiehnlab.ucdavis.edu/batch"
composition_fobi %>%
  filter(is.na(name)) %>%
  filter(!duplicated(compound)) %>%
  pull(compound) %>%
  str_to_title() %>%
  cat(sep = "\n")

####

annotations_1 <- readr::read_csv("data/cts-20210714170715.csv") %>%
  na_if("No result") %>% 
  na_if("undefined")

annotations_2 <- readr::read_csv("data/cts-20210714172629.csv") %>%
  na_if("No result") %>% 
  na_if("undefined")

annotations <- left_join(annotations_1, annotations_2, by = "Chemical Name") %>%
  select(-Score)

####

annotations_nona <- annotations %>%
  filter(!is.na(InChIKey))

# df <- purrr::map(annotations_nona$InChIKey, get_classification)

# save(df, file = "data/classyfireR.rda")
load("data/classyfireR.rda")

####

df_class <- purrr::map(df, classification) %>%
  set_names(annotations_nona$InChIKey) %>%
  enframe() %>%
  unnest(cols = c(value)) %>%
  filter(Classification != "Organic compounds")

out_fobi <- unique(df_class$Classification[!df_class$Classification %in% metabolites_fobi$name])

ls_class <- list()

for (i in 1:nrow(df_class)) {
  if(df_class$Classification[i] %in% out_fobi){
    ls_class[[i]] <- data.frame(parent = df_class$Classification[i-1], child = df_class$Classification[i])
  }
}

fobi_new_classes <- bind_rows(ls_class) %>%
  filter(!duplicated(.))

# openxlsx::write.xlsx(fobi_new_classes, "data/fobi_new_classes.xlsx")

####

annotations <- annotations_nona %>%
  rename(compound = 1) %>%
  mutate(compound = tolower(compound))

composition_fobi_anno <- composition_fobi %>%
  left_join(annotations, by = "compound") %>%
  mutate(ChEBI = ifelse(is.na(ChEBI), paste0("CHEBI:", `ChEBI ID`), ChEBI)) %>%
  na_if("CHEBI:NA")

####

metabolites_fobi_2 <- fobitools::parse_fobi(terms = "FOBI:01501", get = "des") %>%
  select(name) %>%
  mutate(compound = tolower(name))

composition_fobi_anno <- composition_fobi_anno %>%
  left_join(metabolites_fobi_2, by = "compound") %>%
  filter(!duplicated(.)) %>%
  dplyr::rename(original_name = name.y)

#### relations to include (metabolites already present in FOBI)

relations_fobi <- composition_fobi_anno %>%
  filter(!is.na(original_name)) %>%
  select(FOBI_NAME, publication_ids, pubmed_ids, `PubChem ID`, original_name) %>%
  filter(!duplicated(.))

# openxlsx::write.xlsx(relations_fobi, "data/relations_fobi.xlsx", overwrite = TRUE)

#### relations to include (new FOBI metabolites)

relations_fobi_new <- composition_fobi_anno %>%
  filter(is.na(original_name)) %>%
  filter(!is.na(InChIKey)) %>%
  select(FOBI_NAME, compound, publication_ids, pubmed_ids, `PubChem ID`, ChEBI:ChemSpider) %>%
  filter(!duplicated(.))

# openxlsx::write.xlsx(relations_fobi_new, "data/relations_fobi_new.xlsx")

# new metabolites to add
relations_fobi_new %>%
  pull(compound) %>%
  unique() %>%
  # length() %>%
  cat(sep = "\n")

#### classification new metabolites

df_class2 <- df_class %>%
  dplyr::rename(InChIKey = name) %>%
  group_by(InChIKey) %>%
  dplyr::slice(n()) %>%
  filter(!duplicated(InChIKey))

class_new_metabolites <- relations_fobi_new %>%
  left_join(df_class2, by = "InChIKey") %>%
  select(compound, Classification)

# openxlsx::write.xlsx(class_new_metabolites, "data/class_new_metabolites.xlsx")

