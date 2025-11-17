# ⚙️ Python 3.13 Automation Environment Setup (VS Code)

This guide sets up a Python 3.13 virtual environment named `automation` with essential packages for web automation and dashboard development using VS Code.

---

## 📦 Required Tools

- Python 3.13 (installed and added to PATH)
- Visual Studio Code
- Python extension for VS Code
- Optional: Jupyter extension (for notebooks)

---

## 🧪 Step 1: Create Virtual Environment with Python 3.13

```bash
py -3.13 -m venv automation
```

This creates a folder named `automation` containing your virtual environment.

---

## ▶️ Step 2: Activate the Environment

- **Command Prompt:**
  ```bash
  automation\Scripts\activate
  ```
- **PowerShell:**
  ```bash
  .\automation\Scripts\Activate.ps1
  ```

---

## 📁 Step 3: Create `requirements.txt`

Create a file named `requirements.txt` in your project folder with the following content:

```txt
streamlit
selenium
webdriver-manager
python-dotenv
```

To install all packages:

```bash
pip install -r requirements.txt
```

---

## 🧠 Step 4: VS Code Integration

1. Open your project folder in VS Code.
2. Press `Ctrl+Shift+P` → “Python: Select Interpreter”
3. Choose:
   ```
   .\automation\Scripts\python.exe (3.13.x)
   ```

If not listed:

- Click “Enter interpreter path”
- Browse to: `automation\Scripts\python.exe`

---

## 🧪 Step 5: Verify Setup

```bash
python --version
```

Should return `Python 3.13.x`.

---

## 🚀 Step 6: Run Streamlit App

```bash
streamlit run app.py
```

---

## ✅ Tips

- Always activate the environment before running scripts.
- Use `.gitignore` to exclude `.env` from version control.
- Use `python-dotenv` to keep credentials secure and configurable.
