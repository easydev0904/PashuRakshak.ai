// react-hook-form leaves untouched optional text/date inputs as "" rather
// than undefined. Pydantic's Optional[...] fields reject "" for
// non-string types (dates, numbers), so strip empty strings before
// sending any form payload to the API.
export function stripEmptyStrings<T extends Record<string, unknown>>(values: T): Partial<T> {
  const result: Partial<T> = {};
  for (const [key, value] of Object.entries(values)) {
    if (value !== "") {
      result[key as keyof T] = value as T[keyof T];
    }
  }
  return result;
}
