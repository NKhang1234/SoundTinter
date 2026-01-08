// src/filter/filter.service.ts
import { Injectable, BadRequestException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { SessionData } from '../../auth/interfaces/token.interface';

@Injectable()
export class FilterService {
  constructor(private readonly httpService: HttpService) {}

  async requestFilter(
    songName: string,
    imageName: string,
    sessionData: SessionData,
  ) {
    if (!songName || !imageName) {
      throw new BadRequestException('songName and imageName are required');
    }

    const filterServiceUrl =
      process.env.FILTER_SERVICE_URL + '/request_filter';

    const response = await firstValueFrom(
      this.httpService.post(
        filterServiceUrl,
        null, // no body, only query params
        {
          params: {
            songName,
            imageName,
          },
          headers: {
            'X-User-Id': sessionData.userId,
          },
          timeout: 10_000, // mapping + filter can take time
        },
      ),
    );

    return response.data;
  }

  async getResult(
    songName: string, 
    imageName: string,
    sessionData: SessionData,
  ) {
    if (!songName || !imageName) {
      throw new BadRequestException('songName and imageName are required');
    }

    const filterServiceUrl =
      process.env.FILTER_SERVICE_URL + '/get_result';

    const response = await firstValueFrom(
      this.httpService.get(
        filterServiceUrl,
        {
          params: {
            songName,
            imageName,
          },
          headers: {
            'X-User-Id': sessionData.userId,
          },
          timeout: 10_000, // filter can take time
        },
      ),
    );
    return response.data;
  }
}
