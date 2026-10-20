import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type AnalysisDefinition } from "../../lib/api";

export const analysisKeys = {
	all: ["analyses"] as const,
	detail: (id: string) => ["analyses", id] as const,
};

export function useAnalyses() {
	return useQuery({
		queryKey: analysisKeys.all,
		queryFn: api.listAnalyses,
		retry: false,
	});
}

export function useAnalysis(id: string | undefined) {
	return useQuery({
		queryKey: analysisKeys.detail(id ?? ""),
		queryFn: () => api.getAnalysis(id!),
		enabled: Boolean(id),
		retry: false,
	});
}

export function useUpdateAnalysis() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ id, definition }: { id: string; definition: AnalysisDefinition }) =>
			api.updateAnalysis(id, definition),
		onSuccess: async (saved) => {
			queryClient.setQueryData(analysisKeys.detail(saved.id), saved);
			await queryClient.invalidateQueries({ queryKey: analysisKeys.all });
		},
	});
}

export function useCreateAnalysis() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (definition: AnalysisDefinition) => api.createAnalysis(definition),
		onSuccess: async (saved) => {
			queryClient.setQueryData(analysisKeys.detail(saved.id), saved);
			await queryClient.invalidateQueries({ queryKey: analysisKeys.all });
		},
	});
}

export function useExecuteAnalysis() {
	return useMutation({
		mutationFn: (definition: AnalysisDefinition) => api.executeAnalysis(definition),
	});
}