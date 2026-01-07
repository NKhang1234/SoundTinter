// src/app.module.ts
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AuthModule } from './auth/auth.module';
import { AggregationModule } from './aggregation/aggregation.module';
import { RedisModule } from './redis/redis.module';

@Module({
  imports: [
    // Configuration
    ConfigModule.forRoot({
      isGlobal: true,
      cache: true,
    }),
    // Application Modules
    RedisModule,
    AuthModule,
    AggregationModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}