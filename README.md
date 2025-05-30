# 🛡️ LegalAssist — Cyber Law Awareness Chatbot for Nepal

**LegalAssist** is an AI-powered legal chatbot built using **FastAPI** (backend) and **plain JavaScript, HTML, and CSS** (frontend), integrated with **Firebase** for user authentication and data storage. It aims to educate users in Nepal about cybersecurity laws, promote safe online behavior, and prevent illegal digital activities through real-time, ethical guidance.

---

## 🌟 Key Features

* 🔐 **User Authentication with Firebase**
  Firebase Authentication ensures secure, reliable login and session handling.

* 💬 **Chatbot for Legal Guidance**
  An interactive chatbot that provides information about Nepal’s cyber laws and helps users understand the legal consequences of online actions.

* 📊 **Behavior Analysis**
  Tracks common risky or illegal user queries and responds with preventive education, not punishment.

* 🧠 **Ethical Awareness Engine**
  Uses natural language understanding to distinguish between genuine curiosity and intentional harm, encouraging better digital behavior.

* 🌐 **Simple, Lightweight Frontend**
  Built with plain HTML, CSS, and JavaScript for fast loading and easy integration.

---

## 🏗️ Tech Stack

* **Backend**: FastAPI (Python)
* **Frontend**: HTML + CSS + JavaScript (Vanilla)
* **Authentication & Data**: Firebase (JS SDK v8.10.1)
* **Hosting**: Firebase Hosting / Local Server

---

## 📂 Project Structure

```
LegalAssist/
├── backend/
│   └── main.py                 # FastAPI server routes
├── frontend/
│   ├── index.html              # Main UI
│   ├── style.css               # Stylesheet
|   ├── chatbot.js              # Chatbot logic
│   └── auth.js                 # Firebase integration
├── firebase/
│   └── firebase-config.js      # Firebase SDK config
├── README.md
└── requirements.txt            # Python dependencies
```

---

## 🧪 How to Run Locally

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/LegalAssist.git
   cd LegalAssist
   ```

2. **Install Backend Requirements**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start FastAPI Server**

   ```bash
   uvicorn backend.main:app --reload
   ```

4. **Open `index.html` in your browser**
   (Serve via Live Server or any HTTP server to avoid Firebase Auth issues.)

---

## 👨‍💻 Team

Built with ❤️ by a group of four students as part of a university project, led by **Suraj sah(Backend)**, **Pawan Rishal(Chatbot)**, **Utsuk Kharel(Frontend)** and **Aditya Adhikari(UI/ UX)** , focusing on combining AI with law and Order for real-world impact around the globe.

---

## 📌 Future Goals

* Add support for multilingual chat (Nepali/English)
* Integrate NLP for more context-aware responses
* Connect with legal databases for more dynamic answers

---

## 📄 License

This project is open source under the **MIT License**.

---

## 🤝 Contributing

Contributions are welcome! Please submit pull requests, issues, or suggestions.
