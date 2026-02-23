export interface Candidate {
  id: number;
  container_selector: string;
  example_items: string[];
  count: number;
}

export interface Field {
  name: string;
  selector: string;
  type: "text" | "number" | "link" | "image";
  example?: string;
  attribute?: string;
}

export interface ConfigData {
  container_selector: string;
  fields: Field[];
  pagination?: {
    type: "next_button" | "scroll" | "url_pattern";
    selector?: string;
    url_template?: string;
  };
}

export interface ParserConfig {
  id: number;
  domain: string;
  url_pattern?: string;
  config: ConfigData;
  created_at: string;
  updated_at?: string;
  user_id?: number;
}

export interface TaskResponse {
  task_id: string;
}

export interface TaskStatus {
  task_id: string;
  status: "PENDING" | "SUCCESS" | "FAILURE";
  session_id?: string;
  error?: string;
}

export interface ScrapeStatus {
  task_id: string;
  status: "PENDING" | "PROCESSING" | "SUCCESS" | "FAILURE";
  pages_processed?: number;
  items_count?: number;
  error?: string;
}

export interface ScrapeResult {
  task_id: string;
  data: Record<string, any>[];
  total_items: number;
}