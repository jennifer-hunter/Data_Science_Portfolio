### Suggested running order to follow the flow of analysis

1. **Three datasets were downloaded from the internet for evaluation**
   - kpis/data/Monthly_and_Quarterly_Visits_to_DCMS-Sponsored_Museums_and_Galleries_-_to_June_2025_data_tables.ods
   - collections/data/tate_modern_temporary_exhibitions_2008to2016_public.xlsx
   - collections/data/british_museum_dataset_raw.csv
     
2. **A further dataset was obtained via api and this can be seen in detail**
   - collections/api/va_api_process_README_nicky.md
   - collections/api/va_sculpture_download_nicky.py
   - this dataset is saved here: collections/data/victoria_albert_museum_dataset_raw.csv
     
3. **Quick first look to confirm that the collections data from British Museum (bm) and Victoria and Albert Museum (va) were required**
   - collections/notebooks/tate_footfall_dataset_first_look_jo.ipynb
     
4. **Cleaning of the British Museum dataset**
   - collections/notebooks/bm_date_cleaning_nicky.ipynb
   - collections/notebooks/bm_production_place_cleaning_nicky.ipynb
   - collections/notebooks/bm_technique_materials_cleaning_nicky.ipynb
   - this was looked at briefly by Nicky but continued later by Angie using the combined_collection_dataset
     
5. **Cleaning of the Victoria and Albert Museum dataset**
   - collections/notebooks/va_date_cleaning_diana.ipynb
   - collections/notebooks/va_production_place_cleaning_diana.ipynb
     
6. **Combining the two datasets (bm and va)**
   - collections/notebooks/combined_collections_dataset.ipynb
     
7. **Visualisation of combined collection item records**
   - collections/notebooks/collections_heatmap_experiment_nicky.ipynb
   - collections/notebooks/collections_choropleth_vis_nicky.ipynb
   - collections/notebooks/materials_and_techniques_angie.ipynb
     
8. **Revisit to Tate temporary exhibitions to explore importance of sculpture as a medium**
   - collections/notebooks/tate_temp_exhibitions_jo.ipynb
   
9. **Continued exploration of the combined dataset**
   - collections/notebooks/combined_collections_exploratory_analysis_jo.ipynb
   
10. **Machine Learning**
    - machine_learning/notebooks/footfall_cleansed_ml_jennifer.ipynb
    - machine_learning/notebooks/footfall_machine_learning_jennifer.ipynb
    
11. **KPIs**
    - kpis/notebooks/footfall_cleansing_jennifer_jenny.ipynb
    - kpis/notebooks/tate_exhibitions_with_footfall_collections_jo.ipynb
    - kpis/notebooks/museum_kpis_dataset_cleaning_nicky.ipynb
    - kpis/notebooks/kpi_visualisation_stacked_bar_nicky.ipynb
