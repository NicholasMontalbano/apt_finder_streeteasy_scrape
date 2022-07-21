# Create table for webpage

library(tidyverse)
library(reactablefmtr)
library(reactable)
library(htmlwidgets)
library(webshot)
library(crosstalk)

apt_metrics <- read_csv('data/apt_metrics.csv')

data <- apt_metrics %>%
  mutate(price = as.numeric(gsub("\\$||,", "", price)), 
         arrests_pc = round(arrests_pc * 1000, 1), 
         f_acre_pc = round(f_acre_pc * 1000, 1)) %>%
  select(!c(geo, work_directions, friend_directions, GEO_ID, f_acre_sum_uncap, f_acre_sum, population, med_income, arrests)) %>%
  unique() %>%
  rename(
    park_acres = f_acre_pc,
    Borough = BoroName,
    arrests = arrests_pc, 
    place = neighborhood
  )

write_csv(data, file = 'data/table_data.csv')

### create shared dataset for crosstalk
crosstalk_data <- SharedData$new(data)

### crosstalk team filter
team_filter <- filter_select(
  id = "type",
  label = "TYPE",
  sharedData = crosstalk_data,
  group = ~ type
)

place_filter <- filter_select(
  id = "placee",
  label = "PLACE",
  sharedData = crosstalk_data,
  group = ~ place
)
  

table <- reactable(
  crosstalk_data,
  defaultColDef = colDef(
    cell = data_bars(data, text_position = "outside-base")
  ), 
  theme = nytimes(), 
  pagination = FALSE
)

filter_table <- bscols(
  widths = c(2, NA),
  list(team_filter, place_filter),
  table)

#htmlwidgets::saveWidget(table, file = 'visuals/table.html')
htmltools::save_html(filter_table, file = 'visuals/filter_table.html')

