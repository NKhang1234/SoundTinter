import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { FilterController } from './filter.controller';
import { FilterService } from './filter.service';

@Module({
  imports: [HttpModule],
  controllers: [FilterController],
  providers: [FilterService],
})
export class FilterModule {}
