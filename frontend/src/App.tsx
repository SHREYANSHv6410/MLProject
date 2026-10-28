import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, NavTab } from './components/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { AnalyzePage } from './pages/AnalyzePage';
import { ResultsPage } from './pages/ResultsPage';
import { InsightsPage } from './pages/InsightsPage';
import { ModelInfoPage } from './pages/ModelInfoPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { ChatPreviewResponse, PredictionResult, ConversationStats } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [serverStatus, setServerStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [modelReady, setModelReady] = useState<boolean>(false);
  const [historyCount, setHistoryCount] = useState<number>(0);

  // Active chat state
  const [preview, setPreview] = useState<ChatPreviewResponse | null>(null);
  const [selectedSender, setSelectedSender] = useState<string>('');
  const [selectedRecipient, setSelectedRecipient] = useState<string>('');
  const [targetMessageId, setTargetMessageId] = useState<string>('');
  const [replyHorizonHours, setReplyHorizonHours] = useState<number>(24);

  // Prediction and insights results
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [conversationStats, setConversationStats] = useState<ConversationStats | null>(null);

  // Loading and error states
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isPredicting, setIsPredicting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Initial health check
  useEffect(() => {
    const checkServer = async () => {
      try {
        const res = await api.getHealth();
        setServerStatus(res.status === 'healthy' ? 'online' : 'offline');
        setModelReady(res.model_loaded);
      } catch {
        setServerStatus('offline');
        setModelReady(false);
      }
    };
    checkServer();
    const interval = setInterval(checkServer, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleFileSelected = async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.previewChat(file);
      setPreview(data);
      if (data.default_sender) setSelectedSender(data.default_sender);
      if (data.default_recipient) setSelectedRecipient(data.default_recipient);
      if (data.default_target_message_id) setTargetMessageId(data.default_target_message_id);

      setActiveTab('analyze');

      // Pre-compute conversation stats in background
      if (data.default_sender && data.default_recipient) {
        api.analyzeChat({
          messages: data.preview_messages,
          sender: data.default_sender,
          recipient: data.default_recipient,
          reply_horizon_hours: replyHorizonHours
        }).then(setConversationStats).catch(() => {});
      }
    } catch (err: any) {
      setError(err.message || 'Failed to parse chat export.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadDemo = () => {
    // Construct realistic multi-turn sample chat
    const sampleChatTxt = `15/01/2024, 09:15 - Alex Chen: Hey Sarah, good morning!
15/01/2024, 09:16 - Sarah Miller: Good morning Alex! Ready for the sprint review today?
15/01/2024, 09:18 - Alex Chen: Yes! I've updated the deck. Can you review slides 4 and 5 when you have a moment? 👍
15/01/2024, 09:25 - Sarah Miller: On it right now.
15/01/2024, 09:38 - Sarah Miller: The customer retention slide looks solid. Maybe clarify the Q4 cohort graph?
15/01/2024, 09:42 - Alex Chen: Great catch, adjusting the axis labels now.
15/01/2024, 11:30 - Alex Chen: Are we still on for our 1:1 at 2 PM?
15/01/2024, 11:34 - Sarah Miller: Yes absolutely, let's meet in Room B.
15/01/2024, 14:45 - Alex Chen: Thanks for the feedback during the 1:1!
15/01/2024, 14:48 - Sarah Miller: Anytime! Keep up the momentum.
15/01/2024, 17:15 - Alex Chen: Hey Sarah, quick question before you sign off: did client approve the revised SLA terms?`;

    const blob = new Blob([sampleChatTxt], { type: 'text/plain' });
    const demoFile = new File([blob], 'whatsapp_demo_chat.txt', { type: 'text/plain' });
    handleFileSelected(demoFile);
  };

  const handleRunPrediction = async () => {
    if (!preview || !targetMessageId || !selectedSender || !selectedRecipient) return;

    setIsPredicting(true);
    setError(null);

    try {
      // 1. Predict
      const pred = await api.predictReply({
        messages: preview.preview_messages,
        sender: selectedSender,
        recipient: selectedRecipient,
        target_message_id: targetMessageId,
        reply_horizon_hours: replyHorizonHours
      });
      setPredictionResult(pred);

      // 2. Fetch full conversation stats
      const stats = await api.analyzeChat({
        messages: preview.preview_messages,
        sender: selectedSender,
        recipient: selectedRecipient,
        reply_horizon_hours: replyHorizonHours
      });
      setConversationStats(stats);

      setActiveTab('results');
    } catch (err: any) {
      setError(err.message || 'Failed to generate prediction. Ensure the ML model is trained.');
    } finally {
      setIsPredicting(false);
    }
  };

  const handleResetConversation = () => {
    setPreview(null);
    setPredictionResult(null);
    setConversationStats(null);
    setSelectedSender('');
    setSelectedRecipient('');
    setTargetMessageId('');
    setActiveTab('analyze');
  };

  return (
    <div className="min-h-screen flex flex-col bg-neu-bg-light dark:bg-neu-bg-dark text-slate-800 dark:text-slate-100 transition-colors">
      <Navbar serverStatus={serverStatus} modelReady={modelReady} />

      <div className="flex-1 max-w-7xl w-full mx-auto flex flex-col md:flex-row gap-4 p-4 sm:p-6">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          hasActiveConversation={!!preview}
          hasPrediction={!!predictionResult}
        />

        <main className="flex-1 min-w-0">
          {error && (
            <div className="mb-6 p-4 rounded-xl neu-inset border border-rose-500/30 text-rose-600 dark:text-rose-400 text-sm">
              <span className="font-bold">Error: </span> {error}
            </div>
          )}

          {activeTab === 'overview' && (
            <OverviewPage
              onFileSelected={handleFileSelected}
              onLoadDemo={handleLoadDemo}
              onNavigateToTab={setActiveTab}
              isLoading={isLoading}
              modelReady={modelReady}
              historyCount={historyCount}
            />
          )}

          {activeTab === 'analyze' && (
            <AnalyzePage
              preview={preview}
              onFileSelected={handleFileSelected}
              onLoadDemo={handleLoadDemo}
              onReset={handleResetConversation}
              selectedSender={selectedSender}
              setSelectedSender={setSelectedSender}
              selectedRecipient={selectedRecipient}
              setSelectedRecipient={setSelectedRecipient}
              targetMessageId={targetMessageId}
              setTargetMessageId={setTargetMessageId}
              replyHorizonHours={replyHorizonHours}
              setReplyHorizonHours={setReplyHorizonHours}
              onRunPrediction={handleRunPrediction}
              isLoading={isLoading}
              isPredicting={isPredicting}
              error={error}
            />
          )}

          {activeTab === 'results' && predictionResult && (
            <ResultsPage
              result={predictionResult}
              stats={conversationStats}
              onNavigateToTab={setActiveTab}
              onSelectAnotherMessage={() => setActiveTab('analyze')}
              onUploadAnother={handleResetConversation}
            />
          )}

          {activeTab === 'insights' && (
            <InsightsPage
              stats={conversationStats}
              sender={selectedSender}
              recipient={selectedRecipient}
              onNavigateToTab={setActiveTab}
            />
          )}

          {activeTab === 'model' && <ModelInfoPage />}

          {activeTab === 'history' && <HistoryPage />}

          {activeTab === 'settings' && <SettingsPage />}
        </main>
      </div>

      <footer className="py-6 px-6 border-t border-slate-200/40 dark:border-slate-800/40 text-center text-xs text-slate-400 dark:text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>ReplySense © {new Date().getFullYear()} — Probabilistic Dialogue Analytics</span>
          <span>100% Client-Side Evaluation & Local Privacy Architecture</span>
        </div>
      </footer>
    </div>
  );
};
export default App;
