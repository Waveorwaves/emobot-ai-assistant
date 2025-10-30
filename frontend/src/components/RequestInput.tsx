import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { reasoningApi } from '../utils/api';
import { ReasoningResponse } from '../types';

interface RequestInputProps {
  onReasoningComplete: (reasoning: ReasoningResponse, userRequest: string) => void;
}

const RequestInput: React.FC<RequestInputProps> = ({ onReasoningComplete }) => {
  const [request, setRequest] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!request.trim()) {
      setError('Please enter a request');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await reasoningApi.submitRequest({
        user_request: request.trim(),
        context_data: {
          timestamp: new Date().toISOString(),
          source: 'web_interface'
        }
      });

      onReasoningComplete(response, request.trim());
      setRequest(''); // Clear input after successful submission
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process request');
    } finally {
      setIsLoading(false);
    }
  };

  const exampleRequests = [
    "Help me plan my morning routine to be more productive",
    "How should I approach learning a new programming language?",
    "What's the best way to organize my work priorities?",
    "Help me create a budget for my monthly expenses"
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Request AI Reasoning
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="request" className="block text-sm font-medium text-gray-700 mb-2">
            What would you like help reasoning through?
          </label>
          <textarea
            id="request"
            rows={4}
            value={request}
            onChange={(e) => setRequest(e.target.value)}
            placeholder="Describe what you need help with..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
        </div>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
            {error}
          </div>
        )}

        <div className="flex justify-between items-center">
          <button
            type="submit"
            disabled={isLoading || !request.trim()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Get AI Reasoning
              </>
            )}
          </button>

          <span className="text-sm text-gray-500">
            Response time: ~2-5 seconds
          </span>
        </div>
      </form>

      {/* Example Requests */}
      <div className="mt-6 border-t pt-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          Example Requests:
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {exampleRequests.map((example, index) => (
            <button
              key={index}
              onClick={() => setRequest(example)}
              className="text-left p-2 text-sm text-blue-600 hover:bg-blue-50 rounded border border-gray-200 hover:border-blue-300 transition-colors"
              disabled={isLoading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RequestInput;