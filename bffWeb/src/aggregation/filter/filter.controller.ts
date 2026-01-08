// src/filter/filter.controller.ts
import { Controller, HttpCode, HttpStatus, Post, Query, Session, UseGuards } from '@nestjs/common';
import { FilterService } from './filter.service';
import { SessionDataDecorator } from '../../auth/decorators/session-token.decorator';
import { SessionData } from '../../auth/interfaces/token.interface';
import { SessionGuard } from 'src/auth/guards/session.guard';
import { Roles } from 'src/auth/decorators/roles.decorator';
import { RolesGuard } from 'src/auth/guards/roles.guard';

@Controller('filters')
export class FilterController {
  constructor(private readonly filterService: FilterService) {}

  /**
   * POST /filters/request_filter
   */
  @Post('request_filter')
  @Roles('Admin', 'User')
  @UseGuards(SessionGuard, RolesGuard)
  @HttpCode(HttpStatus.OK)
  async requestFilter(
    @Query('songName') songName: string,
    @Query('imageName') imageName: string,
    @SessionDataDecorator() sessionData: SessionData,
  ) {
    return this.filterService.requestFilter(
      songName,
      imageName,
      sessionData,
    );
  }

  /**
   * POST /filters/result
   */
  @Post('result')
  @Roles('Admin', 'User')
  @UseGuards(SessionGuard, RolesGuard)
  @HttpCode(HttpStatus.OK)
  async applyFilter(
    @Query('songName') songName: string,
    @Query('imageName') imageName: string,
    @SessionDataDecorator() sessionData: SessionData,
  ) {
    return this.filterService.getResult(
      songName,
      imageName,
      sessionData,
    );
  }
}
