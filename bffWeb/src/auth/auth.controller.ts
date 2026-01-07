// src/auth/auth.controller.ts
import { 
  Controller, 
  Post, 
  Param,
  Get, 
  Body, 
  Res, 
  Req, 
  Query, 
  UnauthorizedException,
  UseGuards, 
  HttpCode,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { Response } from 'express';
import { AuthService } from './auth.service';
import { ConfigService } from '@nestjs/config';
import { SessionGuard } from './guards/session.guard';
import { SessionTokenDecorator, SessionDataDecorator } from './decorators/session-token.decorator';
import { 
  SessionData,
  UserInfo,
} from './interfaces/token.interface';
import { LogoutResponseDTO } from './dto/logout-response.dto';
import { RefreshResponseDTO } from './dto/refresh-response.dto';
import { UserSessionsResponseDTO } from './dto/all-sessions-response.dto';
import { RoleCheckingDTO } from './dto/role-checking.dto';

@Controller('auth')
export class AuthController {
  private readonly logger = new Logger(AuthController.name);
  private readonly keycloakUrl: string;
  private readonly realm: string;
  private readonly clientId: string;
  constructor(
    private authService: AuthService,
    private configService: ConfigService
  ) {
    this.keycloakUrl = this.configService.get('KEYCLOAK_URL', 'http://keycloak:8080');
    this.realm = this.configService.get('KEYCLOAK_REALM', 'master');
    this.clientId = this.configService.get('KEYCLOAK_CLIENT_ID', 'web-bff');
  }

  /**
   * Login endpoint
   * POST /auth/login
   */
  @Get('login')
  async login(@Res() res: Response): Promise<void> {
    const authUrl =
      `${this.keycloakUrl}/realms/${this.realm}` +
      `/protocol/openid-connect/auth` +
      `?client_id=${this.clientId}` +
      `&response_type=code` +
      `&scope=openid profile email` +
      `&redirect_uri=${this.configService.get('WEB_CALLBACK_URL', 'http://web.localhost/auth/callback')}`;

    return res.redirect(authUrl);
  }

  @Get('callback')
  async callback(
    @Query('code') code: string,
    @Res({ passthrough: true }) res: Response,
  ): Promise<void> {
    if (!code) {
      throw new UnauthorizedException('Missing authorization code');
    }

    const sessionToken = await this.authService.exchangeCodeForToken(code);

    res.cookie('session_token', sessionToken, {
      httpOnly: true,
      secure: this.configService.get('NODE_ENV') === 'production',
      sameSite: this.configService.get('NODE_ENV') === 'production' ? 'strict' : 'lax',
      maxAge: 24 * 60 * 60 * 1000,
      path: '/',
    });

    return res.redirect(`${this.configService.get('FRONTEND_BASE_URL', 'http://localhost:3000')}/login/success`);
  }

  /**
   * Logout endpoint
   * POST /auth/logout
   */
  @Post('logout')
  @UseGuards(SessionGuard)
  @HttpCode(HttpStatus.OK)
  async logout(
    @SessionTokenDecorator() sessionToken: string,
    @SessionDataDecorator() sessionData: SessionData,
    @Res({ passthrough: true }) res: Response,
  ): Promise<LogoutResponseDTO> {
    this.logger.log(`Logout request for session: ${sessionToken}`);

    if (sessionToken) {
      await this.authService.logout(sessionToken, sessionData);
    }

    res.clearCookie('session_token', {
      httpOnly: true,
      secure: this.configService.get('NODE_ENV') === 'production',
      sameSite: this.configService.get('NODE_ENV') === 'production' ? 'strict' : 'lax',
      path: '/',
    });

    return {
      message: 'Logout successful',
      success: true,
    };
  }

  /**
   * Logout all sessions for current user
   * POST /auth/logout-all
   */
  @Post('logout-all')
  @UseGuards(SessionGuard)
  @HttpCode(HttpStatus.OK)
  async logoutAll(
    @SessionTokenDecorator() sessionToken: string,
    @SessionDataDecorator() sessionData: SessionData,
    @Res({ passthrough: true }) res: Response,
  ): Promise<LogoutResponseDTO> {
    this.logger.log(`Logout all sessions for user: ${sessionData.userId}`);

    const count = await this.authService.logoutAllSessions(sessionToken, sessionData);

    res.clearCookie('session_token', {
      httpOnly: true,
      secure: this.configService.get('NODE_ENV') === 'production',
      sameSite: this.configService.get('NODE_ENV') === 'production' ? 'strict' : 'lax',
      path: '/',
    });

    return {
      message: `Logged out ${count} session(s) successfully`,
      success: true,
    };
  }

  /**
   * Refresh token endpoint
   * POST /auth/refresh
   */
  @Post('refresh')
  @UseGuards(SessionGuard)
  @HttpCode(HttpStatus.OK)
  async refresh(
    @SessionTokenDecorator() sessionToken: string,
    @SessionDataDecorator() sessionData: SessionData,
    @Res({ passthrough: true }) res: Response,
  ): Promise<RefreshResponseDTO> {
    this.logger.log(`Token refresh request for session: ${sessionToken}`);

    const newSessionToken = await this.authService.refreshToken(sessionToken, sessionData);

    res.cookie('session_token', newSessionToken, {
      httpOnly: true,
      secure: this.configService.get('NODE_ENV') === 'production',
      sameSite: this.configService.get('NODE_ENV') === 'production' ? 'strict' : 'lax',
      maxAge: 24 * 60 * 60 * 1000,
      path: '/',
    });

    return {
      message: 'Token refreshed successfully',
      expiresIn: 24 * 60 * 60,
    };
  }

  /**
   * Get current user info
   * GET /auth/me
   */
  @Get('me')
  @UseGuards(SessionGuard)
  @HttpCode(HttpStatus.OK)
  async getMe(
    @SessionDataDecorator() sessionData: SessionData,
  ): Promise<UserInfo> {
    return {
      userId: sessionData.userId,
      username: sessionData.username,
      name: sessionData.name,
      given_name: sessionData.given_name,
      family_name: sessionData.family_name,
      email: sessionData.email,
      emailVerified: sessionData.emailVerified,
      roles: sessionData.roles,
    };
  }


  /**
   * Get all active sessions for current user
   * GET /auth/sessions
   */
  @Get('sessions')
  @UseGuards(SessionGuard)
  @HttpCode(HttpStatus.OK)
  async getSessions(
    @SessionDataDecorator() sessionData: SessionData,
  ): Promise<UserSessionsResponseDTO> {
    const sessions = await this.authService.getUserSessions(sessionData);
    
    return{
      userId: sessionData.userId,
      activeSessions: sessions.length,
      sessions: sessions.map(token => ({
        sessionToken: token.substring(0, 8) + '...',
        // In production, you might want to store and return more metadata
      })),
    };
  }

  /**
   * Check if user has specific role
   * GET /auth/check-role/:role
   */
  @Get('check-role/:role')
  @UseGuards(SessionGuard)
  @HttpCode(HttpStatus.OK)
  async checkRole(
    @SessionDataDecorator() sessionData: SessionData,
    @Param('role') role: string
  ): Promise<RoleCheckingDTO> {
    const hasRole = await this.authService.hasRole(sessionData, role);
    
    return {
      role,
      hasRole,
    };
  }
}