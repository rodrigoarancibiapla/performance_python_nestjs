import { ObjectType, Field, Int, Float } from '@nestjs/graphql';
import { Factura } from '../facturas/factura.model';

@ObjectType()
export class ClienteModel {
  @Field(() => Int)
  id: number;

  @Field()
  nombre: string;

  @Field()
  email: string;

  @Field(() => [Factura], { nullable: true })
  facturas?: Factura[];

  @Field(() => Float, { nullable: true })
  totalFacturas?: number;
}
