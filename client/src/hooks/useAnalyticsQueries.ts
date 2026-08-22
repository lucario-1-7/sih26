import { useQuery } from "@tanstack/react-query";

import { getChallengeAnalytics, getIndustryAnalytics, getMLAnalytics, getModelInfo, getProjectAnalytics } from "@/lib/api/analytics";

export const useChallengeAnalytics = () => useQuery({ queryKey: ["analytics", "challenges"], queryFn: getChallengeAnalytics });
export const useProjectAnalytics = () => useQuery({ queryKey: ["analytics", "projects"], queryFn: getProjectAnalytics });
export const useIndustryAnalytics = () => useQuery({ queryKey: ["analytics", "industry"], queryFn: getIndustryAnalytics });
export const useMLAnalytics = () => useQuery({ queryKey: ["analytics", "ml"], queryFn: getMLAnalytics });
export const useModelInfo = () => useQuery({ queryKey: ["analytics", "model-info"], queryFn: getModelInfo });
