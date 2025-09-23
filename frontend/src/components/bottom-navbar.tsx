import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  FileText,
  GitBranch,
  Briefcase,
  PersonStanding,
  FileCheck,
} from "lucide-react";

interface BottomNavbarProps {
  activeTab: string;
  onTabChange: (
    tab: "job-analysis" | "projects" | "cv-generator" | "personal-info" | "job-applications"
  ) => void;
}

export function BottomNavbar({ activeTab, onTabChange }: Readonly<BottomNavbarProps>) {
  const menuItems: Array<{
    id: "job-analysis" | "projects" | "cv-generator" | "personal-info" | "job-applications";
    label: string;
    icon: React.ElementType;
  }> = [
    {
      id: "job-analysis" as const,
      label: "Job",
      icon: Briefcase,
    },
    {
      id: "projects" as const,
      label: "Projects",
      icon: GitBranch,
    },
    {
      id: "cv-generator" as const,
      label: "CV",
      icon: FileText,
    },
    {
      id: "personal-info" as const,
      label: "Profile",
      icon: PersonStanding,
    },
    {
      id: "job-applications" as const,
      label: "Apps",
      icon: FileCheck,
    },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-sidebar border-t border-sidebar-border z-50">
      <nav className="flex justify-around py-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <Button
              key={item.id}
              variant="ghost"
              className={cn(
                "flex flex-col items-center justify-center h-auto p-2 gap-1 min-w-0 flex-1",
                isActive
                  ? "text-sidebar-primary bg-sidebar-accent"
                  : "text-sidebar-foreground hover:text-sidebar-primary hover:bg-sidebar-accent/50"
              )}
              onClick={() => onTabChange(item.id)}
            >
              <Icon className="h-5 w-5" />
              <span className="text-xs font-medium truncate">{item.label}</span>
            </Button>
          );
        })}
      </nav>
    </div>
  );
}