import { Injectable, BadRequestException } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import * as FormData from 'form-data';
import { SessionData } from 'src/auth/interfaces/token.interface';

@Injectable()
export class UploadService {
  constructor(private readonly httpService: HttpService) {}

  async forwardUploadImage(file: Express.Multer.File, sessionData: SessionData) {
    if (!file) {
      throw new BadRequestException('file is required');
    }

    const formData = new FormData();

    // IMPORTANT: send buffer exactly as FastAPI expects
    formData.append('file', file.buffer, {
      filename: file.originalname,
      contentType: file.mimetype,
    });

    const uploadServiceUrl =
      process.env.UPLOAD_SERVICE_URL + '/upload-image';

    try {
      const response = await firstValueFrom(
        this.httpService.post(uploadServiceUrl, formData, {
          headers: {
            ...formData.getHeaders(),
            'X-User-Id': sessionData.userId,
            'X-User-Roles': sessionData.roles?.join(',') ?? '',
          },
        }),
      );

      return response.data;
    } catch (err: any) {
      // Preserve Upload Service error
      if (err.response) {
        throw err.response.data;
      }
      throw err;
    }
  }

  async forwardUploadSong(file: Express.Multer.File, sessionData: SessionData) {
    if (!file) {
      throw new BadRequestException('file is required');
    }

    const formData = new FormData();

    formData.append('file', file.buffer, {
      filename: file.originalname,
      contentType: file.mimetype,
    });

    const uploadServiceUrl =
      process.env.UPLOAD_SERVICE_URL + '/upload-song';

    const response = await firstValueFrom(
      this.httpService.post(uploadServiceUrl, formData, {
        headers: {
          ...formData.getHeaders(),
          'X-User-Id': sessionData.userId,
          'X-User-Roles': sessionData.roles?.join(',') ?? '',
        },
        maxBodyLength: Infinity,
        maxContentLength: Infinity,
      }),
    );

    return response.data;
  }
}
