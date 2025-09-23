import { Github } from "lucide-react";

export function MobileHeader() {
  return (
    <div className="bg-sidebar border-b border-sidebar-border p-4">
      <div className="flex items-center gap-2">
        <Github className="h-6 w-6 text-sidebar-primary" />
        <div>
          <h1 className="font-heading font-bold text-lg text-sidebar-foreground">
            Auto-CV
          </h1>
          <p className="text-xs text-sidebar-foreground/60">
            AI-powered CV generator
          </p>
        </div>
      </div>
    </div>
  );
}