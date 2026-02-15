/**
 * Export data to CSV file
 * 
 * @param {Array} data - Array of objects to export
 * @param {string} filename - Name of the file (without extension)
 * @param {Object} options - Export options
 * @param {Array} options.columns - Column definitions [{key: 'fieldName', label: 'Column Header', format: (val) => val}]
 * @param {boolean} options.includeHeaders - Include header row (default: true)
 */
export function exportToCSV(data, filename, options = {}) {
    const { columns, includeHeaders = true } = options;

    if (!data || data.length === 0) {
        console.warn('No data to export');
        return;
    }

    // Determine columns from first row if not provided
    const cols = columns || Object.keys(data[0]).map(key => ({
        key,
        label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    }));

    // Build CSV content
    const rows = [];

    // Header row
    if (includeHeaders) {
        rows.push(cols.map(col => escapeCSVValue(col.label)).join(','));
    }

    // Data rows
    data.forEach(row => {
        const values = cols.map(col => {
            let value = row[col.key];

            // Apply custom formatter if provided
            if (col.format && typeof col.format === 'function') {
                value = col.format(value, row);
            }

            return escapeCSVValue(value);
        });
        rows.push(values.join(','));
    });

    const csvContent = rows.join('\n');

    // Create and download file
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' }); // BOM for Excel compatibility
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `${filename}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Escape a value for CSV
 */
function escapeCSVValue(value) {
    if (value === null || value === undefined) {
        return '';
    }

    const stringValue = String(value);

    // If value contains comma, newline, or quote, wrap in quotes and escape quotes
    if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
    }

    return stringValue;
}

/**
 * Format number for CSV export
 */
export function formatNumberForExport(value) {
    if (typeof value === 'number') {
        return value.toLocaleString('en-US');
    }
    return value;
}

/**
 * Format date for CSV export (DD.MM.YYYY)
 */
export function formatDateForExport(value) {
    if (!value) return '';
    const date = new Date(value);
    if (isNaN(date.getTime())) return value;
    return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
    }).replace(/\//g, '.');
}

/**
 * Format percentage for CSV export
 */
export function formatPercentForExport(value) {
    if (typeof value === 'number') {
        return `${value.toFixed(1)}%`;
    }
    return value;
}

/**
 * Pre-defined column configurations for common exports
 */
export const CSV_COLUMNS = {
    users: [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Name' },
        { key: 'email', label: 'Email' },
        { key: 'team', label: 'Team' },
        { key: 'personal_quota', label: 'Quota', format: formatNumberForExport },
        { key: 'used_tokens', label: 'Used Tokens', format: formatNumberForExport },
        { key: 'usage_percent', label: 'Usage %', format: (val, row) => formatPercentForExport((row.used_tokens / row.personal_quota) * 100) },
        { key: 'created_at', label: 'Created', format: formatDateForExport },
    ],
    teams: [
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Team Name' },
        { key: 'description', label: 'Description' },
        { key: 'member_count', label: 'Members' },
        { key: 'total_quota', label: 'Total Quota', format: formatNumberForExport },
        { key: 'total_used', label: 'Total Used', format: formatNumberForExport },
        { key: 'created_at', label: 'Created', format: formatDateForExport },
    ],
    transfers: [
        { key: 'id', label: 'ID' },
        { key: 'from_user', label: 'From' },
        { key: 'to_user', label: 'To' },
        { key: 'amount', label: 'Amount', format: formatNumberForExport },
        { key: 'reason', label: 'Reason' },
        { key: 'created_at', label: 'Date', format: formatDateForExport },
    ],
};

/**
 * ExportButton Component
 */
export function ExportButton({ data, filename, columns, className = '' }) {
    const handleExport = () => {
        exportToCSV(data, filename, { columns });
    };

    return (
        <button
            onClick={handleExport}
            disabled={!data || data.length === 0}
            className={`inline-flex items-center px-3 py-2 text-sm font-medium text-gray-200 bg-gray-800 border border-gray-600 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
        >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export CSV
        </button>
    );
}
