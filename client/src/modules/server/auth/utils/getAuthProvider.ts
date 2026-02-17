import bezsConfig from "../../../../../bezs.json";

export function getAuthProvider() {
  const mode =
    (bezsConfig?.authProvider as "betterauth" | "keycloak") || "betterauth";

  return {
    provider: mode,
    isKeycloak: mode === "keycloak",
  };
}
