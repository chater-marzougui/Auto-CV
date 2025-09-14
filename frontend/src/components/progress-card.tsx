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
  title?: string;
  disconnectOnClose?: boolean;
  isVisible: boolean;
  onClose: () => void;
  websocketUrl?: string;
  onComplete?: () => void;
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

const getTimelineItemIcon = (item: {
  alertType?: 'success' | 'warning' | 'error' | 'info';
  step?: string;
}) => {
  if (item.alertType) {
    return getAlertIcon(item.alertType);
  }
  return stepIcons[item.step || ''] || Clock;
};

const getTimelineItemColor = (item: {
  alertType?: 'success' | 'warning' | 'error' | 'info';
  step?: string;
  isCompleted: boolean;
}) => {
  if (item.alertType) {
    return getAlertColor(item.alertType);
  }
  
  // Color based on completion status
  if (item.isCompleted) {
    return 'text-green-600 bg-green-50 border-green-200';
  } else if (item.step === 'error') {
    return 'text-red-500 bg-red-50 border-red-200';
  } else if (item.step === 'warning') {
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  } else {
    return 'text-blue-500 bg-blue-50 border-blue-200';
  }
};

export const ProgressCard: React.FC<ProgressCardProps> = ({ 
  title,
  disconnectOnClose = true,
  isVisible, 
  onClose, 
  websocketUrl = `ws://localhost:5000/ws/${Date.now()}` ,
  onComplete

}) => {
  const [showTimeline, setShowTimeline] = useState(true);
  
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

  // Merge history and alerts into a unified timeline
  const timeline = React.useMemo(() => {
    const timelineItems: Array<{
      id: string;
      type: 'history' | 'alert';
      timestamp: string;
      message: string;
      step?: string;
      repo_name?: string;
      current?: number;
      total?: number;
      alertType?: 'success' | 'warning' | 'error' | 'info';
      isCompleted: boolean;
    }> = [];
    
    // Add history items
    history.forEach((item, index) => {
      timelineItems.push({
        id: `history-${item.timestamp}-${index}`,
        type: 'history',
        timestamp: item.timestamp,
        message: item.message,
        step: item.step,
        repo_name: item.repo_name,
        current: item.current,
        total: item.total,
        alertType: item.alert?.type,
        isCompleted: index < history.length - 1 || (item.step === 'completed' || item.step === 'finished')
      });
    });
    
    // Add alert items
    alerts.forEach(alert => {
      timelineItems.push({
        id: alert.id,
        type: 'alert',
        timestamp: alert.timestamp,
        message: alert.message,
        alertType: alert.type,
        isCompleted: true
      });
    });
    
    // Sort by timestamp (newest first)
    if (onComplete && history.some(h => h.step === 'completed' || h.step === 'finished')) {
      onComplete();
    }
    
    return timelineItems.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [history, alerts]);

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

        {/* Unified Timeline */}
        {timeline.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm flex items-center gap-2">
                <GitBranch className="h-4 w-4" />
                Activity Timeline
                <Badge variant="outline" className="text-xs">
                  {timeline.length}
                </Badge>
              </h4>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowTimeline(!showTimeline)}
                  className="h-7 px-2 text-xs"
                >
                  {showTimeline ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearAll}
                  className="h-7 px-2 text-xs"
                >
                  Clear
                </Button>
              </div>
            </div>
            
            {showTimeline && (
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {timeline.slice(0, 30).map((item) => {
                  const ItemIcon = getTimelineItemIcon(item);
                  const isProcessing = ['processing', 'ai_processing', 'embedding', 'saving', 'embeddings'].includes(item.step || '');
                  
                  return (
                    <div
                      key={item.id}
                      className={`flex items-start gap-3 p-3 rounded-lg border text-xs ${getTimelineItemColor(item)}`}
                    >
                      <div className="flex-shrink-0 mt-0.5">
                        <ItemIcon className={`h-4 w-4 ${isProcessing ? 'animate-spin' : ''}`} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="font-medium mb-1 break-words">{item.message}</div>
                        
                        {item.repo_name && (
                          <div className="text-xs opacity-75 mb-1">
                            <span className="font-mono">{item.repo_name}</span>
                          </div>
                        )}
                        
                        <div className="flex items-center justify-between">
                          <div className="text-xs opacity-70">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </div>
                          
                          {(item.total || 0) > 0 && (
                            <Badge variant="outline" className="text-xs ml-2">
                              {item.current}/{item.total}
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      {item.type === 'alert' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeAlert(item.id)}
                          className="h-5 w-5 p-0 opacity-50 hover:opacity-100 flex-shrink-0"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      )}
                      
                      {item.isCompleted && item.type === 'history' && (
                        <div className="flex-shrink-0 mt-0.5">
                          <CheckCircle className="h-3 w-3 text-green-500" />
                        </div>
                      )}
                    </div>
                  );
                })}
                
                {timeline.length === 0 && (
                  <div className="text-center text-muted-foreground text-xs py-6">
                    <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    No activity yet
                  </div>
                )}
              </div>
            )}
          </div>
        )}

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