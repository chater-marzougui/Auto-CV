import { useState } from "react";
import { ThemeProvider } from "@/components/theme-provider";
import { Sidebar } from "@/components/sidebar";
import { BottomNavbar } from "@/components/bottom-navbar";
import { MobileHeader } from "@/components/mobile-header";
import { PersonalInfo } from "@/pages/personal-info";
import { JobAnalysis } from "@/pages/job-analysis";
import ProjectManagement from "@/pages/project-management";
import "./App.css";
import { Toaster } from "sonner";
import { CVGenerator } from "./pages/cv-generator";
import { JobApplications } from "./pages/job-applications";
import { useIsMobile } from "@/hooks/use-mobile";

type ActiveTab = "job-analysis" | "projects" | "cv-generator" | "personal-info" | "job-applications";

function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("job-analysis");
  const isMobile = useIsMobile();

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
      case "job-applications":
        return <JobApplications />;
      default:
        return <JobAnalysis />;
    }
  };

  return (
    <ThemeProvider defaultTheme="system" storageKey="auto-cv-theme">
      <Toaster richColors duration={3000} position="top-right" />
      <div className="flex flex-col h-screen bg-background">
        {/* Mobile Header */}
        {isMobile && <MobileHeader />}
        
        <div className="flex flex-1">
          {/* Desktop Sidebar */}
          {!isMobile && <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />}
          
          {/* Main Content */}
          <main className={`flex-1 overflow-hidden ${isMobile ? 'pb-16' : ''}`}>
            {renderActiveComponent()}
          </main>
        </div>
        
        {/* Mobile Bottom Navigation */}
        {isMobile && <BottomNavbar activeTab={activeTab} onTabChange={setActiveTab} />}
      </div>
    </ThemeProvider>
  );
}

export default App;
