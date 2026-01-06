// src/auth/interfaces/token.interface.ts

/**
 * Session data stored in Redis
 */
export interface SessionData {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  refreshExpiresAt: number;
  userId: string;
  username?: string;
  name?: string;
  given_name?: string;
  family_name?: string;
  email?: string;
  emailVerified?: boolean;
  roles?: string[];
  sessionState?: string;
  scope?: string;
  createdAt: number;
  lastAccessedAt?: number;
}

/**
 * Decoded JWT token payload from Keycloak
 */
export interface DecodedToken {
  exp: number;
  iat: number;
  auth_time?: number;
  jti: string;
  iss: string;
  aud: string | string[];
  sub: string;
  typ: string;
  azp: string;
  session_state?: string;
  acr?: string;
  'allowed-origins'?: string[];
  realm_access?: {
    roles: string[];
  };
  resource_access?: {
    [key: string]: {
      roles: string[];
    };
  };
  scope?: string;
  sid?: string;
  email_verified?: boolean;
  name?: string;
  preferred_username?: string;
  given_name?: string;
  family_name?: string;
  email?: string;
}

/**
 * User info from token
 */
export interface UserInfo {
  userId: string;
  username?: string;
  name?: string;
  given_name?: string;
  family_name?: string;
  email?: string;
  emailVerified?: boolean;
  roles?: string[];
}

/**
 * Session metadata
 */
export interface SessionMetadata {
  sessionToken: string;
  userId: string;
  createdAt: number;
  expiresAt: number;
  lastAccessedAt?: number;
  ipAddress?: string;
  userAgent?: string;
}
