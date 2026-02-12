/**
 * Skeleton Loader Component
 * Use for loading states in cards, lists, and data displays
 */



export function Skeleton({ className = '', variant = 'text', width, height }) {
    const baseClasses = 'animate-pulse bg-gray-200 dark:bg-gray-700 rounded';

    const variantClasses = {
        text: 'h-4 rounded',
        title: 'h-6 rounded',
        avatar: 'h-10 w-10 rounded-full',
        card: 'h-32 rounded-lg',
        button: 'h-10 w-24 rounded-lg',
        image: 'h-40 rounded-lg',
        circle: 'rounded-full',
    };

    const style = {};
    if (width) style.width = typeof width === 'number' ? `${width}px` : width;
    if (height) style.height = typeof height === 'number' ? `${height}px` : height;

    return (
        <div
            className={`${baseClasses} ${variantClasses[variant] || ''} ${className}`}
            style={style}
        />
    );
}

export function SkeletonCard() {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-4">
            <div className="flex items-center space-x-3">
                <Skeleton variant="avatar" />
                <div className="flex-1 space-y-2">
                    <Skeleton variant="title" width="60%" />
                    <Skeleton variant="text" width="40%" />
                </div>
            </div>
            <div className="space-y-2">
                <Skeleton variant="text" width="100%" />
                <Skeleton variant="text" width="80%" />
                <Skeleton variant="text" width="90%" />
            </div>
        </div>
    );
}

export function SkeletonTable({ rows = 5, columns = 4 }) {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            {/* Header */}
            <div className="grid gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700"
                style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
                {Array.from({ length: columns }).map((_, i) => (
                    <Skeleton key={i} variant="text" width="70%" />
                ))}
            </div>
            {/* Rows */}
            {Array.from({ length: rows }).map((_, rowIndex) => (
                <div
                    key={rowIndex}
                    className="grid gap-4 p-4 border-b border-gray-100 dark:border-gray-700 last:border-b-0"
                    style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
                >
                    {Array.from({ length: columns }).map((_, colIndex) => (
                        <Skeleton key={colIndex} variant="text" width={`${60 + Math.random() * 30}%`} />
                    ))}
                </div>
            ))}
        </div>
    );
}

export function SkeletonStats({ count = 4 }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-center justify-between">
                        <div className="space-y-2 flex-1">
                            <Skeleton variant="text" width="50%" />
                            <Skeleton variant="title" width="70%" height={28} />
                        </div>
                        <Skeleton variant="circle" width={48} height={48} />
                    </div>
                    <Skeleton variant="text" width="40%" className="mt-4" />
                </div>
            ))}
        </div>
    );
}

export function SkeletonList({ items = 5 }) {
    return (
        <div className="space-y-3">
            {Array.from({ length: items }).map((_, i) => (
                <div key={i} className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <Skeleton variant="avatar" />
                    <div className="flex-1 space-y-2">
                        <Skeleton variant="text" width="40%" />
                        <Skeleton variant="text" width="60%" />
                    </div>
                    <Skeleton variant="button" />
                </div>
            ))}
        </div>
    );
}

export function SkeletonChart() {
    // Pre-defined heights for skeleton bars
    const barHeights = [45, 72, 58, 85, 32, 67, 91, 54, 78, 42, 65, 88];

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
                <Skeleton variant="title" width="30%" />
                <Skeleton variant="button" width={100} />
            </div>
            <div className="flex items-end justify-between h-48 space-x-2">
                {barHeights.map((height, i) => (
                    <div
                        key={i}
                        className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-t animate-pulse"
                        style={{ height: `${height}%` }}
                    />
                ))}
            </div>
        </div>
    );
}
