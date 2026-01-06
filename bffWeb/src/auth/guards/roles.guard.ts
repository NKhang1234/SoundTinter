// src/auth/guards/roles.guard.ts
import { 
  Injectable, 
  CanActivate, 
  ExecutionContext, 
  ForbiddenException,
  Logger,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { ROLES_KEY } from '../decorators/roles.decorator';

/**
 * Guard to check if user has required roles
 * Use with @Roles() decorator and @UseGuards(SessionGuard, RolesGuard)
 */
@Injectable()
export class RolesGuard implements CanActivate {
  private readonly logger = new Logger(RolesGuard.name);

  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // Get required roles from decorator metadata
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles || requiredRoles.length === 0) {
      // No roles required, allow access
      return true;
    }

    const request = context.switchToHttp().getRequest();
    const userRoles = request.sessionData?.roles || [];

    // Check if user has any of the required roles
    const hasRole = requiredRoles.some(role => userRoles.includes(role));

    if (!hasRole) {
      this.logger.warn(
        `User with roles [${userRoles.join(', ')}] attempted to access resource requiring [${requiredRoles.join(', ')}]`,
      );
      throw new ForbiddenException(
        'You do not have permission to access this resource',
      );
    }

    return true;
  }
}