import { useState } from 'react';

const FeedbackWidget = () => {
    const [rating, setRating] = useState(0);
    const [feedback, setFeedback] = useState('');
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = () => {
        // TODO: Integrate with backend analytics API
        setSubmitted(true);
    };

    return (
        <div className="feedback-widget">
            <h4>Rate your experience</h4>
            {[1, 2, 3, 4, 5].map(star => (
                <button key={star} onClick={() => setRating(star)}>{star}★</button>
            ))}
            <textarea
                placeholder="Additional feedback"
                value={feedback}
                onChange={e => setFeedback(e.target.value)}
            />
            <button onClick={handleSubmit}>Submit</button>
            {submitted && <div>Thank you for your feedback!</div>}
        </div>
    );
};

export default FeedbackWidget;
