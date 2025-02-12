import { Resolver, Query, Mutation, Args, Int } from '@nestjs/graphql';
import { Factura } from './factura.model';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Factura as FacturaEntity } from './factura.entity';
import { Cliente } from '../clientes/cliente.entity';

@Resolver(() => Factura)
export class FacturasResolver {
  constructor(
    @InjectRepository(FacturaEntity) private facturaRepo: Repository<FacturaEntity>,
    @InjectRepository(Cliente) private clienteRepo: Repository<Cliente>,
  ) {}

  @Query(() => [Factura])
  async allFacturas() {
    return await this.facturaRepo.find({ relations: ['cliente'] });
  }

  @Mutation(() => Factura)
  async crearFactura(
    @Args('clienteId', { type: () => Int }) clienteId: number,
    @Args('total', { type: () => String }) total: string,
  ) {
    const cliente = await this.clienteRepo.findOne({ where: { id: clienteId } });
    if (!cliente) throw new Error('Cliente no encontrado');

    const factura = this.facturaRepo.create({ cliente, total: parseFloat(total) });
    return await this.facturaRepo.save(factura);
  }
}
