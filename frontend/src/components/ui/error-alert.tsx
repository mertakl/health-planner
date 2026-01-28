interface ErrorAlertProps {
    message: string;
    onDismiss: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({message, onDismiss}) => {
    return (
        <div className="mb-6 max-w-7xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3 shadow-sm">
                <svg
                    className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
                <div className="flex-1">
                    <p className="text-red-800 font-medium">Error</p>
                    <p className="text-red-700 text-sm mt-1">{message}</p>
                </div>
                <button
                    onClick={onDismiss}
                    className="text-red-600 hover:text-red-800 transition-colors flex-shrink-0"
                    aria-label="Dismiss error"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        </div>
    );
};