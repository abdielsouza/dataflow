import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, type UpdateUserRequest } from "../../lib/api";

export const currentUserKey = ["users", "me"] as const;

export function useCurrentUser(enabled = true) {
  return useQuery({
    queryKey: currentUserKey,
    queryFn: api.getCurrentUser,
    enabled,
    retry: false,
  });
}

export function useUpdateCurrentUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateUserRequest) => api.updateCurrentUser(data),
    onSuccess: (user) => {
      queryClient.setQueryData(currentUserKey, user);
    },
  });
}

export function useDeleteCurrentUser() {
  return useMutation({
    mutationFn: api.deleteCurrentUser,
  });
}
