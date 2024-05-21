

#### Livability and Population Correlation Analysis

### Introduction

This  aims to determine whether there is a correlation between the livability percentage and the population of Melbourne. By analyzing data from 2011 to 2021, we investigate the relationship between these two variables. The analysis utilizes the Regional Population Dataset and the Livability Index Dataset to provide insights into how population changes might impact the overall livability of Melbourne.

### Data Sources

# Regional Population Dataset
Description: Contains population-related information in Victoria, including births, deaths, and migration.
Key Feature: erp_YYYY columns representing the estimated regional population for Melbourne from 2011 to 2021.
# Livability Index Dataset
Description: Provides metrics related to the livability of Melbourne, focusing on topics such as economy, finance, governance, housing, and transportation.
Key Feature: Percentages that reflect different aspects of livability over the years.
### Data Processing

## Regional Population Data
# Data Retrieval: 
Extracted from Elasticsearch using the index abs-regional_population_lga_2001-2021.
# Data Cleaning:
Removed spacing from column names.
Extracted key columns for the years 2011 to 2021.
Selected and cleaned the row corresponding to Melbourne.
## Livability Index Data
# Data Retrieval: Extracted from Elasticsearch using the index liveability-index.
D#ata Cleaning:
Filtered for rows where type is 'Liveability' and value_type is 'Percentage'.
Extracted the year from the period column.
Replaced 'N/A' values and removed rows with NaN values.
Grouped by year and calculated overall percentages.
## Merging Datasets
The cleaned datasets were merged on the year column to facilitate the correlation analysis.

### Analysis  and Visualization

Correlation Calculation
A correlation matrix was calculated to determine the relationship between the livability percentage and population.

An interactive heatmap was created using Plotly to visualize the correlation between the two variables.

### Results

The correlation analysis reveals a weak negative correlation (-0.15) between the livability percentage and population in Melbourne over the period from 2011 to 2018. This suggests that as the population increases, the livability percentage slightly decreases, but the relationship is not significant.
