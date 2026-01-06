import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { UploadController } from './upload.controller';
import { UploadService } from './upload.service';

@Module({
  imports: [HttpModule],
  controllers: [UploadController],
  providers: [UploadService],
})
export class UploadModule {}
