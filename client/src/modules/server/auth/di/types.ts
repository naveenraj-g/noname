import {
  IAuthenticationService,
  IKeycloakAuthenticationService,
} from "../application/services/authenticationService.interface";

export const DI_SYMBOLS = {
  // Services
  IBetterauthAuthenticationService: Symbol.for(
    "IBetterauthAuthenticationService"
  ),
  IKeycloakAuthenticationService: Symbol.for("IKeycloakAuthenticationService"),
};

export interface DI_RETURN_TYPES {
  // Services
  IBetterauthAuthenticationService: IAuthenticationService;
  IKeycloakAuthenticationService: IKeycloakAuthenticationService;
}
