import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  FileText,
  GitBranch,
  Briefcase,
  Github,
  PersonStanding,
  FileCheck,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";

interface SidebarProps {
  activeTab: string;
  onTabChange: (
    tab: "job-analysis" | "projects" | "cv-generator" | "personal-info" | "job-applications"
  ) => void;
}

export function Sidebar({ activeTab, onTabChange }: Readonly<SidebarProps>) {
  const menuItems: Array<{
    id: "job-analysis" | "projects" | "cv-generator" | "personal-info" | "job-applications";
    label: string;
    icon: React.ElementType;
    description: string;
  }> = [
    {
      id: "job-analysis" as const,
      label: "Job Analysis",
      icon: Briefcase,
      description: "Analyze job descriptions",
    },
    {
      id: "projects" as const,
      label: "Projects",
      icon: GitBranch,
      description: "Manage GitHub projects",
    },
    {
      id: "cv-generator" as const,
      label: "CV Generator",
      icon: FileText,
      description: "Generate CV",
    },
    {
      id: "personal-info" as const,
      label: "Personal Info",
      icon: PersonStanding,
      description: "Manage personal information",
    },
    {
      id: "job-applications" as const,
      label: "Job Applications",
      icon: FileCheck,
      description: "Track your applications",
    },
  ];

  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Github className="h-8 w-8 text-sidebar-primary" />
            <div>
              <h2 className="font-heading font-bold text-3xl text-sidebar-foreground">
                Auto-CV
              </h2>
              <p className="text-sm text-sidebar-foreground/60">
                AI-powered CV generator
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <Button
              key={item.id}
              variant={activeTab === item.id ? "default" : "ghost"}
              className={cn(
                "w-full justify-start gap-3 h-auto p-3 cursor-pointer",
                activeTab === item.id
                  ? "bg-sidebar-primary hover:bg-sidebar-primary-hover text-sidebar-primary-foreground"
                  : "bg-sidebar-secondary text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              )}
              onClick={() => onTabChange(item.id)}
            >
              <Icon className="h-5 w-5" />
              <div className="text-left">
                <div className="font-medium">{item.label}</div>
                <div className="text-xs opacity-70">{item.description}</div>
              </div>
            </Button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <ThemeToggle />
      </div>
    </div>
  );
}
