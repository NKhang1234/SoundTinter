// src/auth/guards/session.guard.ts
import { 
  Injectable, 
  CanActivate, 
  ExecutionContext, 
  UnauthorizedException,
  Logger,
} from '@nestjs/common';
import { AuthService } from '../auth.service';

@Injectable()
export class SessionGuard implements CanActivate {
  private readonly logger = new Logger(SessionGuard.name);

  constructor(private authService: AuthService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const sessionToken = request.cookies?.session_token;

    if (!sessionToken) {
      this.logger.warn('No session token found in request');
      throw new UnauthorizedException('No session token found');
    }

    try {
      const sessionData = await this.authService.validateSession(sessionToken);
      
      // Attach session data to request for use in controllers
      request.sessionData = sessionData;
      return true;
    } catch (error) {
      this.logger.error('Session validation failed:', error.message);
      throw new UnauthorizedException('Invalid or expired session');
    }
  }
}