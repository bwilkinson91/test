# First, import the packages needed to conduct the analysis.

```{r}
library(rvest)
library(lubridate)
library(dplyr)
library(stringr)
library(purrr)
library(ggplot2)
```


# Next, using the 'rvest' package, import the HTML script from my profile on 'DreamTeam.gg.' 

```{r}
apex_page <- 'https://dreamteam.gg/apex/profile-matches/ps4/b_dubya91'
apex <- read_html(apex_page)
```


Extract the text from specific nodes in the HTML script that contain the time at which each match took place.  

```{r}
time <- apex %>%
  html_node('div') %>%
  xml_find_all("//p[contains(@class, 'base___2IHZA general___33ZOl s___3mnzq s-mobile___3i3cb left___1AJ7s semibold___1ArSI l_l___1BRm- l_l-mobile___3p5vc')]") %>%
  html_text()
```


Convert the extracted data into a tbl, remove any extraneous observations, convert the remaining observations into strings and replace the commas.

```{r}
time_df <- data.frame(time)
time_df <- as_tibble(time_df)  %>%
  filter(time != '', time != 'Kills', time != 'Damage', time != 'Headshots') %>%
  mutate(time = as.character(time)) %>%
  mutate(time = str_replace(time, ',', ''))
```


Follow a similar process to obtain data regarding the legend used for each match.

```{r}
legend <- apex %>%
  html_node('div') %>%
  xml_find_all("//div[contains(@class, 'box___jUrgl')]") %>%
  html_children() %>%
  xml_attr('src')

legend_df <- data.frame(legend)
legend_df <- as_tibble(legend_df) %>%
  mutate(legend = as.character(legend)) %>%
  drop_na()
```


Extract the text from specific nodes in the HTML script that contain various measures of performance for each match.

```{r}
stats <- apex %>%
  html_node('div') %>%
  xml_find_all("//p[contains(@class, 'base___2IHZA general___33ZOl m___1GMQu m-mobile___1ifKn left___1AJ7s bold___1xn02 ellipsis___2YNw_ l_m___3SqLU l_m-mobile___2QlVQ')]") %>%
  html_text()
```


To obtain data regarding the number of eliminations, keep every third observation in the character vector, 'stats.'

```{r}
elims_df <- data.frame(stats)
elims_df <- as_tibble(elims_df) %>%
  slice(seq(1, n(), by = 3)) %>%
  rename(elims = stats) %>%
  mutate(elims = as.character(elims)) %>%
  mutate(elims = as.integer(elims))
```


Replace the missing values for the number of eliminations per match with the median value of all matches.

```{r}
elims_df <- elims_df %>%
  mutate(elims = replace_na(elims, median(elims, na.rm = TRUE)))
```


Follow a similar process to create separate tbl's for the amount of damage inflicted and the number of headshots per match.

```{r}
damage_df <- data.frame(stats)
damage_df <- as_tibble(damage_df) %>%
  slice(seq(2, n(), by = 3)) %>%
  rename(damage = stats) %>%
  mutate(damage = as.character(damage)) %>%
  mutate(damage = as.integer(damage))

damage_df <- damage_df %>%
  mutate(damage = replace_na(damage, median(damage, na.rm = TRUE)))

headshots_df <- data.frame(stats)
headshots_df <- as_tibble(headshots_df) %>%
  slice(seq(3, n(), by = 3)) %>%
  rename(headshots = stats) %>%
  mutate(headshots = as.character(headshots)) %>%
  mutate(headshots = as.integer(headshots))

headshots_df <- headshots_df %>%
  mutate(headshots = replace_na(headshots, median(headshots, na.rm = TRUE)))
```


Combine the tbl's for time, legend, eliminations, damage and headshots into a single tbl.

```{r}
matches <- cbind(time_df, legend_df, elims_df, damage_df, headshots_df)
```


Convert the 'time' variable into a date-time object and adjust the observations to be reflective of the actual time.

```{r}
matches$time <- parse_date_time(matches$time, order = 'HM_db')

matches$time <- matches$time - hours(5)
```


Calculate the duration of each match by subtracting the starting time of one match by the starting time of the preceding match.

```{r}
matches <- matches %>%
  mutate(day = day(time), minutes = minute(time)) %>%
  group_by(day) %>%
  mutate(duration = abs(minutes - lag(minutes, default = first(minutes)))) %>%
  ungroup() %>%
  select(-c(day, minutes))
```


Replace impossible values of the 'duration' variable with the mean of average value.

```{r}
matches <- matches %>%
  mutate(duration_fix = ifelse(duration > 25, round(mean(duration, na.rm = TRUE), 0),
                               ifelse(duration == 0, round(mean(duration, na.rm = TRUE), 0), duration)))

```


Create a new variable that indicates whether each match took place in the 'morning' or 'evening.'

```{r}
matches <- matches %>%
    mutate(time_of_day = ifelse(hour(time) < 18, 'morning', 'evening'))
```


Replace the hyperlinks saved in the 'legend' variable with the actual name of each character.

```{r}
legend_list <- c('caustic', 'pathfinder', 'bloodhound', 'bangalore', 'wraith', 'gibraltar', 'mirage',
                 'lifeline', 'octane', 'wattson')

for (x in legend_list) {
  matches$legend[grep(x, matches$legend)] <- x
  
}
```


Create a tbl that contains relevant summary statistics for each legend.

```{r}
legend_stats <- matches %>%
  group_by(legend) %>%
  summarize(avg_elims = mean(elims, na.rm = TRUE), avg_damage = mean(damage, na.rm = TRUE),
  avg_headshots = mean(headshots, na.rm = TRUE) , avg_duration = mean(duration, na.rm = TRUE),
  n = n())
```


Write a function that produces a bar chart for each summary statistic across all legends.

```{r}
create_bar = function (x, y) {
  ggplot(data = legend_stats) +
    aes_string(x = x, y = y) +
    geom_bar(stat = 'identity')
}

x_var <- names(legend_stats)[2]
y_var <- names(legend_stats)[3:6]

bars <- map2(x_var, y_var, create_bar)
```





