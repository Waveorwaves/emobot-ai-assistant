import React, { useState } from 'react';
import { Edit3, Clock, Target, TrendingUp, Star, Check } from 'lucide-react';
import { ReasoningResponse } from '../types';
import { reasoningApi } from '../utils/api';

interface ReasoningDisplayProps {
  reasoning: ReasoningResponse;
  userRequest: string;
  onRequestCorrections: () => void;
}

const ReasoningDisplay: React.FC<ReasoningDisplayProps> = ({ 
  reasoning, 
  userRequest,
  onRequestCorrections 
}) => {
  const [satisfactionRating, setSatisfactionRating] = useState<number>(0);
  const [isSubmittingRating, setIsSubmittingRating] = useState(false);
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const handleStarClick = async (rating: number) => {
    setSatisfactionRating(rating);
    setIsSubmittingRating(true);
    
    try {
      await reasoningApi.submitCorrections({
        interaction_id: reasoning.interaction_id,
        step_corrections: {},
        satisfaction_rating: rating
      });
      setRatingSubmitted(true);
    } catch (error) {
      console.error('Failed to submit rating:', error);
    } finally {
      setIsSubmittingRating(false);
    }
  };

  const StarRating = () => (
    <div className="flex items-center space-x-1">
      <span className="text-sm text-gray-600 mr-2">Rate this reasoning:</span>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => handleStarClick(star)}
          disabled={isSubmittingRating || ratingSubmitted}
          className="p-1 hover:scale-110 transition-transform disabled:cursor-not-allowed"
        >
          <Star
            className={`h-5 w-5 ${
              star <= satisfactionRating
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300 hover:text-yellow-400'
            }`}
          />
        </button>
      ))}
      {ratingSubmitted && (
        <div className="flex items-center ml-2 text-green-600">
          <Check className="h-4 w-4 mr-1" />
          <span className="text-sm">Thank you!</span>
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              AI Reasoning Analysis
            </h2>
            <div className="flex items-center mt-2 space-x-4 text-sm text-gray-500">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                {reasoning.processing_time.toFixed(2)}s
              </div>
              <div className="flex items-center">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(reasoning.overall_confidence)}`}>
                  {getConfidenceLabel(reasoning.overall_confidence)} ({(reasoning.overall_confidence * 100).toFixed(0)}%)
                </span>
              </div>
            </div>
          </div>
          
          <button
            onClick={onRequestCorrections}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Edit3 className="h-4 w-4 mr-2" />
            Make Corrections
          </button>
        </div>
        
        {/* Star Rating */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <StarRating />
        </div>
      </div>

      {/* User Question */}
      <div className="px-6 py-4 bg-blue-50 border-b border-blue-100">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          Your Question:
        </h3>
        <p className="text-blue-800 text-base leading-relaxed">
          "{userRequest}"
        </p>
      </div>

      {/* Reasoning Steps */}
      <div className="px-6 py-4">
        <h3 className="text-md font-medium text-gray-900 mb-4">
          Step-by-Step Reasoning:
        </h3>
        
        <div className="space-y-4">
          {reasoning.reasoning_steps.map((step) => (
            <div 
              key={step.step} 
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center">
                  <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full mr-3">
                    Step {step.step}
                  </span>
                  <h4 className="font-medium text-gray-900">
                    {step.action}
                  </h4>
                </div>
                
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(step.confidence)}`}>
                  {(step.confidence * 100).toFixed(0)}%
                </span>
              </div>
              
              <p className="text-gray-600 ml-20">
                {step.reasoning}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Final Plan */}
      {reasoning.final_plan && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center mb-3">
            <Target className="h-5 w-5 text-green-600 mr-2" />
            <h3 className="text-md font-medium text-gray-900">
              Recommended Plan:
            </h3>
          </div>
          
          <div className="bg-white rounded-md p-4 border border-gray-200">
            {reasoning.final_plan.summary && (
              <div className="mb-3">
                <h4 className="font-medium text-gray-900 mb-1">Summary:</h4>
                <p className="text-gray-600">{reasoning.final_plan.summary}</p>
              </div>
            )}
            
            {reasoning.final_plan.next_actions && Array.isArray(reasoning.final_plan.next_actions) && (
              <div className="mb-3">
                <h4 className="font-medium text-gray-900 mb-2">Next Actions:</h4>
                <ul className="space-y-1">
                  {reasoning.final_plan.next_actions.map((action: string, index: number) => (
                    <li key={index} className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      <span className="text-gray-600">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              {reasoning.final_plan.estimated_time && (
                <div>
                  <span className="font-medium text-gray-700">Estimated Time:</span>
                  <span className="text-gray-600 ml-2">{reasoning.final_plan.estimated_time}</span>
                </div>
              )}
              
              {reasoning.final_plan.expected_outcome && (
                <div>
                  <span className="font-medium text-gray-700">Expected Outcome:</span>
                  <span className="text-gray-600 ml-2">{reasoning.final_plan.expected_outcome}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReasoningDisplay;