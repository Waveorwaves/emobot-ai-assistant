import React, { useState } from 'react';
import { Save, X } from 'lucide-react';
import { reasoningApi } from '../utils/api';
import { ReasoningResponse } from '../types';

interface CorrectionInterfaceProps {
  reasoning: ReasoningResponse;
  onCorrectionsSubmitted: () => void;
  onCancel: () => void;
}

const CorrectionInterface: React.FC<CorrectionInterfaceProps> = ({
  reasoning,
  onCorrectionsSubmitted,
  onCancel
}) => {
  const [corrections, setCorrections] = useState<Record<number, string>>({});
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStepCorrection = (stepNumber: number, correction: string) => {
    if (correction.trim()) {
      setCorrections(prev => ({
        ...prev,
        [stepNumber]: correction.trim()
      }));
    } else {
      const newCorrections = { ...corrections };
      delete newCorrections[stepNumber];
      setCorrections(newCorrections);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await reasoningApi.submitCorrections({
        interaction_id: reasoning.interaction_id,
        step_corrections: corrections,
        satisfaction_rating: 4, // Default rating when only corrections are submitted
        feedback: feedback.trim() || undefined
      });

      onCorrectionsSubmitted();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit corrections');
    } finally {
      setIsSubmitting(false);
    }
  };


  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">
            Correct AI Reasoning
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <p className="mt-1 text-sm text-gray-600">
          Help improve the AI by correcting any reasoning steps that could be better. You can rate the overall quality above.
        </p>
      </div>

      {/* Correction Form */}
      <div className="px-6 py-4 space-y-6">
        {/* Step Corrections */}
        <div>
          <h3 className="text-md font-medium text-gray-900 mb-4">
            Step-by-Step Corrections:
          </h3>
          
          <div className="space-y-4">
            {reasoning.reasoning_steps.map((step) => (
              <div key={step.step} className="border border-gray-200 rounded-lg p-4">
                <div className="mb-3">
                  <div className="flex items-center mb-2">
                    <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2.5 py-0.5 rounded-full mr-3">
                      Step {step.step}
                    </span>
                    <h4 className="font-medium text-gray-900">
                      {step.action}
                    </h4>
                  </div>
                  <p className="text-gray-600 ml-20 mb-3">
                    {step.reasoning}
                  </p>
                </div>
                
                <div className="ml-20">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Correction (leave empty if step is correct):
                  </label>
                  <textarea
                    rows={2}
                    placeholder="How should this step be improved?"
                    value={corrections[step.step] || ''}
                    onChange={(e) => handleStepCorrection(step.step, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>


        {/* General Feedback */}
        <div>
          <label htmlFor="feedback" className="block text-sm font-medium text-gray-700 mb-2">
            Additional Feedback (optional):
          </label>
          <textarea
            id="feedback"
            rows={3}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Any other thoughts on how the AI could reason better?"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Cancel
          </button>
          
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Submitting...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Submit Corrections
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CorrectionInterface;