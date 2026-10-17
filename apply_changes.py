"""Applies 5 website changes to the project, one git commit per change,
then writes the commit hashes into the README change table.

Run from the project root with the virtual environment active:
    python apply_changes.py
"""
import importlib.util
import subprocess
import sys

MARKER = "<!-- CHANGES_TABLE -->"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit("git " + " ".join(args) + " failed:\n" + r.stdout + r.stderr)
    return r.stdout.strip()


def edit(path, old, new):
    text = read(path)
    if old not in text:
        sys.exit("Could not apply the change: expected text not found in " + path
                 + "\n--- looking for ---\n" + old[:120])
    write(path, text.replace(old, new, 1))


def add_tests(code):
    write("tests/test_app.py", read("tests/test_app.py").rstrip("\n") + "\n\n\n" + code.strip("\n") + "\n")


def run_tests():
    if importlib.util.find_spec("pytest") is None:
        print("  (pytest not found, skipping test run)")
        return
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
    if r.returncode:
        sys.exit("Tests failed, stopping before commit:\n" + r.stdout + r.stderr)
    print("  tests passed")


# ---------------------------------------------------------------- changes
def change1():
    edit("templates/index.html", "  footer { text-align", """  .how { grid-column: 1 / -1; }
  .how h2 { margin: 0 0 10px; font: 700 1.5rem Palatino, Georgia, serif; }
  .how ol { margin: 0; padding-left: 20px; }
  .how li { margin-bottom: 6px; }
  footer { text-align""")
    edit("templates/index.html", "</main>\n<footer>", """  <section class="card how" aria-label="How it works">
    <h2>How it works</h2>
    <ol>
      <li>You choose a dish, portion size, extra oil or butter and the number of servings.</li>
      <li>A RandomForest model trained on typical nutrition values predicts the protein, carbs and fat for your meal.</li>
      <li>Calories are calculated as 4 x protein + 4 x carbs + 9 x fat.</li>
    </ol>
  </section>
</main>
<footer>""")


def change2():
    edit("templates/index.html", "  footer { text-align",
         "  .per { margin: 10px 0 0; color: var(--muted); font-size: .9rem; }\n  footer { text-align")
    edit("templates/index.html",
         '<span class="tag" id="label" data-level="light">Light snack</span>',
         '<span class="tag" id="label" data-level="light">Light snack</span>\n    <p class="per" id="per"></p>')
    edit("templates/index.html",
         '      document.getElementById("percent").textContent = data.daily_percent + "%";',
         '      document.getElementById("percent").textContent = data.daily_percent + "%";\n'
         '      document.getElementById("per").textContent = data.per_serving + " kcal per serving";')


def change3():
    edit("app.py", '@app.route("/health")', '''@app.route("/dishes")
def dishes():
    """List the available dishes and what one serving means."""
    return jsonify([{"name": n, "serving": v[3]} for n, v in DISHES.items()])


@app.route("/health")''')
    add_tests('''
def test_dishes_endpoint():
    res = client.get("/dishes")
    assert res.status_code == 200
    names = [d["name"] for d in res.get_json()]
    assert len(names) == 8
    assert "Misal Pav" in names
''')


def change4():
    edit("app.py", '''    item, error = parse_item(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    result = predict_nutrition(model, *item)
    result.update({
        "dish": item[0],
        "daily_percent": round(result["total"] / DAILY_KCAL * 100, 1),''', '''    data = request.get_json(silent=True) or {}
    item, error = parse_item(data)
    if error:
        return jsonify({"error": error}), 400
    try:
        goal = int(data.get("daily_goal", DAILY_KCAL))
    except (TypeError, ValueError):
        return jsonify({"error": "Daily goal must be a whole number."}), 400
    if not 1000 <= goal <= 5000:
        return jsonify({"error": "Daily goal must be between 1000 and 5000 kcal."}), 400
    result = predict_nutrition(model, *item)
    result.update({
        "dish": item[0],
        "daily_goal": goal,
        "daily_percent": round(result["total"] / goal * 100, 1),''')
    edit("templates/index.html", "  footer { text-align",
         '  #goal { width: 160px; padding: 10px 12px; border: 2px solid var(--line); border-radius: 12px; '
         'font: 700 1rem "Trebuchet MS", sans-serif; color: var(--ink); }\n  footer { text-align')
    edit("templates/index.html",
         '      <button type="button" id="plus" aria-label="Increase servings">+</button>\n    </div>\n  </section>',
         '      <button type="button" id="plus" aria-label="Increase servings">+</button>\n    </div>\n\n'
         '    <p class="step"><b>5</b> Your daily calorie goal</p>\n'
         '    <input type="number" id="goal" value="2000" min="1000" max="5000" step="50" aria-label="Daily calorie goal in kcal">\n'
         '  </section>')
    edit("templates/index.html", "      quantity: qty\n    };",
         '      quantity: qty,\n      daily_goal: document.getElementById("goal").value\n    };')
    edit("templates/index.html", "<span>of a 2000 kcal day</span>", '<span id="goaltxt">of a 2000 kcal day</span>')
    edit("templates/index.html",
         '      document.getElementById("percent").textContent = data.daily_percent + "%";',
         '      document.getElementById("percent").textContent = data.daily_percent + "%";\n'
         '      document.getElementById("goaltxt").textContent = "of a " + data.daily_goal + " kcal day";')
    add_tests('''
def test_custom_daily_goal_changes_percent():
    base = post().get_json()
    res = client.post("/predict", json={"dish": "Vada Pav", "size": "Regular", "extra": "None",
                                        "quantity": 1, "daily_goal": 1000})
    assert res.status_code == 200
    assert res.get_json()["daily_percent"] > base["daily_percent"]


def test_invalid_daily_goal_rejected():
    res = client.post("/predict", json={"dish": "Vada Pav", "size": "Regular", "extra": "None",
                                        "quantity": 1, "daily_goal": 50})
    assert res.status_code == 400
''')


def change5():
    edit("app.py", "import json\n", "import json\nfrom datetime import datetime\n")
    edit("app.py", 'body = json.dumps({"app": "Kolhapur Street Food Calorie Estimator",',
         'body = json.dumps({"app": "Kolhapur Street Food Calorie Estimator",\n'
         '                       "generated_at": datetime.now().isoformat(timespec="seconds"),')
    add_tests('''
def test_report_has_timestamp():
    items = [{"dish": "Vada Pav", "size": "Regular", "extra": "None", "quantity": 1}]
    body = client.post("/report", json={"items": items}).get_json()
    assert "generated_at" in body
''')


CHANGES = [
    ("Add How it works section to the page", "templates/index.html", change1,
     "Add How it works section to the page"),
    ("Show calories per serving in the result card", "templates/index.html", change2,
     "Show calories per serving in the result card"),
    ("Add /dishes API endpoint with a test", "app.py, tests/test_app.py", change3,
     "Add /dishes API endpoint with a test"),
    ("Add customizable daily calorie goal", "app.py, templates/index.html, tests/test_app.py", change4,
     "Add customizable daily calorie goal"),
    ("Add timestamp to the downloaded report", "app.py, tests/test_app.py", change5,
     "Add generated_at timestamp to the downloaded report"),
]


def main():
    if MARKER not in read("README.md"):
        sys.exit("README.md does not contain " + MARKER + ". Copy the new README.md into the project first.")
    if git("status", "--porcelain", "--untracked-files=no"):
        sys.exit("You have uncommitted changes. Commit them first (git add . and git commit), then run again.")

    rows = []
    for number, (title, files, func, message) in enumerate(CHANGES, 1):
        print(f"Change {number}: {title}")
        func()
        run_tests()
        git("add", "app.py", "templates/index.html", "tests/test_app.py")
        git("commit", "-m", message)
        rows.append(f"| {number} | {title} | {files} | `{message}` | `{git('rev-parse', '--short', 'HEAD')}` |")

    table = ("| No. | Change | Files changed | Commit message | Commit |\n"
             "|-----|--------|---------------|----------------|--------|\n" + "\n".join(rows))
    write("README.md", read("README.md").replace(MARKER, table))
    git("add", "README.md")
    git("commit", "-m", "Add change log with commit hashes to README")

    print("\nDone. Your commit history:\n")
    print(git("log", "--oneline", "-8"))
    print("\nNow run: git push")


main()
