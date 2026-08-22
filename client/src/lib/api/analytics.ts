import { apiFetch } from "@/lib/api/client";
import type { ChallengeAnalytics, IndustryAnalytics, MLAnalytics, ModelInfo, ProjectAnalytics } from "@/types/api";

/** All Superadmin only. */
export const getChallengeAnalytics = () => apiFetch<ChallengeAnalytics>("/analytics/challenges");
export const getProjectAnalytics = () => apiFetch<ProjectAnalytics>("/analytics/projects");
export const getIndustryAnalytics = () => apiFetch<IndustryAnalytics>("/analytics/industry");
export const getMLAnalytics = () => apiFetch<MLAnalytics>("/analytics/ml");
export const getModelInfo = () => apiFetch<ModelInfo>("/analytics/model-info");
