# Kolhapur Street Food Calorie Estimator

## 1. Project introduction and objective
The Kolhapur Street Food Calorie Estimator is a Flask website that estimates the calories and macronutrients (protein, carbohydrates and fat) of popular Kolhapur street foods using a scikit-learn machine learning model.

**Objective:** build a unique website, manage it with Git and GitHub through several meaningful changes, and integrate a DevOps tool (Jenkins) that automatically builds and tests the project on every commit.

The user picks a dish (Misal Pav, Vada Pav, Pav Bhaji, Samosa, Jalebi, Masala Dosa, Bhel Puri or Sabudana Khichdi), a portion size, the amount of extra oil/butter/farsan and the number of servings. A RandomForest model predicts protein, carbs and fat, and calories are calculated as:

```
kcal = 4 x protein + 4 x carbs + 9 x fat
```

### Features
- ML-based nutrition prediction with instant results
- My Plate meal builder with total calories and macros
- Macro split bar (share of calories from protein, carbs and fat)
- Downloadable JSON report of the plate
- Adjustable daily calorie goal
- 21 automated pytest tests

## 2. Technology stack and how to run

| Area | Technology |
|------|------------|
| Backend | Python, Flask |
| Machine learning | scikit-learn (RandomForest), NumPy |
| Frontend | HTML, CSS, JavaScript |
| Testing | pytest |
| Version control | Git, GitHub |
| DevOps tool | Jenkins (CI pipeline) |
| Containerization | Docker |

### Folder structure
```
.
├── app.py                 Flask application and API routes
├── model.py               Nutrition data, ML model training and prediction
├── templates/
│   └── index.html         Web page (HTML, CSS, JavaScript)
├── tests/
│   └── test_app.py        pytest tests
├── docs/
│   └── screenshots/       Screenshots used in this README
├── Dockerfile             Container image for the app
├── Jenkinsfile            Jenkins pipeline
├── pytest.ini             pytest configuration
├── requirements.txt       Python dependencies
└── README.md
```

### Run the website
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000. The model trains automatically on first start.

### Run the tests
```
python -m pytest -v
```

### Run with Docker
```
docker build -t calorie-estimator .
docker run -d -p 5000:5000 --name calorie-app calorie-estimator
```

### API routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Web page |
| `/predict` | POST | Nutrition for one dish |
| `/report` | POST | Downloadable JSON report for the plate |
| `/dishes` | GET | List of available dishes |
| `/health` | GET | Health check |

### Versions used
| Tool | Version |
|------|---------|
| Python | 3.13.1 |
| Flask | 3.0.3 |
| scikit-learn | >= 1.5.2 |
| NumPy | >= 2.1 |
| Gunicorn | >= 22.0 |
| pytest | 9.1.1 |
| Git | 2.55.0.windows.3 |
| Docker | 29.8.2 |
| Jenkins | 2.568.2 |

## 3. Changes made (with commit details)
After the first version of the website was uploaded, these five changes were made and committed one by one:

<!-- CHANGES_TABLE -->

Run `git log --oneline` to see the complete history, which is also shown in the screenshots below.

## 4. Git and GitHub workflow
**Repository:** https://github.com/Devileye00/calorie-estimator (branch `main`)

Commands used to create the repository and upload the project:
```
git init
git add .
git commit -m "Initial commit: Kolhapur calorie estimator"
git branch -M main
git remote add origin https://github.com/Devileye00/calorie-estimator.git
git push -u origin main
```

Workflow used for every change:
```
# edit the code, then run the tests
python -m pytest -v
git add <changed files>
git commit -m "Short description of the change"
git push
git log --oneline          # view the commit history
```

## 5. DevOps tool integration: Jenkins
Jenkins is used for Continuous Integration. Every new commit on GitHub is checked out, installed and tested automatically.

### Integration steps
1. Install Jenkins on Windows and open http://localhost:8080.
2. Unlock Jenkins with the initial admin password, install the suggested plugins and create an admin user.
3. Make sure Git and Python are installed on the same machine, and note the Python path used in the `Jenkinsfile`.
4. Create the job: **New Item**, name `Calorie-Estimator-CI`, type **Pipeline**.
5. Under Pipeline choose **Pipeline script from SCM**, SCM **Git**, Repository URL `https://github.com/Devileye00/calorie-estimator.git`, Branch `*/main`, Script Path `Jenkinsfile`.
6. Under Build Triggers enable **Poll SCM** with `H/2 * * * *` so a push starts a build automatically.
7. Save the job and click **Build Now**.

### Pipeline stages (Jenkinsfile)
1. **Checkout**: pulls the latest code from GitHub
2. **Install Dependencies**: creates a virtual environment and installs `requirements.txt`
3. **Test**: runs pytest and publishes the test results in Jenkins

### Result
The first two builds failed because the first `Jenkinsfile` used Linux `sh` commands, which do not exist on Windows. After switching to Windows `bat` commands the pipeline succeeded (build #3), and every test passed. A push to GitHub now triggers a new build automatically.

## 6. Screenshots (proof)

**Figure 1: Home page of the website**

![Home page](docs/screenshots/01-home.png)

**Figure 2: Nutrition result for a selected dish**

![Dish result](docs/screenshots/02-result.png)

**Figure 3: My Plate with several dishes added**

![My Plate](docs/screenshots/03-my-plate.png)

**Figure 4: Git commit history (`git log --oneline`)**

![Git log](docs/screenshots/07-git-log.png)

**Figure 5: GitHub repository with all project files**

![GitHub repository](docs/screenshots/08-github-repo.png)

**Figure 6: Commit history on GitHub**

![GitHub commits](docs/screenshots/09-github-commits.png)

**Figure 7: Jenkins job with successful builds**

![Jenkins job](docs/screenshots/04-jenkins-job.png)

**Figure 8: Jenkins console output with all tests passing**

![Jenkins console](docs/screenshots/05-jenkins-console.png)

**Figure 9: Docker container running the website**

![Docker container](docs/screenshots/06-docker.png)

## Data note
Vada Pav values follow the FatSecret database (1 piece, 140 g). The other dishes use typical published values for a standard serving. Real calories vary with recipe and portion, so results are estimates.
