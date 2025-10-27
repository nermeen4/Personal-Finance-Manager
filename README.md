💰 Personal Finance Manager
A console-based Python application that helps users track finances, manage budgets, set savings goals, and view powerful financial reports — all with persistent data storage


📌 Project Overview
This application enables users to:

✅ Manage multiple accounts securely
✅ Track income & expenses
✅ Visualize spending and earning patterns
✅ Set monthly budgets & savings goals
✅ View detailed dashboard analytics
✅ Store data safely using JSON with backups

This is a well-structured real-world finance tracking system built using Python fundamentals


🏗️ Project Structure

   Personal-Finance-Manager/
│
├─ main.py                     # Application entry point
├─ data/                       # Persistent storage
│   ├─ users.json
│   ├─ transactions.json
│   └─ backups/
│
├─ core/                       # Core system modules
│   ├─ auth.py
│   ├─ transactions.py
│   ├─ reports.py
│   ├─ search_filter.py
│   ├─ data_manager.py
│   ├─ ascii_viz.py
│
└─ advanced_feature/           # Advanced features
    ├─ savings.py
    ├─ budget.py
    └─ bills.py (future)



✨ Features
✅ Core Features
Feature	Description
👤 User Management	Register, login, multi-user support
💳 Transactions	Add, edit, view, delete expenses & income
🔍 Search & Filter	Filter by date, amount, category
📊 Reports	Dashboard, trends, category analytics
💾 Data Persistence	JSON storage + auto-save + backup
🧩 Menu Navigation	Clean UI and input validation



🚀 Advanced Features
✅ Savings Goals with progress bars	✅
✅ Monthly Budget Management	✅
✅ ASCII Chart Visualization	✅
✅ Data Backup System	✅
✅Bill Reminders	        ✅

🎯 More advanced features can be added easily thanks to modular architecture.


📊 Sample Reports & Visuals

📊 DASHBOARD SUMMARY
------------------------------
Total Income : 9000 EGP
Total Expense: 2600 EGP
Balance      : 6400 EGP

📈 SPENDING TRENDS (ASCII)
2025-01 | ████████  1600
2025-02 | ████      1000
2025-03 | ██         350


🧠 Technologies Used

Python 3.10+
json — Data storage
datetime — Date handling
decimal.Decimal — Money calculations


▶️ How to Run

1️⃣ Clone the repository
git clone https://github.com/nermeen4/Personal-Finance-Manager.git
cd Personal-Finance-Manager

2️⃣ Run the main program
python3 main.py



🔐 User Credentials & Security
1-Secure login system using username + PIN/password
2-Users only see their own transactions
3-Data is backed up automatically to avoid loss



🤝 Contributors
👩‍💻 Nermeen Magdy 
👨‍💻 Mohamed Mokhtar



🎥 Future Enhancements
1-Email or notification-based bill reminders
2-Financial Health Scoring system
3-Export & Import as CSV
4-Predictive analytics using ML
5-Web or Mobile user interface


📄 License
This project is open-source for educational and portfolio use.
Feel free to fork and improve!


