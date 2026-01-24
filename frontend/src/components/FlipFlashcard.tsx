import React, { useState } from 'react';

interface FlipFlashcardProps {
  flashcard: {
    front_text: string;
    back_text: string;
    category: string;
    difficulty: string;
    pronunciation?: string;
  };
}

const FlipFlashcard: React.FC<FlipFlashcardProps> = ({ flashcard }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div className="flashcard-container perspective-1000 w-full h-80 mb-6">
      <div 
        className={`flashcard relative w-full h-full transform-style-preserve-3d transition-transform duration-600 cursor-pointer ${isFlipped ? 'rotate-y-180' : ''}`}
        onClick={handleFlip}
      >
        {/* Front of card */}
        <div className="flashcard-face absolute w-full h-full backface-hidden bg-gradient-to-br from-pink-50 to-fuchsia-50 border-2 border-pink-200 rounded-2xl p-8 flex flex-col justify-center">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">Question:</h3>
          <p className="text-xl text-gray-900 leading-relaxed text-center">
            {flashcard.front_text}
          </p>
          <div className="mt-4 text-center text-sm text-gray-500">
            Click to reveal answer
          </div>
        </div>

        {/* Back of card */}
        <div className="flashcard-face absolute w-full h-full backface-hidden bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-8 flex flex-col justify-center rotate-y-180">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">Answer:</h3>
          <p className="text-xl text-gray-900 leading-relaxed text-center mb-4">
            {flashcard.back_text}
          </p>
          {flashcard.pronunciation && (
            <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg text-center">
              <strong>Pronunciation:</strong> {flashcard.pronunciation}
            </div>
          )}
          <div className="mt-4 text-center text-sm text-gray-500">
            Click to see question again
          </div>
        </div>
      </div>
    </div>
  );
};

export default FlipFlashcard;
