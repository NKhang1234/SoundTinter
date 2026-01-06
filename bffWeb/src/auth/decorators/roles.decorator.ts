// src/auth/decorators/roles.decorator.ts
import { SetMetadata } from '@nestjs/common';

export const ROLES_KEY = 'roles';

/**
 * Decorator to specify required roles for a route
 * Use with RolesGuard
 * 
 * @example
 * @Get('admin')
 * @UseGuards(SessionGuard, RolesGuard)
 * @Roles('admin', 'superuser')
 * getAdminData() {
 *   return { message: 'Admin only' };
 * }
 */
export const Roles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles);

/**
 * Decorator to make an endpoint public (skip authentication)
 * 
 * @example
 * @Get('public')
 * @Public()
 * getPublicData() {
 *   return { message: 'Public data' };
 * }
 */
export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);