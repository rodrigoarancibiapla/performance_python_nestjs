import { Entity, PrimaryGeneratedColumn, Column, OneToMany } from 'typeorm';
import { Factura } from '../facturas/factura.entity';

@Entity()
export class Cliente {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  nombre: string;

  @Column()
  email: string;

  @OneToMany(() => Factura, (factura) => factura.cliente)
  facturas: Factura[];
}

