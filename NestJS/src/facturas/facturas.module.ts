import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { FacturasResolver } from './facturas.resolver';
import { Factura } from './factura.entity';
import { Cliente } from '../clientes/cliente.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Factura, Cliente])],
  providers: [FacturasResolver],
})
export class FacturasModule {}
