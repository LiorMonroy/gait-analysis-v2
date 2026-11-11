# Gait Analysis in Parkinson's Disease (v2)

Python rebuild of my BME100 project comparing walking patterns of people with Parkinson's disease and healthy controls, using foot-pressure insole data from the PhysioNet Gait in Parkinson's Disease database.

v1 was in MATLAB with 12 participants. v2 aims to fix its limitations:
- use all participants in the database
- normalise forces by body weight
- detect individual steps
- run real statistical tests
- show a foot-shaped pressure heatmap

## Status
- [x] Project setup
- [x] Load and plot one walking trial