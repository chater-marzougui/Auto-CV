import { useState } from "react";
import { ThemeProvider } from "@/components/theme-provider";
import { Sidebar } from "@/components/sidebar";
import { CVGenerator } from "@/components/cv-generator";
import { JobAnalysis } from "@/components/job-analysis";
import ProjectManagement from "@/components/project-management";
import "./App.css";
import { Toaster } from "sonner";

type ActiveTab = "job-analysis" | "projects" | "cv-generator";

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
