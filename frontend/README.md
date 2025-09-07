
# Auto-CV Frontend

This is the frontend for **Auto-CV**, an AI-powered CV and cover letter generator. It provides a modern web interface for generating tailored job applications based on your GitHub projects and job descriptions.

## 🚀 Features

- **React + TypeScript + Vite**: Fast, modern frontend stack
- **Tailwind CSS**: Utility-first styling
- **Radix UI**: Accessible UI components
- **Live Progress**: Real-time updates via WebSocket
- **Project Matching**: View matched projects based on semantic similarity
- **Document Generation**: Generate professional CVs and cover letters

## ⚡ Getting Started

### Prerequisites

- Node.js 16+
- Backend API running (see main project README)

### Installation

1. Install dependencies:
  ```bash
  npm install
  ```
2. Start the development server:
  ```bash
  npm run dev
  ```
3. The app will be available at [http://localhost:5173](http://localhost:5173)

## 📝 Usage

1. Enter your GitHub username to analyze your repositories
2. Paste a job description to match relevant projects
3. Generate CV and cover letter with one click

## 🛠️ Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   ├── hooks/           # Custom hooks
│   ├── lib/             # Utility functions
│   ├── config/          # App configuration
│   └── assets/          # Static assets
├── app/                 # Global styles
├── public/              # Public files
├── index.html           # Main HTML file
├── package.json         # Project config
└── README.md            # This file
```

## 🧩 Technologies

- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)

## 🤝 Contributing

Contributions are welcome! Please open issues or pull requests in the main [Auto-CV repository](https://github.com/chater-marzougui/Auto-CV).

## 📃 License

Distributed under the MIT License. See `LICENSE` for details.

---

**Revolutionize your job applications with AI-powered CV generation.**
