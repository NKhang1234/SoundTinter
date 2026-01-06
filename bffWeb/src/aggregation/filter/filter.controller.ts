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
   * POST /filters/test/request
   */
  @Post('test/request')
  @Roles('Admin')
  @UseGuards(SessionGuard, RolesGuard)
  @HttpCode(HttpStatus.OK)
  async requestFilter(
    @Query('songName') songName: string,
    @Query('imageID') imageID: string,
    @SessionDataDecorator() sessionData: SessionData,
  ) {
    return this.filterService.requestFilter(
      songName,
      imageID,
      sessionData,
    );
  }

  /**
   * POST /filters/test/apply
   */
  @Post('test/apply')
  @Roles('Admin')
  @UseGuards(SessionGuard, RolesGuard)
  @HttpCode(HttpStatus.OK)
  async applyFilter(
    @Query('songName') songName: string,
    @Query('imageID') imageID: string,
  ) {
    return this.filterService.applyFilter(
      songName,
      imageID,
    );
  }
}
