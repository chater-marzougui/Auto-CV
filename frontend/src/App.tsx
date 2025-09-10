import { useState } from "react";
import { ThemeProvider } from "@/components/theme-provider";
import { Sidebar } from "@/components/sidebar";
import { PersonalInfo } from "@/pages/personal-info";
import { JobAnalysis } from "@/pages/job-analysis";
import ProjectManagement from "@/pages/project-management";
import "./App.css";
import { Toaster } from "sonner";
import { CVGenerator } from "./pages/cv-generator";

type ActiveTab = "job-analysis" | "projects" | "cv-generator" | "personal-info";

function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("job-analysis");

  const renderActiveComponent = () => {
    switch (activeTab) {
      case "job-analysis":
        return <JobAnalysis />;
      case "projects":
        return <ProjectManagement />;
      case "cv-generator":
        return <CVGenerator />;
      case "personal-info":
        return <PersonalInfo />;
      default:
        return <JobAnalysis />;
    }
  };

  return (
    <ThemeProvider defaultTheme="system" storageKey="auto-cv-theme">
      <Toaster richColors duration={3000} position="top-right" />
      <div className="flex h-screen bg-background">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        <main className="flex-1 overflow-hidden">
          {renderActiveComponent()}
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
