// src/redis/redis.service.ts
import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from '@nestjs/common';
import { createClient, RedisClientType } from 'redis';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class RedisService implements OnModuleInit, OnModuleDestroy {
  private client: RedisClientType;
  private readonly logger = new Logger(RedisService.name);
  private isConnected = false;

  constructor(private configService: ConfigService) {}

  async onModuleInit() {
    await this.connect();
  }

  private async connect() {
    try {
      const redisUrl = this.configService.get('REDIS_URL', 'redis://redis:6379');
      
      this.client = createClient({
        url: redisUrl,
        socket: {
          reconnectStrategy: (retries) => {
            if (retries > 10) {
              this.logger.error('Redis max reconnection attempts reached');
              return new Error('Max reconnection attempts reached');
            }
            const delay = Math.min(retries * 100, 3000);
            this.logger.warn(`Redis reconnecting... attempt ${retries}, delay ${delay}ms`);
            return delay;
          },
        },
      });

      // Event handlers
      this.client.on('error', (err) => {
        this.logger.error('Redis Client Error:', err);
        this.isConnected = false;
      });

      this.client.on('connect', () => {
        this.logger.log('Redis client connecting...');
      });

      this.client.on('ready', () => {
        this.logger.log('Redis client ready');
        this.isConnected = true;
      });

      this.client.on('reconnecting', () => {
        this.logger.warn('Redis client reconnecting...');
        this.isConnected = false;
      });

      this.client.on('end', () => {
        this.logger.warn('Redis client connection ended');
        this.isConnected = false;
      });

      await this.client.connect();
      this.logger.log('Redis connected successfully');
    } catch (error) {
      this.logger.error('Failed to connect to Redis:', error);
      throw error;
    }
  }

  /**
   * Set a key-value pair with optional TTL
   * @param key Redis key
   * @param value Value to store (will be stringified if object)
   * @param ttl Time to live in seconds (optional)
   */
  async set(key: string, value: string | object, keepTTL: boolean, ttl?: number): Promise<void> {
    try {
      const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
      
      if (ttl && ttl > 0) {
        await this.client.set(key, stringValue, {EX: ttl});
        this.logger.debug(`Set key ${key} with TTL ${ttl}s`);
      } else {
        await this.client.set(key, stringValue, {KEEPTTL: keepTTL});
        this.logger.debug(`Set key ${key}`);
      }
    } catch (error) {
      this.logger.error(`Error setting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get value by key
   * @param key Redis key
   * @returns Value as string or null if not found
   */
  async get(key: string): Promise<string | null> {
    try {
      const value = await this.client.get(key);
      this.logger.debug(`Get key ${key}: ${value ? 'found' : 'not found'}`);
      return value;
    } catch (error) {
      this.logger.error(`Error getting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get value and parse as JSON
   * @param key Redis key
   * @returns Parsed object or null
   */
  async getJson<T = any>(key: string): Promise<T | null> {
    try {
      const value = await this.get(key);
      if (!value) return null;
      return JSON.parse(value) as T;
    } catch (error) {
      this.logger.error(`Error parsing JSON for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Delete a key
   * @param key Redis key
   * @returns Number of keys deleted (0 or 1)
   */
  
  async del(key: string): Promise<number> {
    try {
      const result = await this.client.del(key);
      this.logger.debug(`Deleted key ${key}: ${result}`);
      return result;
    } catch (error) {
      this.logger.error(`Error deleting key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Delete multiple keys
   * @param keys Array of Redis keys
   * @returns Number of keys deleted
   */
  async delMany(keys: string[]): Promise<number> {
    try {
      if (keys.length === 0) return 0;
      const result = await this.client.del(keys);
      this.logger.debug(`Deleted ${result} keys`);
      return result;
    } catch (error) {
      this.logger.error('Error deleting multiple keys:', error);
      throw error;
    }
  }

  /**
   * Check if a key exists
   * @param key Redis key
   * @returns True if key exists
   */
  async exists(key: string): Promise<boolean> {
    try {
      const result = await this.client.exists(key);
      return result === 1;
    } catch (error) {
      this.logger.error(`Error checking existence of key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Set expiration time for a key
   * @param key Redis key
   * @param seconds TTL in seconds
   * @returns True if expiration was set
   */
  async expire(key: string, seconds: number): Promise<boolean> {
    try {
      const result = await this.client.expire(key, seconds);
      this.logger.debug(`Set expiration for key ${key}: ${seconds}s`);
      return result === 1;
    } catch (error) {
      this.logger.error(`Error setting expiration for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get remaining TTL for a key
   * @param key Redis key
   * @returns TTL in seconds, -1 if no expiration, -2 if key doesn't exist
   */
  async ttl(key: string): Promise<number> {
    try {
      return await this.client.ttl(key);
    } catch (error) {
      this.logger.error(`Error getting TTL for key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get all keys matching a pattern
   * @param pattern Redis key pattern (e.g., "session:*")
   * @returns Array of matching keys
   * It may ruin performance when it is executed against large databases
   */
  async keys(pattern: string): Promise<string[]> {
    try {
      const keys = await this.client.keys(pattern);
      this.logger.debug(`Found ${keys.length} keys matching pattern ${pattern}`);
      return keys;
    } catch (error) {
      this.logger.error(`Error getting keys with pattern ${pattern}:`, error);
      throw error;
    }
  }

  /**
   * Increment a counter
   * @param key Redis key
   * @param increment Amount to increment by (default: 1)
   * @returns New value after increment
   */
  async incr(key: string, increment: number = 1): Promise<number> {
    try {
      const result = increment === 1 
        ? await this.client.incr(key)
        : await this.client.incrBy(key, increment);
      return result;
    } catch (error) {
      this.logger.error(`Error incrementing key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Decrement a counter
   * @param key Redis key
   * @param decrement Amount to decrement by (default: 1)
   * @returns New value after decrement
   */
  async decr(key: string, decrement: number = 1): Promise<number> {
    try {
      const result = decrement === 1
        ? await this.client.decr(key)
        : await this.client.decrBy(key, decrement);
      return result;
    } catch (error) {
      this.logger.error(`Error decrementing key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Set if not exists (atomic operation)
   * @param key Redis key
   * @param value Value to set
   * @param ttl Optional TTL in seconds
   * @returns True if key was set, false if key already existed
   * Deprecated: use set with NX option instead
   */
  async setNX(key: string, value: string | object, ttl?: number): Promise<boolean> {
    try {
      const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
      
      if (ttl && ttl > 0) {
        const result = await this.client.set(key, stringValue, {
          NX: true,
          EX: ttl,
        });
        return result === 'OK';
      } else {
        const result = await this.client.setNX(key, stringValue);
        return result === 1;
      }
    } catch (error) {
      this.logger.error(`Error setting NX key ${key}:`, error);
      throw error;
    }
  }

  /**
   * Add value to a set
   * @param key Redis key
   * @param members Values to add
   * @returns Number of elements added
   */
  async sadd(key: string, ...members: string[]): Promise<number> {
    try {
      const result = await this.client.sAdd(key, members);
      return result;
    } catch (error) {
      this.logger.error(`Error adding to set ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get all members of a set
   * @param key Redis key
   * @returns Array of set members
   */
  async smembers(key: string): Promise<string[]> {
    try {
      return await this.client.sMembers(key);
    } catch (error) {
      this.logger.error(`Error getting set members for ${key}:`, error);
      throw error;
    }
  }

  /**
   * Remove member from a set
   * @param key Redis key
   * @param members Members to remove
   * @returns Number of members removed
   */
  async srem(key: string, ...members: string[]): Promise<number> {
    try {
      const result = await this.client.sRem(key, members);
      return result;
    } catch (error) {
      this.logger.error(`Error removing from set ${key}:`, error);
      throw error;
    }
  }

  /**
   * Push value to a list (left)
   * @param key Redis key
   * @param values Values to push
   * @returns Length of list after push
   */
  async lpush(key: string, ...values: string[]): Promise<number> {
    try {
      return await this.client.lPush(key, values);
    } catch (error) {
      this.logger.error(`Error pushing to list ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get range of list elements
   * @param key Redis key
   * @param start Start index
   * @param stop Stop index (-1 for end)
   * @returns Array of list elements
   */
  async lrange(key: string, start: number, stop: number): Promise<string[]> {
    try {
      return await this.client.lRange(key, start, stop);
    } catch (error) {
      this.logger.error(`Error getting list range for ${key}:`, error);
      throw error;
    }
  }

  /**
   * Set hash field
   * @param key Redis key
   * @param field Field name
   * @param value Field value
   */
  async hset(key: string, field: string, value: string | object): Promise<number> {
    try {
      const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
      return await this.client.hSet(key, field, stringValue);
    } catch (error) {
      this.logger.error(`Error setting hash field ${field} in ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get hash field
   * @param key Redis key
   * @param field Field name
   * @returns Field value or undefined
   */
  async hget(key: string, field: string): Promise<string | null> {
    try {
      return await this.client.hGet(key, field);
    } catch (error) {
      this.logger.error(`Error getting hash field ${field} from ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get all hash fields and values
   * @param key Redis key
   * @returns Object with all fields and values
   */
  async hgetall(key: string): Promise<Record<string, string>> {
    try {
      return await this.client.hGetAll(key);
    } catch (error) {
      this.logger.error(`Error getting all hash fields from ${key}:`, error);
      throw error;
    }
  }

  /**
   * Delete hash field
   * @param key Redis key
   * @param fields Field names to delete
   * @returns Number of fields deleted
   */
  async hdel(key: string, ...fields: string[]): Promise<number> {
    try {
      return await this.client.hDel(key, fields);
    } catch (error) {
      this.logger.error(`Error deleting hash fields from ${key}:`, error);
      throw error;
    }
  }

  /**
   * Flush all data (use with caution!)
   */
  async flushAll(): Promise<void> {
    try {
      await this.client.flushAll();
      this.logger.warn('Flushed all Redis data');
    } catch (error) {
      this.logger.error('Error flushing Redis:', error);
      throw error;
    }
  }

  /**
   * Check if Redis is connected
   */
  isReady(): boolean {
    return this.isConnected && this.client?.isReady;
  }

  /**
   * Get Redis client for advanced operations
   */
  getClient(): RedisClientType {
    return this.client;
  }

  async onModuleDestroy() {
    try {
      if (this.client) {
        await this.client.quit();
        this.logger.log('Redis connection closed');
      }
    } catch (error) {
      this.logger.error('Error closing Redis connection:', error);
    }
  }
}