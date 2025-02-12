import { Module } from '@nestjs/common';
import { GraphQLModule } from '@nestjs/graphql';
import { ApolloDriver, ApolloDriverConfig } from '@nestjs/apollo';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Cliente } from './clientes/cliente.entity';
import { Factura } from './facturas/factura.entity';
import { ClientesModule } from './clientes/clientes.module';
import { FacturasModule } from './facturas/facturas.module';
import { CacheModule } from '@nestjs/cache-manager';

import * as redisStore from 'cache-manager-redis-store';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'myuser',
      password: 'mypassword',
      database: 'mydatabase',
      entities: [Cliente, Factura],
      synchronize: true,
    }),
    GraphQLModule.forRoot<ApolloDriverConfig>({
      driver: ApolloDriver,
      autoSchemaFile: 'schema.gql',
      playground: true,  // Habilita GraphQL Playground
      introspection: true,  // Permite introspección del esquema
    }),
    ClientesModule,
    FacturasModule,
    CacheModule.register({
      store: redisStore,
      host: '127.0.0.1',
      port: 6379,
      db:3,
      ttl: 65000
    }),
  ],
})
export class AppModule {}
