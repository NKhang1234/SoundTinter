export class SessionItemDTO {
  sessionToken: string;
}

export class UserSessionsResponseDTO {
  userId: string;
  activeSessions: number;
  sessions: SessionItemDTO[];
}
