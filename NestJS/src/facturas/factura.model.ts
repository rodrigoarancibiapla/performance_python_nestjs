import { ObjectType, Field, Int, Float, GraphQLISODateTime } from '@nestjs/graphql';
import { ClienteModel } from '../clientes/cliente.model';

@ObjectType()
export class Factura {
  @Field(() => Int)
  id: number;

  @Field(() => Float)
  total: number;

  @Field(() => GraphQLISODateTime)
  fecha: Date;

  @Field(() => ClienteModel)
  cliente: ClienteModel;
}
