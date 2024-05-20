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
