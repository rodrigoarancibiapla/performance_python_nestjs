import { Resolver, Query, Mutation, Args } from '@nestjs/graphql';
import { ClienteModel } from './cliente.model';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Cliente } from './cliente.entity';
import { Factura } from '../facturas/factura.entity';
import { Cache } from 'cache-manager';
import { Inject } from '@nestjs/common';
import { CACHE_MANAGER } from '@nestjs/cache-manager';

@Resolver(() => ClienteModel)
export class ClientesResolver {
  constructor(
    @InjectRepository(Cliente) private clienteRepo: Repository<Cliente>,
    @InjectRepository(Factura) private facturaRepo: Repository<Factura>,
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
  ) {}

  @Query(() => [ClienteModel])
  async allClientes() {
    const cacheKey = 'allClientes';
    const cachedClientes = await this.cacheManager.get<Cliente[]>(cacheKey);

    if (cachedClientes) {
    
      // Convertir fecha de string a Date
      return cachedClientes.map(cliente => ({
        ...cliente,
        facturas: cliente.facturas?.map(factura => ({
          ...factura,
          fecha: new Date(factura.fecha), // 🔹 Conversión de fecha
        })),
      }));
    }

    const clientes = await this.clienteRepo.find({ relations: ['facturas'] });

    let clientesConTotales;
    clientesConTotales = clientes.map(cliente => ({
      ...cliente,
      totalFacturas: cliente.facturas.reduce((sum, f) => sum + parseFloat(f.total.toString()), 0),
    }));
    
    if (!cachedClientes) {
      await this.cacheManager.set(cacheKey, clientesConTotales, 900000); // Caché por 15 minutos
    }

    return clientesConTotales;
  }

  @Mutation(() => ClienteModel)
  async crearCliente(
    @Args('nombre') nombre: string,
    @Args('email') email: string,
  ) {
    const cliente = this.clienteRepo.create({ nombre, email });
    return await this.clienteRepo.save(cliente);
  }
}
