import { useIsMobile } from "@/hooks/use-mobile";
import { Github } from "lucide-react";

interface LocalHeaderProps {
  title: string;
  description: string;
}

const LocalHeader = ({ title, description }: Readonly<LocalHeaderProps>) => {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
        <div className="flex items-center gap-2 pr-5">
          <Github className="h-12 w-12 text-sidebar-primary" />
          <div>
            <h1 className="font-heading font-bold text-lg text-sidebar-foreground">
              Auto-CV
            </h1>
            <p className="text-xs text-sidebar-foreground/60">
              AI-powered CV generator
            </p>
          </div>
        </div>
    );
  }

  return (
    <div className="space-y-1">
      <h1 className="font-heading text-2xl font-bold text-foreground">
        {title}
      </h1>
      <p className="text-muted-foreground mt-1">{description}</p>
    </div>
  );
};

export default LocalHeader;
