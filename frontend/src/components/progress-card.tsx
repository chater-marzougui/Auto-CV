import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Info, 
  Loader2, 
  ChevronDown, 
  ChevronUp,
  X,
  Clock,
  GitBranch,
  Zap
} from 'lucide-react';
import { useProgressWebSocket } from '@/hooks/use-websocket';

interface ProgressCardProps {
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

const getAlertIcon = (type: string) => {
  switch (type) {
    case 'success': return CheckCircle;
    case 'warning': return AlertCircle;
    case 'error': return XCircle;
    case 'info': return Info;
    default: return Info;
  }
};

const getAlertColor = (type: string) => {
  switch (type) {
    case 'success': return 'text-green-500 bg-green-50 border-green-200';
    case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'error': return 'text-red-500 bg-red-50 border-red-200';
    case 'info': return 'text-blue-500 bg-blue-50 border-blue-200';
    default: return 'text-gray-500 bg-gray-50 border-gray-200';
  }
};

export const ProgressCard: React.FC<ProgressCardProps> = ({ 
  isVisible, 
  onClose, 
  websocketUrl = `ws://localhost:5000/ws/${Date.now()}` 
}) => {
  const [showHistory, setShowHistory] = useState(false);
  const [showAlerts, setShowAlerts] = useState(true);
  
  const {
    isConnected,
    currentMessage,
    currentStep,
    progress,
    currentRepo,
    history,
    alerts,
    connect,
    disconnect,
    clearHistory,
    clearAlerts,
    removeAlert
  } = useProgressWebSocket(websocketUrl);

  React.useEffect(() => {
    if (isVisible && !isConnected) {
      connect();
    } else if (!isVisible && isConnected) {
      disconnect();
    }
  }, [isVisible, isConnected, connect, disconnect]);

  if (!isVisible) return null;

  const StepIcon = stepIcons[currentStep] || Clock;
  const isProcessing = ['processing', 'ai_processing', 'embedding', 'saving', 'embeddings'].includes(currentStep);

  return (
    <Card className="fixed bottom-4 right-4 w-96 max-h-[80vh] shadow-xl border-2 z-50 bg-background">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <div className={`p-1 rounded-full ${isConnected ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
              <StepIcon className={`h-4 w-4 ${isProcessing ? 'animate-spin' : ''}`} />
            </div>
            Scraping Progress
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
        
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Status:</span>
            <Badge variant={isConnected ? 'default' : 'secondary'}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Badge>
          </div>
          
          {progress > 0 && (
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4 max-h-[50vh] overflow-y-auto">
        {/* Current Status */}
        <div className="space-y-2">
          <div className="p-3 bg-muted rounded-lg">
            <div className="font-medium text-sm">{currentMessage}</div>
            {currentRepo && (
              <div className="text-xs text-muted-foreground mt-1">
                Repository: {currentRepo}
              </div>
            )}
          </div>
        </div>

        {/* Alerts Section */}
        {alerts.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm">Recent Alerts</h4>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAlerts(!showAlerts)}
                  className="h-6 px-2 text-xs"
                >
                  {showAlerts ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearAlerts}
                  className="h-6 px-2 text-xs"
                >
                  Clear
                </Button>
              </div>
            </div>
            
            {showAlerts && (
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {alerts.slice(-5).reverse().map((alert) => {
                  const AlertIcon = getAlertIcon(alert.type);
                  return (
                    <div
                      key={alert.id}
                      className={`flex items-start gap-2 p-2 rounded border text-xs ${getAlertColor(alert.type)}`}
                    >
                      <AlertIcon className="h-3 w-3 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <div>{alert.message}</div>
                        <div className="text-xs opacity-70 mt-1">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAlert(alert.id)}
                        className="h-4 w-4 p-0 opacity-50 hover:opacity-100"
                      >
                        <X className="h-2 w-2" />
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* History Section */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-sm">Process History</h4>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(!showHistory)}
                className="h-6 px-2 text-xs"
              >
                {showHistory ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearHistory}
                className="h-6 px-2 text-xs"
              >
                Clear
              </Button>
            </div>
          </div>
          
          {showHistory && (
            <div className="space-y-1 max-h-40 overflow-y-auto">
              {history.slice(-20).reverse().map((item, index) => {
                const ItemIcon = stepIcons[item.step] || Clock;
                const isItemProcessing = ['processing', 'ai_processing', 'embedding', 'saving', 'embeddings'].includes(item.step);
                
                return (
                  <div
                    key={`${item.timestamp}-${index}`}
                    className="flex items-start gap-2 p-2 rounded bg-muted/50 text-xs"
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <ItemIcon className={`h-3 w-3 text-muted-foreground ${isItemProcessing ? 'animate-spin' : ''}`} />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{item.message}</div>
                      {item.repo_name && (
                        <div className="text-muted-foreground">
                          {item.repo_name}
                        </div>
                      )}
                      <div className="text-muted-foreground opacity-70">
                        {new Date(item.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                    {item.total > 0 && (
                      <Badge variant="outline" className="text-xs">
                        {item.current}/{item.total}
                      </Badge>
                    )}
                  </div>
                );
              })}
              
              {history.length === 0 && (
                <div className="text-center text-muted-foreground text-xs py-4">
                  No history available
                </div>
              )}
            </div>
          )}
        </div>

        {/* Connection Controls */}
        <div className="flex gap-2 pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={isConnected ? disconnect : connect}
            className="text-xs"
          >
            {isConnected ? 'Disconnect' : 'Connect'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              clearHistory();
              clearAlerts();
            }}
            className="text-xs"
          >
            Clear All
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};