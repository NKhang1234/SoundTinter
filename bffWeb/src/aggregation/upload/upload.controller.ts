import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
  HttpCode,
  UseGuards,
  Session,
  HttpStatus,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { UploadService } from './upload.service';
import { SessionDataDecorator } from 'src/auth/decorators/session-token.decorator';
import { SessionData } from 'src/auth/interfaces/token.interface';
import { SessionGuard } from 'src/auth/guards/session.guard';
import { RolesGuard } from 'src/auth/guards/roles.guard';
import { Roles } from 'src/auth/decorators/roles.decorator';

@Controller('upload')
export class UploadController {
  constructor(private readonly uploadService: UploadService) {}

  /**
   * POST /upload/images
   */
  @Post('images')
  @Roles('User', 'Admin')
  @UseGuards(SessionGuard, RolesGuard)
  @HttpCode(HttpStatus.OK)
  @UseInterceptors(FileInterceptor('file'))
  async uploadImage(
    @UploadedFile() file: Express.Multer.File,
    @SessionDataDecorator() sessionData: SessionData,
  ) {
    return this.uploadService.forwardUploadImage(file, sessionData);
  }

  @Post('songs')
  @Roles('User', 'Admin')
  @UseGuards(SessionGuard, RolesGuard)
  @HttpCode(HttpStatus.OK)
  @UseInterceptors(FileInterceptor('file'))
  async uploadSong(
    @UploadedFile() file: Express.Multer.File,
    @SessionDataDecorator() sessionData: SessionData,
  ) {
    return this.uploadService.forwardUploadSong(file, sessionData);
  }

  
}
