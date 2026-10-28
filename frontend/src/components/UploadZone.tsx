import React, { useState, useRef } from 'react';
import { Upload, FileText, Database, Code2, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react';
import { NeumorphicCard } from './NeumorphicCard';

interface UploadZoneProps {
  onFileSelected: (file: File) => void;
  onLoadDemo: () => void;
  isLoading: boolean;
  error?: string | null;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFileSelected,
  onLoadDemo,
  isLoading,
  error
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <div className="w-full space-y-4">
      <NeumorphicCard
        variant={isDragOver ? 'inset' : 'raised'}
        className={`relative border-2 border-dashed transition-all cursor-pointer ${
          isDragOver
            ? 'border-indigo-500 bg-indigo-50/20 dark:bg-indigo-950/20 scale-[0.99]'
            : 'border-slate-300 dark:border-slate-700/60 hover:border-indigo-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.csv,.json"
          className="hidden"
          onChange={handleFileChange}
          disabled={isLoading}
        />

        <div className="flex flex-col items-center justify-center py-10 px-4 text-center">
          <div className="w-16 h-16 rounded-2xl neu-button flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4">
            {isLoading ? (
              <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Upload className="w-8 h-8" />
            )}
          </div>

          <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100 mb-1">
            {isLoading ? 'Parsing and validating conversation...' : 'Drag and drop your chat export here'}
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mb-6">
            Upload your WhatsApp (.txt), CSV, or JSON conversation export. All processing occurs locally in memory.
          </p>

          <button
            type="button"
            className="neu-button px-6 py-2.5 rounded-xl text-sm font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-2"
          >
            <span>Browse from computer</span>
          </button>
        </div>
      </NeumorphicCard>

      {/* Supported formats & Demo trigger */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-2">
        <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-emerald-500" />
            <span>WhatsApp (.txt)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-blue-500" />
            <span>CSV (Tabular)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Code2 className="w-3.5 h-3.5 text-purple-500" />
            <span>JSON (Structured)</span>
          </div>
        </div>

        <button
          type="button"
          onClick={onLoadDemo}
          disabled={isLoading}
          className="neu-button px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 flex items-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span>Load sample demo chat</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl neu-inset border border-rose-500/30 flex items-start gap-3 text-rose-600 dark:text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">File Parsing Error: </span>
            <span>{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};
