import { Module } from '@nestjs/common';
import { UploadModule } from './upload/upload.module';
import { FilterModule } from './filter/filter.module';



@Module({
  imports: [FilterModule , UploadModule],
  
})
export class AggregationModule {}
