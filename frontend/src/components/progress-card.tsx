import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  Loader2, 
  ChevronDown,
  X,
  Clock,
  GitBranch,
  Zap
} from 'lucide-react';
import { useProgressWebSocket } from '@/hooks/use-websocket';

interface ProgressCardProps {
  title?: string;
  disconnectOnClose?: boolean;
  isVisible: boolean;
  onClose: () => void;
  websocketUrl?: string;
}

const stepIcons: Record<string, React.ElementType> = {
  initialization: Clock,
  discovery: GitBranch,
  processing: Loader2,
  skipping: ChevronDown,
  readme: CheckCircle,
  readme_missing: AlertCircle,
  file_tree: GitBranch,
  ai_processing: Zap,
  readme_quality: AlertCircle,
  embedding: CheckCircle,
  repo_completed: CheckCircle,
  saving: CheckCircle,
  embeddings: Zap,
  completed: CheckCircle,
  error: XCircle,
  warning: AlertCircle
};

export const ProgressCard: React.FC<ProgressCardProps> = ({ 
  title,
  disconnectOnClose = true,
  isVisible, 
  onClose, 
  websocketUrl = `ws://localhost:5000/ws/${Date.now()}`

}) => {
  const {
    isConnected,
    currentMessage,
    currentStep,
    progress,
    currentRepo,
    connect,
    disconnect,
    clearHistory,
    clearAlerts
  } = useProgressWebSocket(websocketUrl);

  const clearAll = () => {
    clearHistory();
    clearAlerts();
  };

  React.useEffect(() => {
    if (isVisible && !isConnected) {
      connect();
    } else if (!isVisible && isConnected && disconnectOnClose) {
      disconnect();
    }
  }, [isVisible, isConnected, connect, disconnect]);

  if (!isVisible) return null;

  const StepIcon = stepIcons[currentStep] || Clock;
  const isProcessing = ['processing', 'ai_processing', 'embedding', 'saving', 'embeddings'].includes(currentStep);

  return (
    <Card className="fixed bottom-4 right-4 w-[420px] max-h-[85vh] shadow-xl border-2 z-50 bg-background">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold flex items-center gap-3">
            <div className={`p-2 rounded-full ${isConnected ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
              <StepIcon className={`h-5 w-5 ${isProcessing ? 'animate-spin' : ''}`} />
            </div>
            <span>{title ?? "Scraping Progress"}</span>
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Connection Status:</span>
            <Badge variant={isConnected ? 'default' : 'secondary'} className="text-xs">
              {isConnected ? 'Connected' : 'Disconnected'}
            </Badge>
          </div>
          
          {progress > 0 && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Overall Progress</span>
                <span className="font-medium">{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6 max-h-[60vh] overflow-y-auto">
        {/* Current Status */}
        <div className="space-y-3">
          <div className="p-4 bg-muted rounded-lg border">
            <div className="font-medium text-sm mb-2">{currentMessage}</div>
            {currentRepo && (
              <div className="text-xs text-muted-foreground mb-2">
                Repository: <span className="font-mono">{currentRepo}</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-muted-foreground">Current Step:</span>
              <Badge variant={isConnected ? 'default' : 'secondary'} className="text-xs">
                {currentStep?.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
          </div>
        </div>

        {/* Connection Controls */}
        <div className="flex gap-2 pt-4 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={isConnected ? disconnect : connect}
            className="text-xs flex items-center gap-1"
          >
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`} />
            {isConnected ? 'Disconnect' : 'Connect'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={clearAll}
            className="text-xs"
          >
            Clear All
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};