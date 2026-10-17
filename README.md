# Kolhapur Street Food Calorie Estimator

A Flask web app where you pick a Kolhapur street food (Misal Pav, Vada Pav, Pav Bhaji, Samosa, Jalebi, Masala Dosa, Bhel Puri, Sabudana Khichdi), choose portion size, extra oil and servings, and a **scikit-learn RandomForest model** predicts protein, carbs and fat. Calories are calculated as `4 x protein + 4 x carbs + 9 x fat`.

Built for DevOps ISE-II using Git, GitHub, Jenkins, Ansible and Docker.

## Features
- ML-based nutrition prediction with live results
- **My Plate** meal builder with total calories and macros
- Macro split chart (protein / carbs / fat share of calories)
- **Download report** (JSON) for the whole plate
- 17 automated pytest tests

## Run locally
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

## Run tests
```
python -m pytest -v
```

## Run with Docker
```
docker build -t calorie-estimator .
docker run -d -p 5000:5000 --name calorie-app calorie-estimator
```

## CI/CD pipeline
GitHub push -> Jenkins (Checkout -> Install -> Test -> Deploy with Ansible) -> health check on `/health`.

Files: `Jenkinsfile`, `deploy.yml` (Ansible playbook), `inventory.ini`, `jenkins/Dockerfile` (Jenkins image with Python and Ansible).

## Versions
| Tool | Version |
|------|---------|
| Python | fill in (`python --version`) |
| Flask | 3.0.3 |
| scikit-learn | fill in (`pip show scikit-learn`) |
| NumPy | fill in (`pip show numpy`) |
| Gunicorn | fill in (`pip show gunicorn`) |
| pytest | fill in (`pip show pytest`) |
| Git | fill in (`git --version`) |
| Docker | fill in (`docker --version`) |
| Jenkins | fill in (Manage Jenkins > About Jenkins) |
| Ansible | fill in (`ansible --version`) |

## Data note
Vada Pav values follow the FatSecret database (1 piece, 140 g). Other dishes use typical published values. Real calories vary with recipe and portion.

## Project Screenshots
[View full screenshots report (PDF)](docs/DevOps_ISE-II.pdf)
