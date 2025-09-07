import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { FileText, GitBranch, Briefcase, Github } from "lucide-react"

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: "job-analysis" | "projects" | "cv-generator") => void
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const menuItems = [
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
      description: "Generate CV & cover letter",
    },
  ]

  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-2">
          <Github className="h-8 w-8 text-sidebar-primary" />
          <div>
            <h1 className="font-heading font-bold text-lg text-sidebar-foreground">Auto-CV</h1>
            <p className="text-sm text-sidebar-foreground/60">AI-powered CV generator</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <Button
              key={item.id}
              variant={activeTab === item.id ? "default" : "ghost"}
              className={cn(
                "w-full justify-start gap-3 h-auto p-3",
                activeTab === item.id
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              )}
              onClick={() => onTabChange(item.id)}
            >
              <Icon className="h-5 w-5" />
              <div className="text-left">
                <div className="font-medium">{item.label}</div>
                <div className="text-xs opacity-70">{item.description}</div>
              </div>
            </Button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <p className="text-xs text-sidebar-foreground/60 text-center">Built with AI & GitHub API</p>
      </div>
    </div>
  )
}
