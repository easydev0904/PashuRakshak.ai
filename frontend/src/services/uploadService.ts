import { apiClient } from "@/api/client";

export const uploadService = {
  uploadImage: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient
      .post<{ url: string }>("/uploads", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data.url);
  },
};
