import { createParamDecorator, ExecutionContext } from '@nestjs/common';

/**
 * Parameter decorator that extracts the session token from the request cookies. 
 * @example
 * @Get('profile')
 * getProfile(@SessionToken() token: string) {
 *   // token contains the session_token cookie value
 * }
 */
export const SessionTokenDecorator = createParamDecorator(
  (_: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();

    // cookie-parser must be enabled
    return request.cookies?.['session_token'];
  },
);


/**
 * Decorator that injects session data from the HTTP request into a controller method parameter.
 * @example
 * @Post('profile')
 * updateProfile(@SessionDataDecorator() sessionData: SessionData) {
 *   // sessionData contains the user's session information
 * }
 */
export const SessionDataDecorator = createParamDecorator(
  (_: unknown, ctx: ExecutionContext) => {
    const request = ctx.switchToHttp().getRequest();
    return request.sessionData;
  },
);
