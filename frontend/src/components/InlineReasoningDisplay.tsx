import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, Wrench, Eye, CheckCircle, XCircle } from 'lucide-react';
import { ReasoningStep } from '../context/DataContext';

interface InlineReasoningDisplayProps {
  steps: ReasoningStep[];
  defaultExpanded?: boolean;
}

const InlineReasoningDisplay: React.FC<InlineReasoningDisplayProps> = ({
  steps,
  defaultExpanded = false
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!steps || steps.length === 0) {
    return null;
  }

  const getStepIcon = (type: string) => {
    switch (type) {
      case 'thought':
        return <Brain className="w-4 h-4 text-purple-500" />;
      case 'tool_call':
        return <Wrench className="w-4 h-4 text-blue-500" />;
      case 'observation':
        return <Eye className="w-4 h-4 text-green-500" />;
      case 'final_answer':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <CheckCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStepColor = (type: string) => {
    switch (type) {
      case 'thought':
        return 'bg-purple-50 border-purple-200';
      case 'tool_call':
        return 'bg-blue-50 border-blue-200';
      case 'observation':
        return 'bg-green-50 border-green-200';
      case 'final_answer':
        return 'bg-green-100 border-green-300';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getStepLabel = (type: string) => {
    switch (type) {
      case 'thought':
        return 'Thinking';
      case 'tool_call':
        return 'Action';
      case 'observation':
        return 'Observation';
      case 'final_answer':
        return 'Answer';
      case 'query_received':
        return 'Received';
      case 'error':
        return 'Error';
      default:
        return type;
    }
  };

  // Filter out query_received and final_answer_marker steps for cleaner display
  const displaySteps = steps.filter(
    step => step.type !== 'query_received' && step.type !== 'final_answer_marker'
  );

  return (
    <div className="mt-2 rounded-md overflow-hidden border border-gray-600 bg-[#2a2a2a]">
      {/* Toggle Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 flex items-center justify-between text-sm hover:bg-[#333] transition-colors"
      >
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-blue-400" />
          <span className="text-gray-300 font-medium">
            Reasoning Process ({displaySteps.length} steps)
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {/* Expandable Steps */}
      {isExpanded && (
        <div className="border-t border-gray-600 bg-[#1e1e1e]">
          <div className="p-3 space-y-2 max-h-96 overflow-y-auto">
            {displaySteps.map((step, index) => (
              <div
                key={index}
                className={`p-2 rounded border ${getStepColor(step.type)} transition-all`}
              >
                <div className="flex items-start gap-2">
                  <div className="flex-shrink-0 mt-0.5">
                    {getStepIcon(step.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
                        {getStepLabel(step.type)}
                      </span>
                      {step.confidence !== undefined && (
                        <span className="text-xs text-gray-500">
                          ({Math.round(step.confidence * 100)}%)
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed break-words">
                      {step.action && step.action !== step.reasoning && (
                        <span className="font-medium">{step.action}: </span>
                      )}
                      {step.reasoning}
                    </p>
                    {step.tool_name && (
                      <div className="mt-1 text-xs text-gray-600">
                        Tool: <span className="font-mono">{step.tool_name}</span>
                      </div>
                    )}
                    {step.parameters && (
                      <div className="mt-1 text-xs text-gray-600 font-mono overflow-auto">
                        {typeof step.parameters === 'string'
                          ? step.parameters
                          : JSON.stringify(step.parameters)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default InlineReasoningDisplay;
