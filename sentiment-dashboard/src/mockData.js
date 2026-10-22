// Mock Data Service for Sentiment Analysis Prototype

export const mockPlatforms = ['Amazon', 'Flipkart', 'Myntra', 'Meesho'];

export const getMockAnalysis = (query) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        query: query,
        platforms: {
          Amazon: {
            totalReviews: 12450,
            averageRating: 4.2,
            sentiment: { positive: 65, neutral: 20, negative: 15 },
            recentReviews: [
              { id: 1, text: "Great product, works exactly as described.", sentiment: "positive", score: 0.92 },
              { id: 2, text: "It's okay, but the shipping was late.", sentiment: "neutral", score: 0.55 },
              { id: 3, text: "Broke after two days of use. Terrible.", sentiment: "negative", score: 0.12 },
            ]
          },
          Flipkart: {
            totalReviews: 8300,
            averageRating: 3.9,
            sentiment: { positive: 50, neutral: 25, negative: 25 },
            recentReviews: [
              { id: 4, text: "Value for money.", sentiment: "positive", score: 0.85 },
              { id: 5, text: "Packaging was damaged.", sentiment: "negative", score: 0.3 },
            ]
          },
          Myntra: {
            totalReviews: 15200,
            averageRating: 4.5,
            sentiment: { positive: 75, neutral: 15, negative: 10 },
            recentReviews: [
              { id: 6, text: "Perfect fit and amazing material!", sentiment: "positive", score: 0.98 },
              { id: 7, text: "Color is slightly different than picture.", sentiment: "neutral", score: 0.6 },
            ]
          },
          Meesho: {
            totalReviews: 450,
            averageRating: 3.2,
            sentiment: { positive: 35, neutral: 30, negative: 35 },
            recentReviews: [
              { id: 8, text: "Cheap quality.", sentiment: "negative", score: 0.18 },
              { id: 9, text: "Good for the price.", sentiment: "neutral", score: 0.5 },
            ]
          }
        },
        overall: {
          totalAnalyzed: 36400,
          dominantSentiment: "Positive",
          platformWinner: "Myntra"
        }
      });
    }, 1200); // Simulate network latency
  });
};
