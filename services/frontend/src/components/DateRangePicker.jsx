import { Calendar, ChevronDown } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

const RANGE_OPTIONS = [
    { label: 'Last 7 days', value: '7d', days: 7 },
    { label: 'Last 30 days', value: '30d', days: 30 },
    { label: 'This month', value: 'month', days: 0 },
    { label: 'This year', value: 'year', days: 0 },
    { label: 'Last year', value: 'lastyear', days: 0 },
];

// Format date as DD.MM.YY
function formatDate(date) {
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear().toString().slice(-2);
    return `${day}.${month}.${year}`;
}

// Check if date is today
function isToday(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
        date.getMonth() === today.getMonth() &&
        date.getFullYear() === today.getFullYear();
}

export default function DateRangePicker({ value, onChange, className = '' }) {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedRange, setSelectedRange] = useState(value || 'year');
    const [customYear, setCustomYear] = useState(new Date().getFullYear());
    const dropdownRef = useRef(null);

    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (option) => {
        setSelectedRange(option.value);
        if (onChange) {
            onChange({
                range: option.value,
                days: option.days,
                year: option.value === 'lastyear' ? currentYear - 1 : currentYear,
            });
        }
        setIsOpen(false);
    };

    const handleYearChange = (year) => {
        setCustomYear(year);
        setSelectedRange('custom');
        if (onChange) {
            onChange({
                range: 'custom',
                year: year,
            });
        }
        setIsOpen(false);
    };

    const getDisplayText = () => {
        const now = new Date();
        const endText = isToday(now) ? 'Today' : formatDate(now);

        if (selectedRange === '7d') {
            const start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            return `${formatDate(start)}-${endText}`;
        }
        if (selectedRange === '30d') {
            const start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            return `${formatDate(start)}-${endText}`;
        }
        if (selectedRange === 'month') {
            const start = new Date(now.getFullYear(), now.getMonth(), 1);
            return `${formatDate(start)}-${endText}`;
        }
        if (selectedRange === 'year') {
            const start = new Date(currentYear, 0, 1);
            return `${formatDate(start)}-${endText}`;
        }
        if (selectedRange === 'lastyear') {
            const start = new Date(currentYear - 1, 0, 1);
            const end = new Date(currentYear - 1, 11, 31);
            return `${formatDate(start)}-${formatDate(end)}`;
        }
        if (selectedRange === 'custom') {
            const start = new Date(customYear, 0, 1);
            const end = customYear === currentYear ? now : new Date(customYear, 11, 31);
            const customEndText = isToday(end) ? 'Today' : formatDate(end);
            return `${formatDate(start)}-${customEndText}`;
        }
        return 'Select range';
    };

    return (
        <div className={`relative ${className}`} ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
            >
                <Calendar className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                <span className="text-gray-800 dark:text-gray-200 font-medium">{getDisplayText()}</span>
                <ChevronDown className={`h-4 w-4 text-gray-500 dark:text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                    <div className="p-2">
                        <p className="text-xs text-gray-500 dark:text-gray-400 px-2 mb-2 font-medium">Quick Select</p>
                        {RANGE_OPTIONS.map((option) => (
                            <button
                                key={option.value}
                                onClick={() => handleSelect(option)}
                                className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${selectedRange === option.value
                                    ? 'bg-[#1d3557] text-white'
                                    : 'text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700'
                                    }`}
                            >
                                {option.label}
                            </button>
                        ))}
                    </div>

                    <div className="border-t border-gray-200 dark:border-gray-700 p-2">
                        <p className="text-xs text-gray-500 dark:text-gray-400 px-2 mb-2 font-medium">Select Year</p>
                        <div className="flex flex-wrap gap-2 px-2">
                            {years.map((year) => (
                                <button
                                    key={year}
                                    onClick={() => handleYearChange(year)}
                                    className={`px-3 py-1 text-sm rounded-lg transition-colors ${customYear === year && selectedRange === 'custom'
                                        ? 'bg-[#1d3557] text-white'
                                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
                                        }`}
                                >
                                    {year}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
