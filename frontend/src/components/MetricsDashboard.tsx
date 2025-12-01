import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { TrendingUp, Users, Target, Award } from 'lucide-react';
import { reasoningApi } from '../utils/api';
import { MetricsData } from '../types';

const MetricsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setIsLoading(true);
        const data = await reasoningApi.getMetrics();
        setMetrics(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load metrics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-red-600">
          <p>Error loading metrics: {error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-2 px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">No metrics data available</p>
      </div>
    );
  }

  const StatCard = ({
    title,
    value,
    icon: Icon,
    color = 'blue',
    description
  }: {
    title: string;
    value: string | number;
    icon: any;
    color?: string;
    description?: string;
  }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {description && (
            <p className="text-sm text-gray-500 mt-1">{description}</p>
          )}
        </div>
        <div className={`p-3 rounded-full bg-${color}-100`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
        <p className="text-gray-600">Track AI reasoning performance and learning progress</p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Interactions"
          value={metrics.learning_progress.total_interactions}
          icon={Users}
          color="blue"
          description="Reasoning requests processed"
        />

        <StatCard
          title="Avg Satisfaction"
          value={`${metrics.user_satisfaction.average.toFixed(1)}/5`}
          icon={Award}
          color="green"
          description={`Trend: ${metrics.user_satisfaction.trend}`}
        />

        <StatCard
          title="Learning Quality"
          value={`${(metrics.learning_progress.learning_data_quality * 100).toFixed(0)}%`}
          icon={Target}
          color="sky"
          description="Interactions with feedback"
        />

        <StatCard
          title="Correction Rate"
          value={`${(metrics.correction_stats.correction_rate * 100).toFixed(1)}%`}
          icon={TrendingUp}
          color="orange"
          description="Interactions needing correction"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Accuracy Trends Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Accuracy & Satisfaction Trends
          </h3>
          {metrics.accuracy_trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics.accuracy_trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value: any, name: string) => [
                    typeof value === 'number' ? value.toFixed(2) : value,
                    name === 'accuracy' ? 'Accuracy' : 'Satisfaction'
                  ]}
                />
                <Line
                  type="monotone"
                  dataKey="accuracy"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  name="accuracy"
                />
                <Line
                  type="monotone"
                  dataKey="satisfaction"
                  stroke="#10B981"
                  strokeWidth={2}
                  name="satisfaction"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No trend data available yet
            </div>
          )}
        </div>

        {/* Interactions Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Daily Interactions
          </h3>
          {metrics.accuracy_trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metrics.accuracy_trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value: any) => [value, 'Interactions']}
                />
                <Bar dataKey="interactions" fill="#0ea5e9" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No interaction data available yet
            </div>
          )}
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Detailed Statistics
          </h3>
        </div>

        <div className="px-6 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Correction Statistics</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Corrections:</span>
                  <span className="font-medium">{metrics.correction_stats.total_corrections}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg per Interaction:</span>
                  <span className="font-medium">
                    {metrics.correction_stats.avg_corrections_per_interaction.toFixed(1)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Correction Rate:</span>
                  <span className="font-medium">
                    {(metrics.correction_stats.correction_rate * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Learning Progress</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Interactions:</span>
                  <span className="font-medium">{metrics.learning_progress.total_interactions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">With Feedback:</span>
                  <span className="font-medium">{metrics.learning_progress.interactions_with_feedback}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Estimated Improvement:</span>
                  <span className="font-medium">
                    {(metrics.learning_progress.estimated_improvement * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Data Quality</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Learning Data Quality:</span>
                  <span className="font-medium">
                    {(metrics.learning_progress.learning_data_quality * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">User Satisfaction:</span>
                  <span className="font-medium">
                    {metrics.user_satisfaction.average.toFixed(1)}/5
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Satisfaction Trend:</span>
                  <span className="font-medium capitalize">{metrics.user_satisfaction.trend}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;