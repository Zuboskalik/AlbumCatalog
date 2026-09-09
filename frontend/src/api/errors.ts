import axios from "axios";

/** DRF validation error body: {"<field>": ["msg", ...]} or {"non_field_errors": [...]}. */
export type ApiErrorBody = Record<string, string[] | string>;

/** Extracts a human-readable message from any error thrown by the api/* modules. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "Не удалось связаться с сервером. Проверьте, что backend запущен.";
    }
    const data = error.response.data as ApiErrorBody | undefined;
    if (data && typeof data === "object") {
      const parts: string[] = [];
      for (const [field, messages] of Object.entries(data)) {
        const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
        parts.push(field === "non_field_errors" || field === "detail" ? text : `${field}: ${text}`);
      }
      if (parts.length > 0) return parts.join(" ");
    }
    return `Ошибка сервера (${error.response.status}).`;
  }
  if (error instanceof Error) return error.message;
  return "Неизвестная ошибка.";
}

/** Field-level errors keyed the same way DRF returns them, for inline form display. */
export function getFieldErrors(error: unknown): Record<string, string> {
  if (!axios.isAxiosError(error) || !error.response) return {};
  const data = error.response.data as ApiErrorBody | undefined;
  if (!data || typeof data !== "object") return {};
  const result: Record<string, string> = {};
  for (const [field, messages] of Object.entries(data)) {
    result[field] = Array.isArray(messages) ? messages.join(" ") : String(messages);
  }
  return result;
}
