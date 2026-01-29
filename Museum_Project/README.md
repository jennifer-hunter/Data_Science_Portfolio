> **Portfolio Note:** This was a group project completed using Agile methodology. My contributions included the footfall data cleaning and the machine learning components.

# 🎨 Museum Project: Collections and KPI Trends
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Jupyter Notebook](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)
![Pandas](https://img.shields.io/badge/pandas-Data%20Analysis-yellow.svg)
![NumPy](https://img.shields.io/badge/NumPy-Arrays-blue.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualisation-green.svg)
![Seaborn](https://img.shields.io/badge/Seaborn-Statistical%20Plots-teal.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange.svg)
![statsmodels](https://img.shields.io/badge/Statsmodels-Statistical%20Modelling-purple.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-Gradient%20Boosting-red.svg)
![Status](https://img.shields.io/badge/Status-Completed-green.svg)

---

## 📑 Table of Contents
1. [Project Overview](#project-overview)
2. [Research Questions](#research-questions)
3. [Datasets](#datasets)
4. [Repository Structure](#repository-structure)
5. [Project Workflow](#project-workflow)
6. [Methods Summary](#methods-summary)
7. [Results Summary](#results-summary)
8. [Setup & Requirements](#setup--requirements)
9. [How to Run the Project](#how-to-run-the-project)
10. [Project Timeline](#project-timeline)
11. [Contributors](#contributors)
    
---

<a id="project-overview"></a>
## 🧭 Project Overview
<details>
<summary><strong>Click to expand</strong></summary>

This project examines how museum collections and visitor behaviour intersect across the UK national museum sector. Using sculpture records from the V&A and the British Museum, alongside DCMS visitor footfall and KPI data, the work explores cultural representation, geographic patterns and long term visitor trends.

The analysis combines data cleaning, integration, visualisation and predictive modelling to support clearer insight into museum audiences and the cultural material they encounter.

</details>

---

<a id="research-questions"></a>
## 🎯 Research Questions
<details>
<summary><strong>Click to expand</strong></summary>

To guide the analysis and ensure a focused approach across the collections and visitor data, the project addressed the following research questions:
1. How are cultures, regions, materials and techniques represented across sculpture collections, and how have these changed over time
2. How have visitor numbers to national museums changed over the past two decades
3. What relationship can be observed between visitor attendance and museum income
4. Can future museum footfall be forecast using time series models

</details>

---

<a id="datasets"></a>
## 📚 Datasets
<details>
<summary><strong>Click to expand</strong></summary>

**V&A Collections API**  
Structured API queries retrieving sculpture objects with production place, date, materials and techniques.  
https://www.vam.ac.uk/collections

**British Museum Collections CSV**  
Downloaded sculpture object records requiring substantial cleaning due to non standardised fields.  
https://www.britishmuseum.org/collection/

**DCMS National Museums Footfall**  
Monthly totals (2004–2025), used to explore seasonality and long term public engagement.  
https://www.gov.uk/government/statistical-data-sets/museums-and-galleries-monthly-visits

**DCMS National Museums KPIs**  
Annual indicators including income and attendance, aligned with visitor trends.  
https://www.gov.uk/government/statistics/dcms-sponsored-museums-and-galleries-annual-performance-indicators-202324

**Tate Collections (GitHub)**  
Publicly accessible object metadata used for comparative analysis.  
https://github.com/tategallery/collection

**Tate Temporary Exhibitions (Figshare)**  
Dataset documenting exhibition duration and medium.  
https://figshare.com/articles/dataset/Temporary_Exhibitions_at_Tate_Modern_-_2008_to_2016/5766570

</details>

---

<a id="repository-structure"></a>
## 📁 Repository Structure
<details>
<summary><strong>Click to expand</strong></summary>

The project repository is organised to separate data cleaning, exploratory work, modelling and final outputs, ensuring clarity, reproducibility and ease of navigation.
```mermaid
flowchart TB

    A([📁 MUSEUM_PROJECT])

    subgraph COL[📂 collections]
        C1([📂 data])
        C2([📂 notebooks])
        C3([📂 visualisations])
        C4([📂 api])
    end

    subgraph KPI[📂 kpis]
        K1([📂 data])
        K2([📂 notebooks])
        K3([📂 visualisations])
    end

    subgraph ML[📂 machine_learning]
        M1([📂 data])
        M2([📂 notebooks])
        M3([📂 visualisations])
    end

    A --> COL
    A --> KPI
    A --> ML
    A --> IG([📝 .gitignore])
    A --> README([📝 README.md])
    A --> REQ([📝 requirements.txt])
    A --> NOTE([📝 notebook_reference.md])
```

</details>

---

<a id="project-workflow"></a>
## 🔄 Project Workflow
<details>
<summary><strong>Click to expand</strong></summary>

The project workflow combined a planned sequence of tasks with iterative refinement, progressing from data collection and cleaning to integration, analysis, visualisation and modelling.

```mermaid
flowchart TD

    Start([Start])

    %% DATA SOURCES
    subgraph Datasets [Datasets]
        direction LR
        VA[(V&A API Dataset)]
        BM[(British Museum Dataset)]
        FF[(Footfall Dataset)]
        Tate[(Tate Exhibitions Dataset)]
        KPI[(DCMS KPI Dataset)]
    end

    Start --> VA
    Start --> BM
    Start --> FF
    Start --> Tate
    Start --> KPI

    VA --> Clean[Data Cleaning & Standardisation]
    BM --> Clean
    FF --> Clean
    Tate --> Clean
    KPI --> Clean

    %% COLLECTIONS WORKFLOW
    subgraph Collections [Collections Workflow]
        direction TB
        ColData[Collections Data]
        Dates[Date Standardisation]
        Places[Place Normalisation]
        Materials[Materials]
        Techniques[Techniques]
        ColData --> Dates
        ColData --> Places
        ColData --> Materials
        ColData --> Techniques
        Dates --> ColOut[Collections Output]
        Places --> ColOut
        Materials --> ColOut
        Techniques --> ColOut
    end

    Clean --> ColData

    %% KPI AND FOOTFALL WORKFLOW
    subgraph KPI_Workflow [KPI & Footfall Workflow]
        direction TB
        KPIData[KPI & Footfall Data]
        Annual[Annual KPI Analysis]
        Monthly[Monthly Footfall Aggregation]
        Annual --> KPIOut[KPI Output]
        Monthly --> FootOut[Footfall Output]
    end

    Clean --> KPIData
    KPIData --> Annual
    KPIData --> Monthly

    %% MODELLING WORKFLOW
    subgraph ML_Workflow [Machine Learning Workflow]
        direction LR
        Select[Model Selection]
        FE[Feature Engineering]
        CV[Cross Validation]
        Eval[Model Evaluation]
        Select --> FE --> CV --> Eval --> ModelOut[Model Output]
    end

    FootOut --> Select

    %% OUTPUT STAGE
    ColOut --> Viz[Visualisations]
    KPIOut --> Viz
    ModelOut --> Viz
    Viz --> Conclusions[Conclusions]
    Conclusions --> Report([Report Creation & Documentation])

```

</details>

---

<a id="methods-summary"></a>
## 🛠️ Methods Summary
<details>
<summary><strong>Click to expand</strong></summary>

The following summary outlines the key methods applied in cleaning, standardising and integrating the datasets, and the analytical and modelling techniques used to produce the final insights.

### 🏺 Collections Strand  
- Standardised dates into start, end and midpoint years  
- Normalised production place names and mapped to modern countries  
- Cleaned materials and techniques fields  
- Integrated datasets for combined visualisation  

### 👥 Footfall Strand  
- Reshaped monthly DCMS data into a continuous time series  
- Analysed seasonality and long term patterns  
- Tested regression, XGBoost and ARIMA models  

### 📊 KPI Strand  
- Cleaned annual income and attendance data  
- Standardised museum names and year structures  
- Corrected malformed financial values  
- Merged multiple tables into a single analysis dataset  

</details>

---

<a id="results-summary"></a>
## 📈 Results Summary
<details>
<summary><strong>Click to expand</strong></summary>

### 🏺 Collections Findings
- Eurocentric distribution dominated by Italy, the UK, Greece and Egypt  
- BM shows wider global coverage; V&A more European  
- Distinct institutional collecting patterns revealed  

### 📊 KPI Insights
- Income and footfall both peak around 2014–15  
- Income declines slightly afterwards despite steady attendance  
- Strong recovery by 2023–24  

### 👥 Footfall Trends
- Steady growth 2004–2019, sharp decline during pandemic  
- Some museums now exceed pre-pandemic attendance  
- Strong seasonal variation (summer peaks, winter lows)  

### 🤖 Machine Learning Outcomes
- XGBoost performed best in early tests  
- Produces reasonable overall volume predictions  
- Volatility remains due to structural breaks  

### 🧱 Materials & Techniques Timeline
- Long lived techniques (carving, casting) appear across millennia  
- Terracotta, marble and bronze persist through history  
- Later periods show denser, better documented activity  

</details>

---

<a id="setup--requirements"></a>
## ⚙️ Setup & Requirements 
<details>
<summary><strong>Click to expand</strong></summary>

Install dependencies:

```
pip install -r requirements.txt
jupyter notebook
```

Required libraries:

- python  
- pandas  
- numpy  
- matplotlib  
- seaborn  
- scikit learn  
- statsmodels  
- xgboost  
- jupyter notebook  

</details>

---

<a id="how-to-run-the-project"></a>
## ▶️ How to Run the Project
<details>
<summary><strong>Click to expand</strong></summary>

A full running order of all notebooks used in the project can be found in notebook_reference.md.

1. Clone the repository  
2. Install dependencies listed in requirements.txt  
3. The general flow of the analysis is from `collections` to `machine_learning` and then to `kpis`  
4. Notebooks are designed to be run independently and are linked to source files already saved in the repository `data` folders  
5. Example visualisations are already saved in the `visualisation` folders, but it is also possible to generate them directly by running the notebooks  

</details>

---

<a id="project-timeline"></a>
## 🗓️ Project Timeline
<details>
<summary><strong>Click to expand</strong></summary>

```mermaid
gantt
    title Museum Project Timeline
    dateFormat  YYYY-MM-DD
    axisFormat  %d %b

    section Milestones
    Project Kickoff                    :milestone, m1, 2025-11-10, 0d
    Initial proposal due               :milestone, m2, 2025-11-23, 0d
    Final project submission           :milestone, m3, 2025-12-12, 0d

    section Planning
    Set up repo                        :p1, 2025-11-10, 2025-11-12
    Create project plan                :p2, 2025-11-10, 2025-11-14
    Finalise research questions        :p3, 2025-11-10, 2025-11-20
    Agree datasets                     :p4, 2025-11-20, 2025-11-21
    Draft project proposal             :p5, 2025-11-21, 2025-11-22

    section Data Collection
    Examine and choose datasets        :d1, 2025-11-15, 2025-11-20
    Download KPI datasets              :d2, 2025-11-17, 2025-11-21
    Download BM dataset                :d3, 2025-11-17, 2025-11-21
    Download V&A dataset               :d4, 2025-11-17, 2025-11-21

    section Data Cleansing
    Cleansing BM dataset               :c1, 2025-11-21, 2025-11-27
    Cleansing V&A dataset              :c2, 2025-11-21, 2025-11-27
    Cleansing footfall dataset         :c3, 2025-11-21, 2025-11-27
    Cleansing kpi dataset              :c4, 2025-11-23, 2025-11-29
    Data integration                   :c5, 2025-11-27, 2025-12-03

    section Analysis & Visualisation
    Core analysis                      :a1, 2025-12-01, 2025-12-08
    Visualisation                      :a2, 2025-12-01, 2025-12-08
    Predictive modelling               :a3, 2025-12-04, 2025-12-10
    Interpretation & narrative         :a4, 2025-12-05, 2025-12-10

    section Final Output
    Build presentation slides          :f1, 2025-12-05, 2025-12-12
    Assemble final report              :f2, 2025-12-05, 2025-12-12
    Integrate visuals                  :f3, 2025-12-05, 2025-12-12
```

</details>

---

<a id="contributors"></a>
## 👥 Contributors
<details>
<summary><strong>Click to expand</strong></summary>
 
**Angie**

**Diana**  
https://github.com/dianaasihene

**Jenny**  
https://github.com/jeenny

**Jennifer**  
https://github.com/jennifer-hunter

**Jo-Ann**  
https://github.com/Jo-bin

**Nicky**  
https://github.com/nickscross

</details>
