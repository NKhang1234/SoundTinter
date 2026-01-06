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
    imageID: string,
    sessionData: SessionData,
  ) {
    if (!songName || !imageID) {
      throw new BadRequestException('songName and imageID are required');
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
            imageID,
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

  async applyFilter(songName: string, imageID: string) {
    if (!songName || !imageID) {
      throw new BadRequestException('songName and imageID are required');
    }

    const filterServiceUrl =
      process.env.FILTER_SERVICE_URL + '/apply_filter';

    const response = await firstValueFrom(
      this.httpService.post(
        filterServiceUrl,
        null, // no body, only query params
        {
          params: {
            songName,
            imageID,
          },
          timeout: 10_000, // filter can take time
        },
      ),
    );
    return response.data;
}
}
