# 📦 Inventory Management System

A simple inventory management application to track products, categories, and stock levels.  
This README explains what the project does, how it works at a high level, and how to install, run, and use it.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.0-blue?style=for-the-badge)

---

## 📚 Table of Contents

- [Project Overview](#project-overview)
- [Main Features](#-main-features)
- [Requirements](#-requirements)
- [Installation & Setup](#️-installation--setup)
- [Build App](#-build-app)
- [Project Structure](#️-project-structure)
- [How to Use](#-how-to-use)
- [Contributing](#-contributing)
- [Reporting Issues](#-reporting-issues)
- [License](#-license)
- [Support & Contact](#-support--contact)

---

## 🧾 Project Overview

**InventoryApp** helps you manage items in stock and organize them into categories.  
It’s a simple yet powerful **inventory management system** built with **Python**, **Tkinter (GUI)**, and **SQLite** for data storage.

---

## ✨ Main Features

- 🧮 **Product Management** — Add, edit, delete, and view products.  
- 📊 **Inventory Control** — Track and update product quantities.  
- 📈 **Reporting** — View sales and inventory statistics.  
- 💾 **Database** — Lightweight, file-based SQLite.  
- 🎯 **Graphical Interface** — Modern UI using `ttkbootstrap`.  
- 📊 **Dashboard** — Quick statistics summary.  
- 🗂️ **Category Management**.  
- 📦 **Stock Level Tracking & Adjustments**.  
- 🔐 **User Authentication** (login/signup, roles).  
- 🔍 **Search & Filter** products.  
- 📤 **Export Reports (CSV / PDF)**.  
- 📥 **Import from CSV** (optional).  

---

## 🚀 Requirements
- Required libraries (auto-installed from `requirements.txt`):
```bash
pip install -r requirements.txt
```


## ⚙️ Installation & Setup

### 1. Download the Project
```bash
git clone https://github.com/Elhussin/inventory-app.git
cd inventory-app

### Switch to Correct Branch
### for Version 1

git checkout main

### for Version 2
git checkout v2

### Run the Application
python app/main_app.py
```
## Build App
```bash shell
pyinstaller --onefile --windowed --noconsole --name="InventorySystem" \
  --add-data="app:app" \
  --hidden-import="PIL._tkinter_finder" \
  --hidden-import="PIL" \
  --hidden-import="Pillow" \
  --additional-hooks-dir=. \
  main.py
  ```


## 🗂️ Project Structure
inventory-app/
├── main.py                  # Main application entry point
├── app/
│   ├── __init__.py
│   ├── constants/           # Constants and field definitions
│   ├── utils/               # Database and helper functions
│   └── ui/                  # User interface components
├── csv_example.csv          # Example data file
├── inventory.db             # SQLite database (auto-created)
├── requirements.txt         # Project dependencies
└── README.md

## 🎯 How to Use

### Main Dashboard

- View all products
- Add data from CSV
- Add new product
- Add stock
- Search and filter products
- View inventory statistics
- Export to CSV or PDF
- Delete products

### ➕ Add Product

- Add new product (name, code, cost, retail, quantity, description)

### 📦 Add Stock

- Add or adjust stock quantities (good, damaged, gift)

### 🔍 Search Products

- Search by code or description

### 📊 View Statistics

- Overview of product counts, stock values, and status

### 📤 Export Options

- Export all or mismatched data to CSV / PDF




## 🤝 Contributing
We welcome contributions! Please follow these steps:

Fork the project

Create a new branch (git checkout -b feature/NewFeature)

Commit your changes (git commit -m 'Add NewFeature')

Push to the branch (git push origin feature/NewFeature)

Open a Pull Request

## 🐛 Reporting Issues
If you find any issues with the application, please open a new issue with a description of the problem.

## 📄 License
This project is licensed under the MIT License [MIT](https://choosealicense.com/licenses/mit/) - see the LICENSE file for details.


## 💬 Support & Contact

If you have any questions, need technical support, or want to discuss features, feel free to reach out:

* **Email:** [hasin3112@gmail.com](mailto:hasin3112@gmail.com)
* **GitHub Issues:** [Open an Issue here](https://github.com/Elhussin/inventory-app/issues) (The preferred way to report bugs)


## 🖼️ Screenshot
![Main Dashboard](https://raw.githubusercontent.com/Elhussin/inventory-app/v2/app/1.png)
![Add Product](https://raw.githubusercontent.com/Elhussin/inventory-app/v2/app/2.png)
## 🖼️ Screenshot

<img src="https://raw.githubusercontent.com/Elhussin/inventory-app/v2/app/1.png" width="700" />
<img src="https://raw.githubusercontent.com/Elhussin/inventory-app/v2/app/2.png" width="700" />





⭐ If you like this project, please consider giving it a star on GitHub!
