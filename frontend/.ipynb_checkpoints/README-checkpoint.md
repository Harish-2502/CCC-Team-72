## Rental Affordability and Population Correlation Analysis

## Overview

This analysis explores the relationship between the population of Melbourne and the rental affordability index over the years 2011 to 2021. Additionally, it examines the impact of the COVID-19 pandemic on the rental affordability index in Melbourne.

## Objectives

To analyze the trends in rental affordability from 2011 to 2021.
To examine the relationship between population growth and rental affordability.
To assess the impact of the COVID-19 pandemic on rental affordability in Melbourne.

## Dataset Description

The analysis utilizes two main datasets:

Regional Population Dataset: Contains information on the estimated regional population for Melbourne, including data from births, deaths, and migration.
Rental Affordability Index Dataset: Includes data on rental affordability for different postal codes in Melbourne over multiple quarters in each year from 2011 to 2021.



## Data Processing

# Regional Population Dataset
Connect to the Elasticsearch client and retrieve data from the index abs-regional_population_lga_2001-2021.
Extract relevant population data specifically for Melbourne from the retrieved data.
Clean the dataset by renaming columns and selecting key columns (erp_2011 to erp_2021) for analysis.
# Rental Affordability Index Dataset
Connect to the Elasticsearch client and retrieve data from the index rental_affordability.
Clean the dataset by removing spaces from column names and selecting columns relevant to rental affordability for each quarter from 2011 to 2021.
Calculate the average rental affordability index for each year by averaging the quarterly indices.
# Merging Datasets
Convert the year columns to numeric format for both datasets.
Merge the cleaned regional population dataset and rental affordability index dataset on the year column to create a consolidated dataset (analysis_df).

## Analysis

# Correlation Analysis
Calculate the correlation matrix for the rental affordability index and population using the consolidated dataset.
Visualize the correlation matrix using a heatmap to display the correlation coefficient between the variables.
# Correlation Method
The correlation between the rental affordability index and population is calculated using the Pearson correlation coefficient.

# Trend Analysis
Plot the trend of the rental affordability index over the years using a line graph.
Highlight the impact period of COVID-19 (2019-2021) and annotate the percentage increase in the rental affordability index during this period.
The plot shows a significant increase in the rental affordability index during the COVID-19 period (2019-2021). Specifically, there was a 44.63% increase from 2019 to 2021.

## Results

# Correlation Coefficient: 
The heatmap reveals a moderate positive correlation (0.662) between the rental affordability index and population.
# Impact of COVID-19: 
The rental affordability index increased significantly during the COVID-19 period, with a 44.63% increase from 2019 to 2021.





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
