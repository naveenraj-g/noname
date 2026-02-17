import axios from "axios";
import { TAuthClientToken } from "../models/keycloak/keycloak";

export async function getKeycloakAdminClientToken(
  apiEndpoint: string,
  clientId: string,
  clientSecret: string
): Promise<TAuthClientToken> {
  const tokenRes = await axios.post<TAuthClientToken>(
    apiEndpoint,
    new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      grant_type: "client_credentials",
    }),
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    }
  );

  return tokenRes.data;
}
