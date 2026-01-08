// src/auth/auth.service.ts
import { Injectable, UnauthorizedException, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import { RedisService } from '../redis/redis.service';
import { v4 as uuidv4 } from 'uuid';
import { firstValueFrom } from 'rxjs';
import { 
  SessionData, 
  DecodedToken,
  UserInfo 
} from './interfaces/token.interface';
import { KeycloakTokenResponseDTO } from './dto/keycloak-token-respones.dto';
import * as jwt from 'jsonwebtoken';

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);
  private keycloakUrl: string;
  private realm: string;
  private clientId: string;
  private clientSecret: string;

  constructor(
    private configService: ConfigService,
    private httpService: HttpService,
    private redisService: RedisService,
  ) {
    this.keycloakUrl = this.configService.get('KEYCLOAK_URL', 'http://keycloak:8080');
    this.realm = this.configService.get('KEYCLOAK_REALM', 'master');
    this.clientId = this.configService.get('KEYCLOAK_CLIENT_ID', 'web-bff');
    this.clientSecret = this.configService.get('KEYCLOAK_CLIENT_SECRET', '');

    if (!this.clientSecret) {
      this.logger.warn('KEYCLOAK_CLIENT_SECRET is not set!');
    }
  }

  // ####################################################################################################################
  // public methods
  // ####################################################################################################################
  
  /**
   * Validate session and return session data
   */
  public async validateSession(sessionToken: string): Promise<SessionData> {
    if (!sessionToken) {
      throw new UnauthorizedException('No session token provided');
    }

    const sessionData = await this.redisService.getJson<SessionData>(`session:${sessionToken}`);
    
    if (!sessionData) {
      this.logger.warn(`Invalid or expired session: ${sessionToken}`);
      throw new UnauthorizedException('Invalid or expired session');
    }

    // Check if token is expired
    if (Date.now()  >= sessionData.expiresAt) {
      if (Date.now() >= sessionData.refreshExpiresAt) {
        await this.redisService.del(`session:${sessionToken}`);
        await this.redisService.srem(`user:${sessionData.userId}:sessions`, sessionToken);
        this.logger.warn(`Session refresh token expired: ${sessionToken}`);
        throw new UnauthorizedException('Session expired. Please login again.');
      }
      // Access token expired but refresh token still valid
      await this.refreshToken(sessionToken, sessionData)
    }

    // Update last accessed time
    sessionData.lastAccessedAt = Date.now();
    await this.redisService.set(`session:${sessionToken}`, sessionData, true);
    
    return sessionData;
  }
  
  /**
   * Exchange authorization code with Keycloak
   */
  public async exchangeCodeForToken(code: string): Promise<string> {
    try {
      const tokenUrl = `${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/token`;
      
      const params = new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: this.clientId,
        client_secret: this.clientSecret,
        code,
        redirect_uri: this.configService.get('WEB_CALLBACK_URL', 'http://web.localhost/auth/callback'),
      });

      this.logger.log(`Attempting login with authorization code: ${code}`);

      const response = await firstValueFrom(
        this.httpService.post<KeycloakTokenResponseDTO>(tokenUrl, params.toString(), {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }),
      );

      const tokenData = response.data;
      
      // Decode JWT to get user info
      const decoded = this.decodeToken(tokenData.access_token);
      const userInfo = this.extractUserInfo(decoded);

      // Generate session token
      const sessionToken = uuidv4();
      
      // Store session data in Redis
      const sessionData: SessionData = {
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        expiresAt: Date.now() + tokenData.expires_in * 1000,
        refreshExpiresAt: Date.now() + tokenData.refresh_expires_in * 1000,
        userId: userInfo.userId,
        username: userInfo.username,
        name: userInfo.name,
        given_name: userInfo.given_name,
        family_name: userInfo.family_name,
        email: userInfo.email,
        emailVerified: userInfo.emailVerified,
        roles: userInfo.roles,
        sessionState: tokenData.session_state,
        scope: tokenData.scope,
        createdAt: Date.now(),
        lastAccessedAt: Date.now(),
      };

      // Store with TTL matching token expiry
      await this.redisService.set(
        `session:${sessionToken}`,
        sessionData,
        false,
        tokenData.refresh_expires_in,
      );

      // Also store user's active sessions for multi-device support
      await this.redisService.sadd(`user:${userInfo.userId}:sessions`, sessionToken);
      await this.redisService.expire(`user:${userInfo.userId}:sessions`, tokenData.expires_in);

      this.logger.log(`User ${userInfo.username} logged in successfully. Session: ${sessionToken}`);

      return sessionToken;
    } catch (error) {
      this.logger.error('Login error:', error.response?.data || error.message);
      throw new UnauthorizedException('Authentication failed. Please try again.');
    }
  }

  /**
   * Logout user and invalidate session
   */
  public async logout(sessionToken: string, sessionData: SessionData): Promise<void> {
    try {
      // Revoke token in Keycloak (optional but recommended)
      try {
        const revokeUrl = `${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/revoke`;
        const params = new URLSearchParams({
          client_id: this.clientId,
          client_secret: this.clientSecret,
          token: sessionData.refreshToken,
          token_type_hint: 'refresh_token',
        });

        await firstValueFrom(
          this.httpService.post(revokeUrl, params.toString(), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          }),
        );

        this.logger.log(`Token revoked in Keycloak for session: ${sessionToken}`);
      } catch (error) {
        this.logger.error('Token revocation error:', error.message);
        // Continue with logout even if revocation fails
      }

      // Remove session from user's active sessions
      await this.redisService.srem(`user:${sessionData.userId}:sessions`, sessionToken);

      // Delete session from Redis
      await this.redisService.del(`session:${sessionToken}`);

      this.logger.log(`User ${sessionData.userId} logged out. Session: ${sessionToken}`);
    } catch (error) {
      if (error instanceof UnauthorizedException) {
        // Session already invalid, just log and continue
        this.logger.warn('Logout called on invalid session');
      } else {
        throw error;
      }
    }
  }

  /**
   * Logout all sessions for a user
   */
  public async logoutAllSessions(sessionToken: string, sessionData: SessionData): Promise<number> {
    const userId = sessionData.userId;
    const sessionTokens = await this.redisService.smembers(`user:${userId}:sessions`);
    
    if (sessionTokens.length === 0) {
      return 0;
    }

    // Delete all sessions
    const sessionKeys = sessionTokens.map(token => `session:${token}`);
    await this.redisService.delMany(sessionKeys);
    await this.redisService.del(`user:${userId}:sessions`);

    this.logger.log(`Logged out all ${sessionTokens.length} sessions for user: ${userId}`);
    return sessionTokens.length;
  }

  /**
   * Refresh access token using refresh token
   */
  public async refreshToken(sessionToken: string, sessionData: SessionData): Promise<string> {
    
    try {
      const tokenUrl = `${this.keycloakUrl}/realms/${this.realm}/protocol/openid-connect/token`;
      
      const params = new URLSearchParams({
        grant_type: 'refresh_token',
        client_id: this.clientId,
        client_secret: this.clientSecret,
        refresh_token: sessionData.refreshToken,
      });

      this.logger.log(`Refreshing token for session: ${sessionToken}`);

      const response = await firstValueFrom(
        this.httpService.post<KeycloakTokenResponseDTO>(tokenUrl, params.toString(), {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }),
      );

      const tokenData = response.data;
      const decoded = this.decodeToken(tokenData.access_token);
      const userInfo = this.extractUserInfo(decoded);
      
      // Update session data with new tokens
      const newSessionData: SessionData = {
        ...sessionData,
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        expiresAt: Date.now() + tokenData.expires_in * 1000,
        refreshExpiresAt: Date.now() + tokenData.refresh_expires_in * 1000,
        roles: userInfo.roles,
        lastAccessedAt: Date.now(),
      };

      await this.redisService.set(
        `session:${sessionToken}`,
        newSessionData,
        false,
        tokenData.refresh_expires_in,
      );

      // Also store user's active sessions for multi-device support
      await this.redisService.sadd(`user:${userInfo.userId}:sessions`, sessionToken);
      await this.redisService.expire(`user:${userInfo.userId}:sessions`, tokenData.expires_in);

      this.logger.log(`Token refreshed successfully for session: ${sessionToken}`);

      return sessionToken;
    } catch (error) {
      this.logger.error('Token refresh error:', error.response?.data || error.message);
      
      // If refresh fails, delete the session
      await this.redisService.del(`session:${sessionToken}`);
      
      throw new UnauthorizedException('Unable to refresh token. Please login again.');
    }
  }

  /**
   * Verify if user has specific role
   */
  public async hasRole(sessionData: SessionData, role: string): Promise<boolean> {
    return sessionData.roles?.includes(role) || false;
  }

  /**
   * Get all active sessions for a user
   */
  public async getUserSessions(sessionData: SessionData): Promise<string[]> {
    const userId = sessionData.userId;
    return await this.redisService.smembers(`user:${userId}:sessions`);
  }

  // ####################################################################################################################
  // private methods
  // ####################################################################################################################

  /**
   * Decode JWT token without verification (Keycloak already verified it)
   */
  private decodeToken(token: string): DecodedToken {
    try {
      return jwt.decode(token) as DecodedToken;
    } catch (error) {
      this.logger.error('Error decoding token:', error);
      throw new UnauthorizedException('Invalid token format');
    }
  }

  /**
   * Extract user information from decoded token
   */
  private extractUserInfo(decoded: DecodedToken): UserInfo {
    const roles: string[] = [];

    // Extract realm roles
    if (decoded.realm_access?.roles) {
      roles.push(...decoded.realm_access.roles);
    }

    // Extract client roles
    if (decoded.resource_access) {
      Object.values(decoded.resource_access).forEach(resource => {
        if (resource.roles) {
          roles.push(...resource.roles);
        }
      });
    }

    return {
      userId: decoded.sub,
      username: decoded.preferred_username,
      name: decoded.name,
      given_name: decoded.given_name,
      family_name: decoded.family_name,
      email: decoded.email,
      emailVerified: decoded.email_verified,
      roles: [...new Set(roles)], // Remove duplicates
    };
  }
}