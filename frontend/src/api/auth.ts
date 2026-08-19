import { apiClient } from "./client";
import type { LoginResponse, User } from "./types";

export async function register(data: {
  full_name: string;
  email: string;
  password: string;
}): Promise<User> {
  const response = await apiClient.post<User>("/auth/register", data);
  return response.data;
}

export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.set("username", email);
  formData.set("password", password);

  const response = await apiClient.post<LoginResponse>(
    "/auth/login",
    formData,
    {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }
  );
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<User>("/auth/me");
  return response.data;
}
