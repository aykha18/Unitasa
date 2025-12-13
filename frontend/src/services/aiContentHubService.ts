import { apiClient } from './api';

export interface Hashtag {
  id: string;
  text: string;
  category: string;
  popularity_score: number;
  usage_count: number;
}

export interface HashtagGenerationResponse {
  success: boolean;
  topic: string;
  platform: string;
  hashtags: Hashtag[];
  total_count: number;
  generated_at: string;
  source: string;
}

export interface ImageSuggestion {
  id: string;
  url: string;
  thumbnail_url: string;
  title: string;
  description: string;
  width: number;
  height: number;
  format: string;
  source: string;
  tags: string[];
  generated_at: string;
  download_url: string;
}

export interface ImageGenerationResponse {
  success: boolean;
  query: string;
  images: ImageSuggestion[];
  total_count: number;
  generated_at: string;
  source: string;
  note?: string;
}

export interface ChatAssistantResponse {
  success: boolean;
  response: {
    id: string;
    message: string;
    timestamp: string;
    source: string;
    confidence: number;
    suggestions: string[];
  };
  conversation_context?: string;
  processing_time_ms: number;
}

export interface HashtagGenerationRequest {
  topic: string;
  platform?: string;
  count?: number;
}

export interface ImageGenerationRequest {
  query: string;
  count?: number;
}

export interface ChatAssistantRequest {
  message: string;
  context?: string;
}

class AIContentHubService {
  private readonly baseUrl = '/api/v1/social/content';

  async generateHashtags(request: HashtagGenerationRequest): Promise<HashtagGenerationResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/generate-hashtags`, request);
      return response.data;
    } catch (error) {
      console.error('Failed to generate hashtags:', error);
      throw error;
    }
  }

  async generateImages(request: ImageGenerationRequest): Promise<ImageGenerationResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/generate-images`, request);
      return response.data;
    } catch (error) {
      console.error('Failed to generate images:', error);
      throw error;
    }
  }

  async chatWithAssistant(request: ChatAssistantRequest): Promise<ChatAssistantResponse> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/chat-assistant`, request);
      return response.data;
    } catch (error) {
      console.error('Failed to chat with assistant:', error);
      throw error;
    }
  }
}

export const aiContentHubService = new AIContentHubService();
export default aiContentHubService;