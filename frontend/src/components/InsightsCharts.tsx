import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { ConversationStats } from '../types';
import { NeumorphicCard } from './NeumorphicCard';
import { Clock, MessageSquare, Flame, CheckCircle } from 'lucide-react';

interface InsightsChartsProps {
  stats: ConversationStats;
  sender: string;
  recipient: string;
}

export const InsightsCharts: React.FC<InsightsChartsProps> = ({
  stats,
  sender,
  recipient
}) => {
  return (
    <div className="space-y-6">
      {/* 4 Summary Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span>Historical Reply Rate</span>
            <CheckCircle className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
            {stats.historical_reply_rate !== null && stats.historical_reply_rate !== undefined
              ? `${Math.round(stats.historical_reply_rate * 100)}%`
              : 'N/A'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Recipient turn reply rate
          </p>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span>Median Response Time</span>
            <Clock className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
            {stats.median_response_time_minutes !== null && stats.median_response_time_minutes !== undefined
              ? stats.median_response_time_minutes < 60
                ? `${Math.round(stats.median_response_time_minutes)} min`
                : `${(stats.median_response_time_minutes / 60).toFixed(1)} hrs`
              : 'N/A'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Avg: {stats.avg_response_time_minutes ? `${Math.round(stats.avg_response_time_minutes)} min` : 'N/A'}
          </p>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span>Message Balance</span>
            <MessageSquare className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
            {Math.round(stats.sender_ratio * 100)}% / {Math.round(stats.recipient_ratio * 100)}%
          </div>
          <p className="text-[11px] text-slate-400 mt-1 truncate">
            {sender} vs {recipient}
          </p>
        </NeumorphicCard>

        <NeumorphicCard variant="raised-sm" className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
            <span>Questions & Cues</span>
            <Flame className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-800 dark:text-slate-100">
            {stats.sender_question_count} asked
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            {stats.sender_emoji_count} emojis used
          </p>
        </NeumorphicCard>
      </div>

      {/* Chart 1: Hourly Activity (Area Chart) */}
      <NeumorphicCard className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
              Hourly Activity Distribution
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              When messages are typically exchanged throughout the 24-hour cycle
            </p>
          </div>
        </div>

        <div className="h-64 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stats.activity_by_hour}>
              <defs>
                <linearGradient id="colorSender" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.0}/>
                </linearGradient>
                <linearGradient id="colorRecip" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0d9488" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#0d9488" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="hour" tickFormatter={(h) => `${h}:00`} tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(val, name) => [
                  `${val} messages`,
                  name === 'sender_count' ? sender : recipient
                ]}
                labelFormatter={(h) => `Hour ${h}:00 - ${h}:59`}
                contentStyle={{
                  backgroundColor: 'rgba(23, 27, 38, 0.9)',
                  borderRadius: '12px',
                  border: 'none',
                  color: '#fff',
                  fontSize: '12px'
                }}
              />
              <Legend formatter={(v) => (v === 'sender_count' ? sender : recipient)} />
              <Area
                type="monotone"
                dataKey="sender_count"
                stroke="#6366f1"
                fillOpacity={1}
                fill="url(#colorSender)"
              />
              <Area
                type="monotone"
                dataKey="recipient_count"
                stroke="#0d9488"
                fillOpacity={1}
                fill="url(#colorRecip)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </NeumorphicCard>

      {/* Chart 2 & 3: Response Time Distribution & Day of Week in 2 Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Response Time Histogram */}
        <NeumorphicCard className="space-y-4">
          <div>
            <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
              Response Time Distribution
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              How quickly recipient historically responds
            </p>
          </div>

          <div className="h-60 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.response_time_distribution}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="bucket" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip
                  formatter={(val, name, item: any) => [
                    `${val} replies (${item.payload.percentage}%)`,
                    'Count'
                  ]}
                  contentStyle={{
                    backgroundColor: 'rgba(23, 27, 38, 0.9)',
                    borderRadius: '12px',
                    border: 'none',
                    color: '#fff',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="count" fill="#818cf8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </NeumorphicCard>

        {/* Day of Week Volume */}
        <NeumorphicCard className="space-y-4">
          <div>
            <h4 className="font-bold text-base text-slate-800 dark:text-slate-100">
              Day of Week Activity
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Total conversational volume by weekday
            </p>
          </div>

          <div className="h-60 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.activity_by_day}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => [`${val} messages`, 'Total Messages']}
                  contentStyle={{
                    backgroundColor: 'rgba(23, 27, 38, 0.9)',
                    borderRadius: '12px',
                    border: 'none',
                    color: '#fff',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="count" fill="#0d9488" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </NeumorphicCard>
      </div>
    </div>
  );
};
