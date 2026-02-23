import axios from "axios";
import {
  Candidate,
  Field,
  ParserConfig,
  TaskResponse,
  TaskStatus,
  ScrapeStatus,
  ScrapeResult,
  ConfigData,
} from "../types";

const API_BASE = "http://localhost:8000/api"; // измените при необходимости

const api = axios.create({
  baseURL: API_BASE,
});

// Анализ
export const startAnalysis = (url: string, useJs: boolean = true) =>
  api.post<TaskResponse>("/analyze/start", { url, use_js: useJs });

export const getAnalysisStatus = (taskId: string) =>
  api.get<TaskStatus>(`/analyze/status/${taskId}`);

export const getCandidates = (sessionId: string) =>
  api.get<{ session_id: string; candidates: Candidate[] }>(
    `/analyze/candidates/${sessionId}`
  );

export const selectContainer = (sessionId: string, containerSelector: string) =>
  api.post("/analyze/select-container", {
    session_id: sessionId,
    container_selector: containerSelector,
  });

export const getFields = (sessionId: string) =>
  api.get<{ session_id: string; fields: Field[] }>(
    `/analyze/fields/${sessionId}`
  );

// Конфигурации
export const createConfig = (config: {
  domain: string;
  url_pattern?: string;
  config: ConfigData;
}) => api.post<ParserConfig>("/configs/", config);

export const getConfigs = () => api.get<ParserConfig[]>("/configs/");

export const getConfigsByDomain = (domain: string) =>
  api.get<ParserConfig[]>(`/configs/by-domain?domain=${domain}`);

export const getConfig = (id: number) =>
  api.get<ParserConfig>(`/configs/${id}`);

// Сбор данных
export const startScrape = (configId: number, startUrl: string, maxPages?: number) =>
  api.post<{ task_id: string }>("/scrape/start", {
    config_id: configId,
    start_url: startUrl,
    max_pages: maxPages,
  });

export const getScrapeStatus = (taskId: string) =>
  api.get<ScrapeStatus>(`/scrape/status/${taskId}`);

export const getScrapeResult = (taskId: string) =>
  api.get<ScrapeResult>(`/scrape/result/${taskId}`);

export const exportResults = (taskId: string, format: "json" | "excel") =>
  `${API_BASE}/scrape/export/${taskId}?format=${format}`; // возвращаем URL для скачивания