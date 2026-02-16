// [AI GENERATED]
// Model: GitHub Copilot (Claude Opus 4.5)
// Logic: Safety Alert modal component for displaying detected violations before LLM requests.
// Why: Provides user-friendly UI for safety violations with options to edit, redact, or cancel.
// Root Cause: Safety pipeline detections need clear visual feedback to users.
// Context: Integrates with API to show violations and allow user actions.
// Model Suitability: Claude Opus 4.5 used for critical security interface.

import { AlertTriangle, Edit, Eraser, Info, Shield, X, XCircle } from 'lucide-react';

/**
 * Safety Alert Modal Component
 * 
 * Displays safety violations detected by the pipeline with options to:
 * - Edit the prompt to remove violations
 * - Auto-redact the violations
 * - Cancel the request
 * 
 * Props:
 * - violations: Array of violation objects
 * - onEdit: Callback when user chooses to edit
 * - onRedact: Callback when user chooses to auto-redact
 * - onCancel: Callback when user cancels
 */
export const SafetyAlert = ({ violations, onEdit, onRedact, onCancel }) => {
  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'high':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high':
        return <XCircle className="w-5 h-5" />;
      case 'medium':
        return <AlertTriangle className="w-5 h-5" />;
      case 'low':
        return <Info className="w-5 h-5" />;
      default:
        return <Shield className="w-5 h-5" />;
    }
  };

  const getCategoryBadgeColor = (category) => {
    switch (category?.toLowerCase()) {
      case 'pii':
        return 'bg-purple-100 text-purple-800';
      case 'secret':
        return 'bg-red-100 text-red-800';
      case 'injection':
        return 'bg-orange-100 text-orange-800';
      case 'blocklist':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const criticalCount = violations?.filter(v => v.severity === 'critical').length || 0;
  const highCount = violations?.filter(v => v.severity === 'high').length || 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-red-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Shield className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Safety Violation Detected
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {violations?.length || 0} issue{violations?.length !== 1 ? 's' : ''} found
                {criticalCount > 0 && ` (${criticalCount} critical)`}
                {highCount > 0 && !criticalCount && ` (${highCount} high)`}
              </p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Violations List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-3">
            {violations?.map((violation, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getSeverityColor(violation.severity)}`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getSeverityIcon(violation.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 text-xs font-medium rounded ${getCategoryBadgeColor(violation.category)}`}>
                        {violation.category?.toUpperCase()}
                      </span>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded ${getSeverityColor(violation.severity)}`}>
                        {violation.severity?.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round((violation.confidence || 0) * 100)}% confidence
                      </span>
                    </div>
                    
                    <p className="text-sm font-medium mb-1">
                      {violation.type?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                    </p>
                    
                    <p className="text-sm opacity-90 mb-2">
                      {violation.description}
                    </p>
                    
                    {violation.masked_value && (
                      <div className="bg-white bg-opacity-50 rounded px-2 py-1 text-xs font-mono">
                        Detected: {violation.masked_value}
                      </div>
                    )}
                    
                    {violation.provider && (
                      <div className="mt-1 text-xs">
                        Provider: <span className="font-medium">{violation.provider}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Warning Message */}
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <p className="font-medium mb-1">Security Policy Enforcement</p>
                <p>
                  Your prompt contains sensitive information that violates security policies.
                  Please review and remove the violations before proceeding, or use auto-redaction.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={onEdit}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Edit className="w-4 h-4" />
              Edit Prompt
            </button>
            
            <button
              onClick={onRedact}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              <Eraser className="w-4 h-4" />
              Auto-Redact
            </button>
            
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-3 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
          </div>
          
          <p className="text-xs text-gray-500 text-center mt-3">
            Auto-redact will replace sensitive information with [REDACTED] placeholders
          </p>
        </div>
      </div>
    </div>
  );
};

export default SafetyAlert;
