import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createUser, listUsers, updateUser } from "@/lib/api/users";
import type { Role, UserCreateInput, UserUpdateInput } from "@/types/api";

export function useUsersList(params: { role?: Role; cursor?: string } = {}) {
  return useQuery({ queryKey: ["users", params], queryFn: () => listUsers(params) });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UserCreateInput) => createUser(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useUpdateUser(userId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UserUpdateInput) => updateUser(userId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });
}
