import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ClientesResolver } from './clientes.resolver';
import { Cliente } from './cliente.entity';
import { Factura } from '../facturas/factura.entity';
import { CacheModule } from '@nestjs/cache-manager'; // ✅ Importa el módulo de caché

@Module({
  imports: [
    TypeOrmModule.forFeature([Cliente, Factura]),
    CacheModule.register(), // ✅ Registra el módulo de caché aquí
  ],
  providers: [ClientesResolver],
})
export class ClientesModule {}
