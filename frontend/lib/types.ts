export interface Destination {
  id: string;
  name: string;
  country: string;
  region: string;
  description: string;
  image_url?: string | null;
  lat?: number | null;
  lng?: number | null;
  tags: string[];
}

/** Shared shape for HiddenGem / Experience / Event, per CONTRACT.md. */
export interface AiEntity {
  id: string;
  destination_id: string;
  name: string;
  description: string;
  category: string;
  ai_generated: boolean;
}

export interface HeritageStory {
  destination_id?: string;
  title?: string;
  narrative: string;
  ai_generated: boolean;
}

export interface RecommendationRequest {
  interests: string[];
  budget?: string;
  duration_days?: number;
  region?: string;
  travel_style?: string;
}

export interface RankedItem {
  name: string;
  reason: string;
}

export interface RecommendationResponse {
  summary: string;
  attractions: RankedItem[];
  hidden_gems: RankedItem[];
}

export interface ChatRequest {
  message: string;
  thread_id?: string;
}

export interface ChatResponse {
  reply: string;
  thread_id: string;
}

export interface SavedItem {
  id: number;
  entity_type?: string;
  entity_id?: number;
  name: string;
  description?: string;
  category?: string;
  destination_id?: number;
  ai_generated?: boolean;
  saved_at?: string;
}
